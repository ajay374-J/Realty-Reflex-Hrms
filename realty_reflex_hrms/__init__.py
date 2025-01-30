__version__ = "0.0.1"


import frappe
from hrms.hr.doctype.attendance import attendance


def add_attendance(events, start, end, conditions=None):
    employee=frappe.db.get_value("Employee",{"user_id":frappe.session.user},['name'])
    if employee:
        query = """select name,shift, attendance_date,leave_application,attendance_request,leave_type,status, employee_name,in_time,out_time,working_hours
            from `tabAttendance` where
            attendance_date between %(from_date)s and %(to_date)s and employee=%(employee)s
            and docstatus < 2"""
    else:
        query = """select name, attendance_date,shift, status,leave_application,attendance_request,leave_type,employee_name,in_time,out_time,working_hours
            from `tabAttendance` where
            attendance_date between %(from_date)s and %(to_date)s
            and docstatus < 2"""

    if conditions:
        query += conditions
    z=[]
    if employee:
        z=frappe.db.sql(query, {"from_date": start, "to_date": end,"employee":employee}, as_dict=True)
    else:
        z=frappe.db.sql(query, {"from_date": start, "to_date": end}, as_dict=True)
    for d in z:
        e = {
            "name": d.name,
            "doctype": "Attendance",
            "start": d.attendance_date,
            "end": d.attendance_date,
            "title": f"{d.employee_name}: {frappe.cstr(d.status)}",
            "status": d.status,
            "docstatus": d.docstatus,
            "employee": employee if employee else "abc"
        }
        if e not in events:
            events.append(e)
            


attendance.add_attendance=add_attendance
