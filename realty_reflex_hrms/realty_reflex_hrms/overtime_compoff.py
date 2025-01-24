from datetime import datetime, timedelta

from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
import frappe
from frappe.utils import add_days
from frappe.utils.data import get_time, getdate, today


@frappe.whitelist()
def generate_compoff_ot(self,method):
	class_forms = frappe.db.sql("""
    SELECT 
        name, employee, type
    FROM (
        SELECT 
            name, employee, type,
            ROW_NUMBER() OVER (PARTITION BY employee ORDER BY creation DESC) as rn
        FROM 
            `tabClassification Form`
        WHERE 
            docstatus = 1
    ) as ranked_cf
    WHERE 
        rn = 1
    """, as_dict=True)
	yesterday = (datetime.now() - timedelta(days=1)).date() 
	for form in class_forms:
		holiday_dates = []
		
		hl_week_offs = frappe.db.get_all("Holiday",{"parent":get_holiday_list_for_employee(form.employee),"holiday_date":['between',[yesterday,yesterday]]},["holiday_date"])
		for hl in hl_week_offs:
			holiday_dates.append(hl.holiday_date)		
		form_type = form.type
		diff=0
		if holiday_dates:
			doc=frappe.get_doc("Employee",form.employee)
			shift_hours=0
			end_time=frappe.db.get_value("Shift Type",doc.default_shift,"end_time")
			start_time=frappe.db.get_value("Shift Type",doc.default_shift,"start_time")
			if end_time<start_time:
				dateTimeA = datetime.combine(getdate(today()), get_time(start_time))
				dateTimeB = datetime.combine(getdate(today())+timedelta(days=1), get_time(end_time))
				dateTimeDifference = dateTimeB- dateTimeA
				shift_hours = dateTimeDifference.total_seconds() / 3600
			else:
				shift_hours=end_time-start_time
				shift_hours=round((end_time-start_time).total_seconds() / 3600,2)

			first_checkin = frappe.db.sql("""SELECT name,time,shift
							FROM `tabEmployee Checkin` 
							WHERE employee = '"""+form.employee+"""'
							AND log_type = 'IN'
							AND DATE(time) = '"""+str(yesterday)+"""'
							ORDER BY time ASC
							LIMIT 1""", as_dict=True)
			last_checkout=[]
			if first_checkin:
				end_time=frappe.db.get_value("Shift Type",first_checkin[0].get("shift"),"end_time")
				start_time=frappe.db.get_value("Shift Type",first_checkin[0].get("shift"),"start_time")
				if end_time<start_time:
					last_checkout = frappe.db.sql("""SELECT name,time
									FROM `tabEmployee Checkin` 
									WHERE employee = '"""+form.employee+"""'
									AND log_type = 'OUT'
									AND DATE(time) = '"""+str(yesterday+timedelta(days=1))+"""'
									ORDER BY time ASC
									LIMIT 1""", as_dict=True)
				else:
					last_checkout = frappe.db.sql("""SELECT name,time
									FROM `tabEmployee Checkin` 
									WHERE employee = '"""+form.employee+"""'
									AND log_type = 'OUT'
									AND DATE(time) = '"""+str(yesterday)+"""'
									ORDER BY time DESC
									LIMIT 1""", as_dict=True)
			if first_checkin and last_checkout:
				in_time = first_checkin[0]['time']
				out_time = last_checkout[0]['time']
				diff = get_time(out_time-in_time).hour
				if not frappe.db.exists("Compensatory Leave Request",{"employee":form.employee,"work_from_date":[">=",yesterday],"work_end_date":["<=",yesterday]}):
					if form_type == "Compensatory Off" and diff  > frappe.db.get_value("Shift Type",first_checkin[0]['shift'],"custom_holiday_min_compensatory_off_hrs"):
						comp_off_doc = frappe.new_doc("Compensatory Leave Request")
						comp_off_doc.employee = form.employee
						comp_off_doc.leave_type = frappe.db.get_value("Leave Type",{"is_compensatory":1},"name")
						comp_off_doc.work_from_date = yesterday
						comp_off_doc.work_end_date = yesterday
						comp_off_doc.reason = "Extra Work On Holiday"
						comp_off_doc.save(ignore_permissions = True)
						comp_off_doc.submit()
				if not frappe.db.exists("Overtime Log",{"employee":form.employee,"date":yesterday}):
					if form_type=="Ex Gratia" and diff - shift_hours  > frappe.db.get_value("Shift Type",first_checkin[0]['shift'],"custom_holiday_min_overtime_hrs"):
						overtime_log = frappe.new_doc("Overtime Log")
						overtime_log.employee = form.employee
						overtime_log.shift = first_checkin[0]['shift']
						overtime_log.date= yesterday
						overtime_log.overtime_hrs = diff - shift_hours
						overtime_log.save(ignore_permissions = True)




@frappe.whitelist()
def laps_compoff():
	
	comp_off=frappe.db.get_all("Compensatory Leave Request",{"docstatus":1},["*"])
	for i in comp_off:
		if getdate(add_days( getdate(i.work_from_date), 7))<=getdate(today()):

			lle=frappe.db.get_value("Leave Ledger Entry",{"employee":i.employee,"leave_type":frappe.db.get_value("Leave Type",{"is_compensatory":1},"name"),"transaction_type":"Leave Allocation","transaction_name":i.leave_allocation,"is_expired":0},"name")
			if lle:
				leave_ledger=frappe.get_doc("Leave Ledger Entry",lle)
				leave_ledger.db_set("is_expired",1)



	


def create_comp_off(self,method):
	holiday_dates = []
	hl_week_offs = frappe.db.get_all("Holiday",{"parent":get_holiday_list_for_employee(self.employee),"holiday_date":['between',[self.from_date,self.from_date]]},["holiday_date"])
	for hl in hl_week_offs:
		holiday_dates.append(hl.holiday_date)
	if len(holiday_dates)>0:
		doc=frappe.new_doc("Compensatory Leave Request")
		doc.employee=self.employee
		doc.work_from_date=self.from_date
		doc.work_end_date=self.to_date
		leave_type=frappe.db.get_value("Leave Type",{"is_compensatory":1},"name")
		doc.leave_type=leave_type
		doc.company=self.company
		doc.reason=self.reason
		doc.save(ignore_permissions=True)
		doc.submit()

