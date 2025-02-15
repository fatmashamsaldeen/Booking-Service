// Copyright (c) 2025, fatma and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Hotel", {
// 	refresh(frm) {

// 	},
// });
// frappe.listview_settings['Hotel'] = {
//     onload: function(listview) {
//         console.log("hiii")
//         frappe.call({
//             method: "booking_service.api.fetch_and_store_hotels", // استبدل "اسم_التطبيق" باسم تطبيقك
//             callback: function(response) {
//                 if (response.message) {
//                     frappe.msgprint(__('Hotels data fetched successfully!'));
//                     // تحديث القائمة مباشرة إذا لزم الأمر
//                     listview.refresh();
//                 }
//             },
//             error: function(err) {
//                 frappe.msgprint(__('Failed to fetch hotel data. Please try again.'));
//             }
//         });
//     }
// };