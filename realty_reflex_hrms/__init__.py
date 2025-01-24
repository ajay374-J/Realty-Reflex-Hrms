# __version__ = "0.0.1"


# from datetime import datetime
# from hrms.hr.doctype.attendance_request.attendance_request import AttendanceRequest
# from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import CompensatoryLeaveRequest
# from realty_reflex_hrms.realty_reflex_hrms.attedance import reprocess_attendance
# import frappe
# from frappe.utils import add_days, date_diff, get_datetime, time_diff_in_seconds


# def validate_attendance(self):
#     pass
# def validate_holidays(self):
#     pass
# setattr(CompensatoryLeaveRequest, "validate_holidays", validate_holidays)
# setattr(CompensatoryLeaveRequest, "validate_attendance", validate_attendance)

# def create_attendance_records(self):
#     if self.custom_short_leave ==0:
#         request_days = date_diff(self.to_date, self.from_date) + 1
#         for day in range(request_days):
#             attendance_date = add_days(self.from_date, day)
#             if self.should_mark_attendance(attendance_date):
#                 self.create_or_update_attendance(attendance_date)
#     else:
#         if self.custom_from_time and self.custom_to_time:
#             checkin_entries = []
#             first_datetime_str = f"{self.from_date} {self.custom_from_time}"
#             second_datetime_str = f"{self.to_date} {self.custom_to_time}"
#             first_timestamp = datetime.strptime(first_datetime_str, '%Y-%m-%d %H:%M:%S')
#             log_type = determine_log_type(self.employee,first_timestamp)
#             checkin_entries.append(first_timestamp)
#             second_timestamp = datetime.strptime(second_datetime_str, '%Y-%m-%d %H:%M:%S')
#             checkin_entries.append(second_timestamp)
#             for idx,entry in enumerate(checkin_entries):
#                 new_chkin = frappe.new_doc("Employee Checkin")
#                 new_chkin.employee = self.employee
#                 new_chkin.time=entry
#                 if idx == 0:
#                     new_chkin.log_type = log_type
#                 else:
#                     if log_type == "IN":
#                         new_chkin.log_type = "OUT"
#                     if log_type == "OUT":
#                         new_chkin.log_type = "IN"
#                 new_chkin.save()
#             frappe.db.commit()
#             reprocess_attendance(self.from_date,self.to_date,self.employee)
#         else:
#             frappe.throw("From Time And To Time Are Mandatory.")
            

# def determine_log_type(employee, timestamp):
#     last_checkin = get_last_checkin(employee,timestamp)
#     if last_checkin:
#         last_checkin_time = get_datetime(last_checkin.get('time'))
#         time_difference = time_diff_in_seconds(timestamp, last_checkin_time) / 3600
#         if time_difference > 12:
#             return "IN"
#         else:
#             return "IN" if last_checkin.get('log_type') == "OUT" else "OUT"
#     return "IN"



# def get_last_checkin(employee,timestamp):
#     last_checkin = frappe.db.sql("""
#         SELECT log_type, time 
#         FROM `tabEmployee Checkin`
#         WHERE employee = %s and time < %s
#         ORDER BY time DESC
#         LIMIT 1
#     """, (employee,timestamp), as_dict=True)
    
#     return last_checkin[0] if last_checkin else None


# # setattr(AttendanceRequest, "create_attendance_records", create_attendance_records)
