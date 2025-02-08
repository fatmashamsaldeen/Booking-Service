# Copyright (c) 2025, fatma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BookingServices(Document):
    def on_update(self):
        if self.total_booking_amount == self.outstanding:
            self.status = "Unpaid"
            self.db_update() 

    def on_submit(self):
        if self.outstanding == -1.00 :
            self.outstanding = self.total_booking_amount
            self.db_update() 

        if self.travelers:
            for traveler in self.travelers:
                ticket = frappe.get_doc({
                    "doctype": "Ticket Booking",
                    "traveler": traveler.traveler,  # تأكد من أن الحقل متطابق مع اسم الحقل في Ticket Booking
                    "flight": self.flight,  # تعيين نفس الرحلة لجميع المسافرين
                    "booking_reference": self.name ,
                    "one_way":self.one_way
                })
                ticket.insert(ignore_permissions=True)  # إدخال المستند الجديد
                
            frappe.db.commit()  # 
