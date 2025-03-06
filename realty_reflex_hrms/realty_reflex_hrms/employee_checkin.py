import frappe
from geopy.distance import geodesic

def is_inside_geofence(self,method):

    doc=frappe.get_doc("Custom Settings")
    if doc.latitude and doc.longitude and doc.allow_checkin_in_radius:
        """Check if a point (device) is inside a circular geofence"""
        distance = geodesic((self.latitude, self.longitude), (doc.latitude, doc.longitude)).meters
        if distance >= doc.allow_checkin_in_radius:
            frappe.throw("You didn't have allowed to checkin")
