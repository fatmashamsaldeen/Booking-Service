// Copyright (c) 2025, fatma and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking Available Rooms', {
    hotel: function (frm) {
        frm.trigger('set_room_query'); // استدعاء الدالة عند تغيير الفندق
    },
    room_type: function (frm) {
        frm.trigger('set_room_query'); // استدعاء الدالة عند تغيير نوع الغرفة
    },
    set_room_query: function (frm) {
        frm.set_query('room', function () {
            let filters = {};

            if (frm.doc.hotel) {
                filters.hotel = frm.doc.hotel;  // تصفية الغرف حسب الفندق المحدد
            }

            if (frm.doc.room_type) {
                filters.room_type = frm.doc.room_type;  // تصفية الغرف حسب نوع الغرفة المحدد
            }

            filters.status = "Available"; // عرض الغرف المتاحة فقط

            return {
                filters: filters
            };
        });
    },
    // after_save: function(frm) {
    //     if (frm.doc.related_booking_service) {
    //         // تحديث القيم في "Booking Services"
    //         frappe.db.set_value("Booking Services", frm.doc.related_booking_service, {
    //             "hotel": frm.doc.name,  // نقل اسم الغرفة إلى حقل hotel
    //             "hotel_booking_amount": frm.doc.total_amount // نقل المبلغ إلى hotel_booking_amount
    //         }).then(() => {
    //             // بعد التحديث، انتظر قليلاً ثم انتقل إلى السجل المحدد
    //             setTimeout(() => {
    //                 frappe.set_route("Form", "Booking Services", frm.doc.related_booking_service);
    //             }, 500);
    //         }).catch(err => {
    //             frappe.msgprint(__("حدث خطأ أثناء التحديث: " + err.message));
    //         });
    //     }
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
    
                        if (!doc.hotels) {
                            doc.hotels = [];
                        }
    
                        // 🔹 إضافة صف جديد مع التأكد من أن `amount` رقم وليس نصًا
                        let newRow = {
                            booking_available_room: frm.doc.name,
                            amount: parseFloat(frm.doc.total_amount) || 0
                        };
                        doc.hotels.push(newRow);
    
                        // 🔹 حساب المجموع الصحيح لجميع قيم `amount`
                        let totalAmount = doc.hotels.reduce((sum, row) => sum + (parseFloat(row.amount) || 0), 0);
                        doc.hotel_booking_amount = totalAmount;
    
                        // 🔹 حفظ التعديلات
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
                                                cur_frm.refresh();  // 🔄 الحل الصحيح: تحديث الفورم بعد التحميل
                                            });
                                        }, 1500); // ⏳ انتظر 1.5 ثانية لضمان تحميل الصفحة قبل التحديث
                                    }, 1000);
                                }
                            }
                        });
                    }
                }
            });
        }
    }
    ,
    refresh: function(frm) {
        console.log("Form loaded: Booking Available Rooms");
    },
    chick_in_date: function(frm) {
        console.log("chick_in_date changed:", frm.doc.chick_in_date);
        frm.trigger("calculate_total_amount");
    },
    chick_out_date: function(frm) {
        console.log("chick_out_date changed:", frm.doc.chick_out_date);
        frm.trigger("calculate_total_amount");
    },
    price_per_night: function(frm) {
        console.log("price_per_night changed:", frm.doc.price_per_night);
        frm.trigger("calculate_total_amount");
    },
    calculate_total_amount: function(frm) {
        console.log("Calculating total amount...");
        if (frm.doc.chick_in_date && frm.doc.chick_out_date && frm.doc.price_per_night) {
            let checkIn = new Date(frm.doc.chick_in_date);
            let checkOut = new Date(frm.doc.chick_out_date);

            let nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24)); 
            
            if (nights > 0) {
                frm.set_value("total_amount", nights * frm.doc.price_per_night);
                console.log("Total Amount Updated:", nights * frm.doc.price_per_night);
            } else {
                frm.set_value("total_amount", 0);
                console.log("Total Amount Reset to 0");
            }
        }
    }
});
