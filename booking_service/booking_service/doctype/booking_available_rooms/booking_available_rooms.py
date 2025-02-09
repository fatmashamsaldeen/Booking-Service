# Copyright (c) 2025, fatma and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

class BookingAvailableRooms(Document):
	@frappe.whitelist()
	def get_filtered_rooms(hotel=None, room_type=None):
		filters = {
			'status': 'Available'  # إظهار الغرف المتاحة فقط
		}

		if hotel:
			filters['hotel'] = hotel  # تصفية حسب الفندق إذا تم تحديده
		if room_type:
			filters['room_type'] = room_type  # تصفية حسب نوع الغرفة إذا تم تحديده

		# استرجاع الغرف التي تتوافق مع الفلاتر
		rooms = frappe.get_all('Rooms', filters=filters, fields=["name", "room", "room_type", "room_view"])

		return rooms

# @frappe.whitelist()  # هذه ضرورية لتتمكن JS من استدعاء الدالة
# def update_booking_service(booking_service_name, hotel_name):
#     if booking_service_name and hotel_name:
#         frappe.db.set_value("Booking Services", booking_service_name, "hotel", hotel_name)
#         frappe.db.commit()
#         return {"status": "success"}
#     return {"status": "error", "message": "Invalid parameters"}