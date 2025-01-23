import calendar
import frappe
from datetime import date, datetime,timedelta
from itertools import groupby
from frappe.utils.data import getdate, today
from hrms.hr.doctype.shift_type.shift_type import ShiftType
from frappe.utils import cint, create_batch, flt, get_datetime, get_time, getdate
from hrms.hr.doctype.employee_checkin.employee_checkin import (
	EmployeeCheckin,
	calculate_working_hours,
	mark_attendance_and_link_log,
)
EMPLOYEE_CHUNK_SIZE = 50


@frappe.whitelist()
def reprocess_attendance(from_date,to_date,employee=None,shift=None):
    frappe.enqueue('cn_leave_shift_managment.cn_leave_shift_managment.overrides.attendance.enqueue_reprocess_attendance', from_date = from_date,to_date = to_date,employee=employee,shift=shift, queue='long', timeout=10000)
    
def enqueue_reprocess_attendance(from_date,to_date,employee=None,shift=None):
	from_date = datetime.strptime(from_date, "%Y-%m-%d")
	to_date = datetime.strptime(to_date, "%Y-%m-%d")
	date_list = get_dates_between(from_date,to_date)
	cond=""
	if employee:
		cond+="and employee='{0}'".format(employee)
	# if shift:
	#     cond+="and shift='{0}'".format(shift)
	for date in date_list:
		single_checkin_employees = frappe.db.sql("""
			SELECT employee,shift
			FROM `tabEmployee Checkin`
			WHERE DATE(time) ='{date}' {cond}
			GROUP BY employee,shift
		""".format(date=date,cond=cond), as_dict=True)
		shifts=[]
		for emp in single_checkin_employees:
			attendance = frappe.get_value("Attendance", {"employee": emp["employee"], "attendance_date": date,"docstatus":1}, "name")
			if attendance:
				attend_doc = frappe.get_doc("Attendance",attendance)
				if not attend_doc.attendance_request or not attend_doc.leave_application:
					salary_slip = frappe.db.exists("Salary Slip", {
										"employee": emp["employee"],
										"start_date": ("<=", date),
										"end_date": (">=", date)
									})
					if not salary_slip:
						shift = ""
						if shift:
							shift+="and shift_type='{0}'".format(shift)
						att=frappe.db.sql("""Select shift_type from `tabShift Assignment` where employee='{0}' and docstatus=1 and start_date<='{1}' 
							and (end_date>='{1}' or end_date is null) and status='Active' {shift}""".format(attend_doc.employee,date,shift=shift),as_dict=1)
						if not att:
							att=[]
							if shift:
								att.append({"shift_type":shift})
							else:
								ds=frappe.db.get_value("Employee",{"name":emp["employee"]},'default_shift')
								if ds:
									att.append({"shift_type":ds})
						if att:
							if attend_doc.docstatus == 1 :
								is_validated = validate_attendance(attend_doc)
								if not is_validated:
									attend_doc.cancel()
									frappe.delete_doc("Attendance",attend_doc.name)
									frappe.db.sql("update `tabEmployee Checkin` set skip_auto_attendance=0 where date(time) >= '{0}' and employee='{1}'".format(date,attend_doc.employee))
									fs=frappe.db.sql("select name from `tabEmployee Checkin` where date(time) between '{0}' and '{2}' and employee='{1}'".format(date,attend_doc.employee,date+timedelta(days=1)),as_dict=1)
									for j in fs:
										doc=frappe.get_doc("Employee Checkin",j.get("name"))
										EmployeeCheckin.fetch_shift(doc)
										doc.flags.ignore_validate = True
										doc.save(ignore_permissions=True)
						for shi in att:
							shifts.append(shi.get("shift_type"))
		if len(shifts)>1:
			for sh in list(set(shifts)):
				process_auto_attendance(frappe.get_doc("Shift Type",sh),date)
		else:
			if len(shifts)==1:
				process_auto_attendance(frappe.get_doc("Shift Type",shifts[0]),date)


