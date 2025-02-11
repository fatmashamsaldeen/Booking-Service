frappe.ui.form.on('Booking Services', {
    ticket_booking(frm) {
        const dialog = new frappe.ui.form.MultiSelectDialog({
            doctype: "Flight Offer",  
            target: frm,
            setters: {
                date: null,
                origin_location_code: null,
                destination_location_code: null,
                number_of_bookable_seats: null,
            },
            add_filters_group: 1,

            action(selections) {
                console.log("Selected Flights:", selections);  
                
                if (selections.length > 0) {
                    frm.set_value("flight", selections[0].name);
                    frm.set_value("flight_price", selections[0].total_price); // تخزين السعر أيضًا
                }
            }
        });

        // انتظر قليلاً حتى يتم تحميل العناصر داخل الـ Dialog
        setTimeout(() => {
            let footer = dialog.dialog.$wrapper.find('.modal-footer');
            if (footer.length > 0) {
                let selectBtn = $('<button class="btn btn-primary">Select</button>');

                selectBtn.click(function () {
                    const selectedItems = dialog.get_checked_items();  // جلب العناصر المختارة
                    if (selectedItems.length > 0) {
                        let selectedFlight = selectedItems[0].name; // جلب اسم الرحلة
                        let selectedPrice = selectedItems[0].total_price; // جلب السعر

                        frm.set_value("flight", selectedFlight); // تخزين اسم الرحلة في الحقل "flight"
                        frm.set_value("flight_price", selectedPrice); // تخزين السعر في الحقل "flight_price"
                        dialog.dialog.hide();  // إغلاق النافذة
                    } else {
                        frappe.msgprint(__('Please select a flight first.'));
                    }
                });

                footer.prepend(selectBtn); // إضافة الزر في الفوتر
            }
        }, 500); // تأخير التنفيذ حتى يتم تحميل العناصر
    },
    hotel_booking(frm) {
        frm.save(); // حفظ النموذج أولاً
    
        const dialog = new frappe.ui.form.MultiSelectDialog({
            doctype: "Hotel",  
            target: frm,
            setters: {
                iatacode: null,
                countrycode: null,
            },
            add_filters_group: 1,
    
            action(selections) {
                console.log("Selected Hotels:", selections);  
    
                if (selections.length === 1) {
                    let selectedHotel = selections[0].name; // اسم الفندق المختار
                    let currentBookingService = frm.doc.name; // اسم خدمة الحجز الحالية
                    
                    // إنشاء مستند جديد مع تعيين حقل hotel و related_booking_service
                    frappe.new_doc('Booking Available Rooms', {
                        hotel: selectedHotel,
                        related_booking_service: currentBookingService // تمرير اسم البوكنق سيرفيس الحالية
                    }).then(function(doc) {
                        // حفظ مستند Booking Available Rooms بعد إنشائه
                        doc.save().then(function() {
                            // إغلاق نافذة الاختيار
                            dialog.dialog.hide();
                            frappe.show_alert({ message: __("تم إضافة الفندق بنجاح"), indicator: "green" });
                        });
                    });
                }
            }
        });
    
        // تأخير بسيط لضمان تحميل عناصر الـ Dialog
        setTimeout(() => {
            let footer = dialog.dialog.$wrapper.find('.modal-footer');
            if (footer.length > 0) {
                let selectBtn = $('<button class="btn btn-primary">Select</button>');
    
                selectBtn.click(function () {
                    const selectedItems = dialog.get_checked_items();  // جلب العناصر المختارة
                    if (selectedItems.length > 0) {
                        let selectedHotel = selectedItems[0].name; // جلب اسم الفندق المختار
                        let currentBookingService = frm.doc.name; // اسم خدمة الحجز الحالية
                        
                        // إنشاء مستند جديد مع تعيين حقل hotel و related_booking_service
                        frappe.new_doc('Booking Available Rooms', { 
                            hotel: selectedHotel,
                            related_booking_service: currentBookingService // تمرير اسم البوكنق سيرفيس الحالية
                        }).then(function(doc) {
                            // حفظ مستند Booking Available Rooms بعد إنشائه
                            doc.save().then(function() {
                                // إغلاق نافذة الاختيار
                                dialog.dialog.hide();
                                frappe.show_alert({ message: __("تم إضافة الفندق بنجاح"), indicator: "green" });
                            });
                        });
                    } else {
                        frappe.msgprint(__('Please select a hotel first.'));
                    }
                });
    
                footer.prepend(selectBtn); // إضافة الزر في الفوتر
            }
        }, 500); // تأخير تنفيذ الكود لضمان تحميل العناصر
    }
,   

transfer_booking: function(frm) {
    frm.save(); 
    frappe.model.with_doctype('Transfer Booking', function() {
        let new_doc = frappe.model.get_new_doc('Transfer Booking');

        new_doc.related_flight = frm.doc.flight;
        new_doc.related_booking_service = frm.doc.name;
        frappe.set_route('Form', 'Transfer Booking', new_doc.name);
    });
},
onload: function(frm) {
    // if (frm.doc.outstanding === -1) {
    //     frm.toggle_display('outstanding', false);
    // };
    frappe.call({
        method: "frappe.client.get_single_value",
        args: {
            doctype: "Booking Setting ", // اسم الـ Doctype الذي يحتوي على الإعدادات
            field: "commition_rate" // اسم الحقل المطلوب
        },
        callback: function(response) {
            if (response.message) {
                frm.set_value("commition_rate", response.message);
            }
        }
    });
},
        show_general_ledger: function(frm) {
            frm.add_custom_button(
                __("Ledger"),
                function () {
                    frappe.route_options = {
                        voucher_no: frm.doc.name,
                    };
                    frappe.set_route("query-report", "General Ledger");
                },
                "fa fa-table"
            );


    if (frm.doc.docstatus === 1) {
        if (!frm.custom_buttons['Payment']) {
            frm.add_custom_button(__('Payment'), function() {
                frappe.msgprint(__('Processing Payment...'));
                frappe.call({
                    method: "booking_service.api.make_payment_entry",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", r.message.doctype, r.message.name);
                        }
                    }
                });
            });
        }
    }
},

    refresh: function(frm) {
        calculate_ticket_booking_amount(frm);
        if (frm.doc.outstanding === -1) {
            frm.toggle_display('outstanding', false);
        };
        
        // if (frm.doc.docstatus === 1) {
        //     frappe.call({
        //         method: "update_outstanding",  // اسم التطبيق والوحدة المناسبة
        //         args: {
        //             docname: frm.doc.name,
        //             outstanding: frm.doc.paid_amount
        //         },
        //         callback: function(response) {
        //             if (!response.exc) {
        //                 frappe.msgprint("تم تحديث القيمة بنجاح!");
        //                 frm.reload_doc();  // إعادة تحميل المستند لعرض القيم المحدثة
        //             }
        //         }
        //     });
        // }


        // if (frm.doc.docstatus === 1) {
        //     if (!frm.custom_buttons['Payment']) {
        //         frm.add_custom_button(__('Payment'), function() {
        //             frappe.msgprint(__('Processing Payment...'));
        //             frappe.call({
        //                 method: "booking_service.api.make_payment_entry",
        //                 args: {
        //                     source_name: frm.doc.name
        //                 },
        //                 callback: function (r) {
        //                     if (r.message) {
        //                         frappe.model.sync(r.message);
        //                         frappe.set_route("Form", r.message.doctype, r.message.name);
        //                     }
        //                 }
        //             });
        //         });
        //     }
        // };
        if (frm.doc.docstatus == 1 ) {
            frm.events.show_general_ledger(frm);
            erpnext.accounts.ledger_preview.show_accounting_ledger_preview(frm);
        };

    },
    
    flight_price: function(frm) {
        calculate_ticket_booking_amount(frm);
    }
});
frappe.ui.form.on('Travelers', {
    travelers_add: function(frm) { 
        calculate_ticket_booking_amount(frm);
    },
    travelers_remove: function(frm) { 
        calculate_ticket_booking_amount(frm);
    }
});

function calculate_ticket_booking_amount(frm) {
    let travelers_count = frm.doc.travelers ? frm.doc.travelers.length : 0;
    let flight_price = frm.doc.flight_price || 0;
    let ticket_booking_amount = travelers_count * flight_price;

    frm.set_value('ticket_booking_amount', ticket_booking_amount);
}
