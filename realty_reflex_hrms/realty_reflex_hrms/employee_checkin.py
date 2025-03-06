import frappe
from geopy.distance import geodesic

def is_inside_geofence(self,method):
    if self.employee:
        emp=frappe.get_doc("Employee",self.employee)
        if emp.branch:
            branch=frappe.get_doc("Branch",emp.branch)
            if branch.custom_latitude and branch.custom_longitude and branch.custom_radius_allowed_for_checkin:
                """Check if a point (device) is inside a circular geofence"""
                distance = geodesic((self.latitude, self.longitude), (branch.custom_latitude, branch.custom_longitude)).meters
                if distance >= branch.custom_radius_allowed_for_checkin:
                    frappe.throw("You didn't have allowed to checkin")