def validate_attendance(self):
    meta = frappe.get_meta(self.doctype)
    if meta.has_field('employee'):
        loc=frappe.db.get_value("Employee",self.employee,"branch")
        if loc:
            ppc=frappe.db.get_value("Pay Period Configuration",{"enable":1,"location":loc},"name")
            if ppc:
                doc=frappe.get_doc("Pay Period Configuration",ppc)
        
                if doc.enable:
                    for i in doc.doctypes:
                        z=i.fieldname
                        if doc.pay_process_lock_day >= getdate(today()).day:
                            previous_month_date = getdate(today()) - timedelta(days=30)
                            date_obj = datetime(getdate(previous_month_date).year, getdate(previous_month_date).month, doc.pay_process_start_day)
                            formatted_date = date_obj.strftime("%Y-%m-%d")
                            if getdate(self.attendance_date) <getdate(formatted_date) :
                                if self.doctype==i.select_doctype:                                   
                                    return True
            
                        else:
                            date_obj = datetime(getdate(today()).year, getdate(today()).month, doc.pay_process_lock_day)
                            formatted_date = date_obj.strftime("%Y-%m-%d")
                            if getdate(self.attendance_date) <getdate(formatted_date) :
                                if self.doctype==i.select_doctype:                                   
                                    return True

def get_dates_between(start_date, end_date):
    # Generate list of dates between the start and end dates (inclusive)
    date_list = [(start_date + timedelta(days=x)) for x in range((end_date - start_date).days + 1)]
    return date_list

def process_auto_attendance(shift_doc,attend_date):
		if (
			not cint(shift_doc.enable_auto_attendance)
			or not shift_doc.process_attendance_after
			or not shift_doc.last_sync_of_checkin
		):
			return

		logs = get_employee_checkins(shift_doc,attend_date)
		group_key = lambda x: (x["employee"], x["shift_start"])  # noqa
		for key, group in groupby(sorted(logs, key=group_key), key=group_key):
			single_shift_logs = list(group)
			attendance_date = key[1].date()
			employee = key[0]

			if not shift_doc.should_mark_attendance(employee, attendance_date):
				continue

			(
				attendance_status,
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
			) = shift_doc.get_attendance(single_shift_logs)

			mark_attendance_and_link_log(
				single_shift_logs,
				attendance_status,
				attendance_date,
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
				shift_doc.name,
			)

		# commit after processing checkin logs to avoid losing progress
		frappe.db.commit()  # nosemgrep

		assigned_employees = shift_doc.get_assigned_employees(shift_doc.process_attendance_after, True)
		for batch in create_batch(assigned_employees, EMPLOYEE_CHUNK_SIZE):
			for employee in batch:
				shift_doc.mark_absent_for_dates_with_no_attendance(employee)

			frappe.db.commit()  # nosemgrep

def get_employee_checkins(self,attend_date) -> list[dict]:
		return frappe.get_all(
			"Employee Checkin",
			fields=[
				"name",
				"employee",
				"log_type",
				"time",
				"shift",
				"shift_start",
				"shift_end",
				"shift_actual_start",
				"shift_actual_end",
				"device_id",
			],
			filters={
				"skip_auto_attendance": 0,
				"attendance": ("is", "not set"),
				"time": (">=", attend_date),
				"shift_actual_end": ("<", self.last_sync_of_checkin),
				"shift": self.name,
			},
			order_by="employee,time",
		)




def validate_short_leave(self,method):
	if self.custom_short_leave==1:
		t1 = get_time(self.custom_from_time)
		t2 = get_time(self.custom_to_time)

		# Assign a reference date (e.g., today's date) to the time objects
		reference_date = datetime.today().date()
		dt1 = datetime.combine(reference_date, t1)
		dt2 = datetime.combine(reference_date, t2)

		# Calculate the time difference
		time_diff = dt2 - dt1
		hours_diff = time_diff.total_seconds() / 3600
		self.custom_hours=hours_diff
		if flt(hours_diff)>2:
			frappe.throw("you cannot apply more than 2 hours Short Leave")
		today = date.today()

		# Get the first day of the month
		start_date = today.replace(day=1)

		# Get the last day of the month
		_, last_day = calendar.monthrange(today.year, today.month)
		end_date = today.replace(day=last_day)
		hours=frappe.db.get_all("Attendance Request",{"custom_short_leave":1,"employee":self.employee,"docstatus":["!=",2],"from_date":["between",[start_date,end_date]]},["custom_hours"])
		hourss=[]
		for i in hours:
			hourss.append(i.custom_hours)
		print("$$$$$$$$$$$$$$",hourss)
		hour=0
		if self.get("__islocal"):
			hour=hours_diff+sum(hourss)
		else:
			hour=sum(hourss)
		if hour >4:
			frappe.throw("You cannot Apply short leave more than 4 hours in month")
        
        
		