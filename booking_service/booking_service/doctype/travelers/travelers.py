# Copyright (c) 2025, fatma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Travelers(Document):
    def before_insert(self):
        try:
            if not self.first_name or not self.last_name:
                frappe.throw("Please, fill in the empty fields")

            self.full_name = f'{self.first_name} {self.last_name}'

            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": self.full_name,
                "mobile_no": self.phone,
                "email_id": self.email_address,
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "All Territories"
            })
            customer.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(message=str(e), title="Traveler Insert Error")
            frappe.throw(f"An error occurred: {e}")

