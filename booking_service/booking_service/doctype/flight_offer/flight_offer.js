// Copyright (c) 2025, fatma and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Flight Offer", {
// 	refresh(frm) {

// 	},
// });
// frappe.listview_settings['Flight Offer'] = {
//     onload: function(listview) {
//         frappe.call({
//             method: "booking_service.api.fetch_and_store_flight_offers",
//             callback: function(response) {
//                 if (response.message) {
//                     frappe.msgprint(__('Flight offers fetched successfully!'));
//                     // تحديث القائمة إذا لزم الأمر
//                     listview.refresh();
//                 }
//             },
//             error: function(err) {
//                 frappe.msgprint(__('Failed to fetch flight offers. Please try again.'));
//             }
//         });
//     }
// };