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
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _

import frappe 
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
	get_dimensions,
)
import erpnext
import traceback
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
)
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from frappe.model.meta import get_meta


from erpnext.accounts.utils import  get_account_currency
from erpnext.assets.doctype.asset.depreciation import (
	depreciate_asset,
	get_disposal_account_and_cost_center,
	get_gl_entries_on_asset_disposal,
	get_gl_entries_on_asset_regain,
	reset_depreciation_schedule,
	reverse_depreciation_entry_made_after_disposal,
)

from frappe import _, qb, throw
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate

import erpnext
from erpnext.accounts.deferred_revenue import validate_service_stop_date
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
from erpnext.accounts.doctype.repost_accounting_ledger.repost_accounting_ledger import (
	validate_docs_for_deferred_accounting,
	validate_docs_for_voucher_types,
)
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	check_if_return_invoice_linked_with_payment_entry,
	get_total_in_party_account_currency,
	is_overdue,
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
	get_party_tax_withholding_details,
)
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from erpnext.accounts.party import get_due_date, get_party_account
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from erpnext.assets.doctype.asset.asset import is_cwip_accounting_enabled
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.buying.utils import check_on_hold_or_closed_status
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import (
	get_item_account_wise_additional_cost,
	update_billed_amount_based_on_po,
)
from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity
from erpnext.accounts.general_ledger import (
    make_gl_entries,
    merge_similar_entries,
)
from erpnext.accounts.party import get_party_account


from erpnext.accounts.general_ledger import (
	make_gl_entries,
	make_reverse_gl_entries,
	process_gl_map,
)
from erpnext.accounts.utils import (
	create_gain_loss_journal,
	get_account_currency,
	get_currency_precision,
	get_fiscal_years,
	validate_fiscal_year,
)
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from erpnext.accounts.utils import (
	cancel_exchange_gain_loss_journal,
	get_account_currency,
	get_balance_on,
	get_outstanding_invoices,
	get_party_types_from_account_type,
)
from erpnext.accounts.party import get_party_account

from erpnext.accounts.doctype.bank_account.bank_account import (
	get_bank_account_details,
	# get_default_company_bank_account,
	get_party_bank_account,
)
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import (
	get_party_account_based_on_invoice_discounting,
)
from erpnext.controllers.accounts_controller import AccountsController


