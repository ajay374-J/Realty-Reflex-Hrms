import frappe
from frappe import STANDARD_USERS, _, msgprint, throw
from frappe.utils import cint


def send_welcome_mail(self, method):
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",self.name)
    if self.name not in STANDARD_USERS:

        if (
            
             cint(self.send_welcome_email)
           
        ):
            self.send_welcome_mail_to_user()
            if frappe.session.user != "Guest":
                msgprint(_("Welcome email sent"))
            return