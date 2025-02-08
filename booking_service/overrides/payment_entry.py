from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import fmt_money
from frappe import _
from frappe.model.document import Document

def update_outstanding(doc, method):
    booking_services_name = doc.custom_booking_service

    if booking_services_name:
        total_amount = float(doc.custom_total_amount or 0.0)
        paid_amount = float(doc.paid_amount or 0.0)
        payment_type = doc.payment_type

        updated_outstanding = total_amount - paid_amount

        if payment_type == "Receive":
            
            frappe.db.set_value("Booking Services", booking_services_name, "outstanding", updated_outstanding)

            # تحديث حالة الحجز
            new_status = "Paid" if updated_outstanding == 0 else "Partially Paid" if updated_outstanding < total_amount else "Unpaid"
            frappe.db.set_value("Booking Services", booking_services_name, "status", new_status)

            frappe.db.commit()

            # إعادة تحميل المستند بعد التحديث
            booking_service_doc = frappe.get_doc("Booking Services", booking_services_name)
            booking_service_doc.reload()






def validate_amounts(doc, method):
    total_amount = float(doc.custom_total_amount or 0.0)
    paid_amount = float(doc.paid_amount or 0.0)
    payment_type = doc.payment_type

    if total_amount <= 0:
        frappe.throw(_("Total amount must be greater than zero."))

    if paid_amount < 0:
        frappe.throw(_("Paid amount cannot be negative."))

    if payment_type == "Receive":
        if paid_amount > total_amount:
            frappe.throw(_(f"Paid Amount Can Not Be Greater Than Total Amount"))
    else:
         if paid_amount!= total_amount:
            frappe.throw(_(f"Paid Amount Can Not Be Less Than Total Amount"))