class BookingServices(AccountsController):

    def on_submit(self):
        # frappe.log_error("Submitting and calling make_gl_entries...", "Submit Debug")
        # تحويل القيم إلى float مع التعامل مع القيم الفارغة
        ticket_amount = float(self.ticket_booking_amount or 0)
        hotel_amount = float(self.hotel_booking_amount or 0)
        transfer_amount = float(self.transfer_booking_amount or 0)

        self.total_booking_amount = ticket_amount + hotel_amount+transfer_amount
        commission_rate = float(self.commition_rate or 0)
        self.paid_amount = self.total_booking_amount + (self.total_booking_amount * commission_rate / 100)
        self.commition_amount=self.paid_amount-self.total_booking_amount
        # # التأكد من وجود حقل outstanding
        outstanding = getattr(self, 'outstanding', None)
        if outstanding is None:
            frappe.throw("The field 'outstanding' is missing from the Booking Services document.")

        # تحديث حالة outstanding
        if outstanding == -1:
            self.outstanding = self.paid_amount

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
        self.make_gl_entries()


    def validate(self):
        pass

    def make_gl_entries(self, cancel=False, from_repost=False):
        if not self.get("debit_to"):
            frappe.throw(_("Debit To account is required to book an entry"))

        gl_entries = self.get_gl_entries()

        if gl_entries:
            make_gl_entries(
                gl_entries,
                cancel=cancel,
                update_outstanding="No",
                merge_entries=False,
                from_repost=from_repost
            )

    def get_gl_entries(self):
        gl_entries = []
        self.record_initial_entry(gl_entries)
       
        return gl_entries

    def record_initial_entry(self, gl_entries):    
        remarks = self.get("remarks") or "No remarks provided"  # Ensure remarks has a value

        if self.paid_amount > 0:
            gl_entries.append(
                self.get_gl_dict({
                    "account": self.debit_to,
                    "debit": self.paid_amount,
                    "credit": 0,
                    "posting_date": frappe.utils.today(),
                    "against": self.income_account,
                    "company": self.company,
                    # "cost_center": self.cost_center,
                    "party_type": "Customer", 
                    "party": self.customer_name ,
                    "remarks": remarks  # إضافة remarks لتجنب الخطأ

                })
            )

            gl_entries.append(
                self.get_gl_dict({
                    "account": self.income_account,
                    "credit": self.paid_amount,
                    "debit": 0,
                    "company": self.company,
                    "posting_date": frappe.utils.today(),
                    "against": self.debit_to,
                    # "cost_center": self.cost_center,
                    "remarks": remarks  # إضافة remarks لتجنب الخطأ

                })
            )

    # def make_gl_entries(self, cancel=False, from_repost=False):
    #     if not self.get("debit_to"):
    #         frappe.throw(_("Debit To account is required to book an entry"))

    #     gl_entries = self.get_gl_entries()

    #     if gl_entries:
    #         make_gl_entries(
    #             gl_entries,
    #             cancel=cancel,
    #             update_outstanding="No",
    #             merge_entries=False,
    #             from_repost=from_repost
    #         )

    # def get_gl_entries(self):
    #     gl_entries = []
    #     self.record_initial_entry(gl_entries)
    #     return gl_entries

    # def record_initial_entry(self, gl_entries):
    #     total_amount = self.paid_amount  # إجمالي المبلغ المدفوع
    #     commission_amount = self.commission_amount  # العمولة
    #     net_income = total_amount - commission_amount  # صافي الدخل بعد خصم العمولة

    #     # 🟢 تسجيل القيد للحساب المدين (Debit)
    #     gl_entries.append(
    #         self.get_gl_dict({
    #             "account": self.debit_to,  # حساب العميل
    #             "debit": total_amount,
    #             "credit": 0,
    #             "posting_date": frappe.utils.today(),
    #             "against": self.income_account,
    #             "company": self.company,
    #             "party_type": "Customer", 
    #             "party": self.customer_name
    #         })
    #     )

    #     # 🟢 تسجيل القيد لحساب الدخل بعد خصم العمولة (Credit)
    #     gl_entries.append(
    #         self.get_gl_dict({
    #             "account": self.income_account,  # حساب الدخل الرئيسي
    #             "credit": net_income,
    #             "debit": 0,
    #             "posting_date": frappe.utils.today(),
    #             "against": self.debit_to,
    #             "company": self.company
    #         })
    #     )

    #     # 🟢 تسجيل قيد العمولة (Commission Account)
    #     gl_entries.append(
    #         self.get_gl_dict({
    #             "account": "Commission Account",  # حساب العمولة
    #             "credit": commission_amount,  
    #             "debit": 0,
    #             "posting_date": frappe.utils.today(),
    #             "against": self.income_account,
    #             "company": self.company
    #         })
    #     )


        # def make_gl_entries(self, cancel=False, from_repost=False):
        #     if not self.get("debit_to"):
        #         frappe.throw(_("Debit To account is required to book an entry"))

        #     gl_entries = self.get_gl_entries()

        #     if gl_entries:
        #         make_gl_entries(
        #             gl_entries,
        #             cancel=cancel,
        #             update_outstanding="No",
        #             merge_entries=False,
        #             from_repost=from_repost
        #         )

        # def get_gl_entries(self):
        #     gl_entries = []
        #     self.record_initial_entry(gl_entries)
        #     if self.paid_amount and self.paid_amount > 0 and self.is_paid:
        #         self.record_payment_entry(gl_entries)
        #     if self.commission_total and self.shipping_total:
        #         self.shipper_company_entry(gl_entries) 