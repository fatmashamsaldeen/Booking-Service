// Copyright (c) 2025, fatma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transfer Booking", {
	// refresh(frm) {

	// },
    after_save: function(frm) {
        if (frm.doc.related_booking_service) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Booking Services",
                    name: frm.doc.related_booking_service
                },
                callback: function(response) {
                    if (response.message) {
                        let doc = response.message;
    
                        if (!doc.transfers_booking) {
                            doc.transfers_booking = [];
                        }
    
                        // 🔹 إضافة صف جديد للتشايلد تيبل
                        let newRow = {
                            transfer_booking: frm.doc.name,
                            total_amount: parseFloat(frm.doc.total_amount) || 0 // تأكد من أنها رقم
                        };
                        doc.transfers_booking.push(newRow);
    
                        // 🔹 حساب المجموع الصحيح لجميع قيم `total_amount`
                        let totalTransferAmount = doc.transfers_booking.reduce((sum, row) => sum + (parseFloat(row.total_amount) || 0), 0);
                        doc.transfer_booking_amount = totalTransferAmount;
    
                        // 🔹 حفظ التعديلات في `Booking Services`
                        frappe.call({
                            method: "frappe.client.save",
                            args: { doc: doc },
                            callback: function(saveResponse) {
                                if (!saveResponse.exc) {
                                    frm.save();
                                    setTimeout(() => {
                                        frappe.set_route("Form", "Booking Services", frm.doc.related_booking_service);
                                        setTimeout(() => {
                                            frappe.model.with_doc("Booking Services", frm.doc.related_booking_service, function() {
                                                cur_frm.refresh();  // 🔄 تحديث الصفحة بعد الانتقال
                                            });
                                        }, 1500); // ⏳ انتظر 1.5 ثانية قبل التحديث
                                    }, 1000);
                                }
                            }
                        });
                    }
                }
            });
        }
    }
    
    
});
