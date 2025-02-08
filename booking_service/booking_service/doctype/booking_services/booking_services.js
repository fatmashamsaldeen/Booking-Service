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
        const dialog = new frappe.ui.form.MultiSelectDialog({
            doctype: "Hotel",  
            target: frm,
            setters: {
                iatacode: null,
                countrycode: null,

            },
            add_filters_group: 1,

            action(selections) {
                console.log("Selected Flights:", selections);  
                
                if (selections.length ===1) {
                    let row = frm.add_child("hotel");
                    row.hotel = selectehotel;
                    frm.refresh_field("hotel");
                    
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
                        let selectehotel = selectedItems[0].name; // جلب اسم الرحلة
                        // let selectedPrice = selectedItems[0].total_price; // جلب السعر

                        let row = frm.add_child("hotel");
                        row.hotel = selectehotel;
                        frm.refresh_field("hotel");
                                                // frm.set_value("flight_price", selectedPrice); // تخزين السعر في الحقل "flight_price"
                        dialog.dialog.hide();  // إغلاق النافذة
                    } else {
                        frappe.msgprint(__('Please select a flight first.'));
                    }
                });

                footer.prepend(selectBtn); // إضافة الزر في الفوتر
            }
        }, 500); // تأخير التنفيذ حتى يتم تحميل العناصر
    },
    onload: function(frm) {
        if (frm.doc.outstanding === -1.00) {
            frm.toggle_display('outstanding', false);
        }
    },
    refresh: function(frm) {
        calculate_total_booking_amount(frm);
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
    
    flight_price: function(frm) {
        calculate_total_booking_amount(frm);
    }
});
frappe.ui.form.on('Travelers', {
    travelers_add: function(frm) { 
        calculate_total_booking_amount(frm);
    },
    travelers_remove: function(frm) { 
        calculate_total_booking_amount(frm);
    }
});

function calculate_total_booking_amount(frm) {
    let travelers_count = frm.doc.travelers ? frm.doc.travelers.length : 0;
    let flight_price = frm.doc.flight_price || 0;
    let total_amount = travelers_count * flight_price;

    frm.set_value('total_booking_amount', total_amount);
}
