# # Copyright (c) 2025, fatma and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class BookingServices(Document):
#     # def on_update(self):
#     #     if self.total_booking_amount == self.outstanding:
#     #         self.status = "Unpaid"
#     #         self.db_update() 

#     # def on_submit(self):
#     #     if self.outstanding == -1.00 :
#     #         self.outstanding = self.total_booking_amount
#     #         self.db_update() 

#         if self.travelers:
#             for traveler in self.travelers:
#                 ticket = frappe.get_doc({
#                     "doctype": "Ticket Booking",
#                     "traveler": traveler.traveler,  # تأكد من أن الحقل متطابق مع اسم الحقل في Ticket Booking
#                     "flight": self.flight,  # تعيين نفس الرحلة لجميع المسافرين
#                     "booking_reference": self.name ,
#                     "one_way":self.one_way
#                 })
#                 ticket.insert(ignore_permissions=True)  # إدخال المستند الجديد
                
#             frappe.db.commit()  # 
#     def on_submit(self):
#     # تحويل القيم إلى float مع التعامل مع القيم الفارغة
#         ticket_amount = float(self.ticket_booking_amount or 0)
#         hotel_amount = float(self.hotel_booking_amount or 0)
#         outstanding = getattr(self, 'outstanding', None)
#         self.total_booking_amount = ticket_amount + hotel_amount

#         if outstanding is None:
#             frappe.throw("The field 'outstanding' is missing from the Booking Services document.")
#         # حساب المجموع
#         if outstanding == -1:
#             self.outstanding = self.total_booking_amount

# Copyright (c) 2025, fatma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BookingServices(Document):

    def on_submit(self):
        # تحويل القيم إلى float مع التعامل مع القيم الفارغة
        ticket_amount = float(self.ticket_booking_amount or 0)
        hotel_amount = float(self.hotel_booking_amount or 0)
        transfer_amount = float(self.transfer_booking_amount or 0)

        self.total_booking_amount = ticket_amount + hotel_amount+transfer_amount

        # التأكد من وجود حقل outstanding
        outstanding = getattr(self, 'outstanding', None)
        if outstanding is None:
            frappe.throw("The field 'outstanding' is missing from the Booking Services document.")

        # تحديث حالة outstanding
        if outstanding == -1:
            self.outstanding = self.total_booking_amount

        # إنشاء سجلات جديدة في "Ticket Booking" لكل مسافر
        if self.travelers:
            for traveler in self.travelers:
                ticket = frappe.get_doc({
                    "doctype": "Ticket Booking",
                    "traveler": traveler.traveler,  # تأكد من أن الحقل متطابق مع اسم الحقل في Ticket Booking
                    "flight": self.flight,  # تعيين نفس الرحلة لجميع المسافرين
                    "booking_reference": self.name,
                    "one_way": self.one_way
                })
                ticket.insert(ignore_permissions=True)  # إدخال المستند الجديد

        # حفظ التعديلات
        self.db_update()
        frappe.db.commit()
