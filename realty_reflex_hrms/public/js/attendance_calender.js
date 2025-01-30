frappe.views.calendar["Attendance"] = {
    field_map: {
        start: "start",
        end: "end",
        id: "name",
        title: "title",
        allDay: "allDay",
        color: "color",
        employee:"employee",
    },
    style_map: {
        // Map conditions to colors
        Absent: "danger",       // Red
        Present: "success",     // Green
        Holiday: "info",        // Blue
    },
    get_css_class: function (data) {
        if (data.doctype === "Holiday") return "default";
        else if (data.doctype === "Attendance") {
            if (data.status === "Absent" || data.status === "On Leave") {
                return "danger";
            }
            if (data.status === "Half Day") return "warning";
            return "success";
        }
    },
    options: {
        header: {
            left: "prev,next today",
            center: "title",
            right: "month",
        },
        viewRender: function (view) {
            // Inject the legend dynamically
            if (!$(".calendar-legend").length) {
                const legendHTML = `
                    <div class="calendar-legend" style="margin-bottom: 10px; display: flex; gap: 10px;">
                        <span class="badge badge-danger">Absent</span>
                        <span class="badge badge-warning">Half Day</span>
                        <span class="badge badge-success">Present</span>
                        <span class="badge badge-info">Holiday</span>
                        <span class="badge badge-success">Work from Home</span>
                        <span class="badge badge-danger">On Leave</span>
                    </div>
                `;

                // Append legend to the calendar view container
                $(".fc-toolbar").append(legendHTML);
            }
        },
        eventRender: function (event, element) {
            if (event.status === "Absent") {
                const date = moment(event.start).format('YYYY-MM-DD');
                
                // Check if Leave Application exists
                frappe.call({
                    method: "cn_leave_shift_managment.api.is_leave_application_exists",
                    args: {
                        date: date,
                        employee: event.employee, // Assuming employee is part of the event object
                    },
                    callback: function (response) {
                        if (!response.message) {
                            // Add the Apply Leave button dynamically
                            const button = $('<button>')
                                .text('Apply Leave')
                                .addClass('btn btn-xs btn-primary')
                                .click(function (e) {
                                    e.stopPropagation(); // Prevent default calendar event click behavior

                                    frappe.new_doc('Leave Application', {
                                        from_date: date,
                                        to_date: date,
                                        reason: 'Marked as Absent in Attendance',
                                    });
                                });
                            element.append(button);
                        }
                    },
                    error: function (error) {
                        console.error("Error checking Leave Application:", error);
                    },
                });
            }
        },
    },
    get_events_method: "hrms.hr.doctype.attendance.attendance.get_events",
};
