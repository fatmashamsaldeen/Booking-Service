import frappe
from frappe.utils import nowdate, nowtime, get_datetime
from frappe.model.mapper import get_mapped_doc
from frappe import _
import requests
from frappe.utils import now
import json


@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    def update_item(source, target, source_parent):
        target.party_type = "Customer"
        target.party = source.customer_name
        target.party_name = source.customer_name
        target.payment_type = "Receive"
        target.received_amount = source.outstanding
        target.custom_total_amount = source.outstanding



    doc = get_mapped_doc(
        "Booking Services",  
        source_name,
        {
            "Booking Services": {
                "doctype": "Payment Entry",
                "field_map": {
                    "customer": "party",
                    "outstanding": "paid_amount",
                    
                },
                "postprocess": update_item,
            },
        },
        target_doc
    )

    return doc
@frappe.whitelist()
def fetch_and_store_flight_offers():
    # تحديد القيم المراد تخزينها
    origin_location_code = "SYD"
    destination_location_code = "BKK"
    departure_date = "2025-05-02"
    seat_count = 1  # adults = 1
    
    url = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={origin_location_code}&destinationLocationCode={destination_location_code}&departureDate={departure_date}&adults={seat_count}&nonStop=false&max=250"

    headers = {
        "Authorization": "Bearer PoaAQSnagFG7WQcWKEhAD4Ap0dHw"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        for offer in data.get("data", []):
            flight_offer = frappe.get_doc({
                "doctype": "Flight Offer",
                "type": offer.get("type"),
                "name": offer.get("id"),
                "source": offer.get("source"),
                "instant_ticketing_required": offer.get("instantTicketingRequired"),
                "last_ticketing_date": offer.get("lastTicketingDate"),
                "number_of_bookable_seats": offer.get("numberOfBookableSeats"),
                "price_currency": offer["price"].get("currency"),
                "total_price": offer["price"].get("total"),
                "offer_details": json.dumps(offer),  
                # إضافة القيم الجديدة
                "origin_location_code": origin_location_code,
                "destination_location_code": destination_location_code,
                "date": departure_date,
                "seat_count": seat_count
            })

            flight_offer.insert()
            frappe.db.commit()
    else:
        frappe.throw(f"Failed to fetch data from API: {response.status_code}") 



@frappe.whitelist()

def fetch_and_store_hotels():
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city?cityCode=PAR&radius=5&radiusUnit=KM&hotelSource=ALL"

    headers = {
        "Authorization": "Bearer UBFKPGGxB8lEX0H4KLQb4zFIT9C0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        for hotel in data.get("data", []):
            hotel_id = hotel.get("hotelId")
            existing_hotel = frappe.get_value("Hotel", {"hotelid": hotel_id}, "name")

            if existing_hotel:
                # الفندق موجود مسبقًا، قم بتحديث بياناته
                hotel_doc = frappe.get_doc("Hotel", existing_hotel)
                hotel_doc.name1 = hotel.get("name")
                hotel_doc.chaincode = hotel.get("chainCode")
                hotel_doc.iatacode = hotel.get("iataCode")
                hotel_doc.countrycode = hotel["address"].get("countryCode")
                hotel_doc.rating = hotel.get("rating")
                hotel_doc.lastupdate = hotel.get("lastUpdate")

                # تحديث قائمة المرافق
                hotel_doc.set("amenities", [])
                for amenity in hotel.get("amenities", []):
                    hotel_doc.append("amenities", {"amenity": amenity})

                hotel_doc.save()
            else:
                # الفندق غير موجود، قم بإضافته
                hotel_doc = frappe.get_doc({
                    "doctype": "Hotel",
                    "name1": hotel.get("name"),
                    "chaincode": hotel.get("chainCode"),
                    "iatacode": hotel.get("iataCode"),
                    "hotelid": hotel_id,
                    "countrycode": hotel["address"].get("countryCode"),
                    "rating": hotel.get("rating"),
                    "lastupdate": hotel.get("lastUpdate"),
                })

                for amenity in hotel.get("amenities", []):
                    hotel_doc.append("amenities", {"amenity": amenity})

                hotel_doc.insert()

        frappe.db.commit()
    else:
        frappe.throw(f"Failed to fetch data from API: {response.status_code}")
