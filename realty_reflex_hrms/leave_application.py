from frappe import _, cint
import frappe
from frappe.utils import formatdate, get_fullname
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication

class CustomLeaveApplication(LeaveApplication):
    def notify(self, args):
        args = frappe._dict(args)
        # args -> message, message_to, subject
        if cint(self.follow_via_email):
            contact = args.message_to
            if not isinstance(contact, list):
                if not args.notify == "employee":
                    contact = frappe.get_doc("User", contact).email or contact

            sender = dict()
            sender["email"] = frappe.get_doc("User", frappe.session.user).email
            sender["full_name"] = get_fullname(sender["email"])
            doc=frappe.get_doc("Custom Settings")
            # Fetch emails from custom_ccs child table
            cc_emails = []
            cc_emails = [row.user for row in doc.leave_application_cc if row.user]

            # Fetch required variables for email template
            email_context = {
                "colleague_name": frappe.db.get_value("Employee", self.employee, "employee_name"),
                "employee_name": self.employee_name,
                "leave_category": self.leave_type,
                "from_date": formatdate(self.from_date),
                "to_date": formatdate(self.to_date),
                "total_days": self.total_leave_days,
                "leave_reason": self.description,
                "leave_balance": self.leave_balance,
                "from_session": formatdate(self.half_day_date) if self.half_day else "Full Day",
                "to_session": "Session2",
                "status": self.status,
                "sender_name": sender["full_name"]
            }

            try:
                frappe.sendmail(
                    recipients=contact,
                    sender=sender["email"],
                    subject=frappe.render_template(args.subject, email_context),
                    message=frappe.render_template(args.message, email_context),
                    cc=cc_emails,  # Include CC emails
                )
                frappe.msgprint(_("Email sent to {0}").format(contact))
                if cc_emails:
                    frappe.msgprint(_("CC: {0}").format(", ".join(cc_emails)))
            except frappe.OutgoingEmailError:
                pass
    
    def notify_leave_approver(self):
        if self.leave_approver:
            parent_doc = frappe.get_doc("Leave Application", self.name)
            args = parent_doc.as_dict()

            template = frappe.db.get_single_value("HR Settings", "leave_approval_notification_template")
            if not template:
                frappe.msgprint(
                    _("Please set default template for Leave Approval Notification in HR Settings.")
                )
                return

            email_template = frappe.get_doc("Email Template", template)

            # Fetch additional required variables
            email_context = {
                "employee_name": self.employee_name,
                "employee_id": frappe.db.get_value("Employee", self.employee, "name"),
                "approver_name": frappe.db.get_value("Employee", self.leave_approver, "employee_name"),
                "leave_type": self.leave_type,
                "leave_dates": f"{formatdate(self.from_date)} to {formatdate(self.to_date)}",
                "from_date": formatdate(self.from_date),
                "to_date": formatdate(self.to_date),
                "total_days": self.total_leave_days,
                "leave_reason": self.description or "Not Provided",
                "leave_balance": self.leave_balance,
                "from_session": formatdate(self.half_day_date) if self.half_day else "Full Day",
                "to_session": "Session2",  # Adjust if needed
                "application_date": formatdate(self.creation),
                "approval_link": f"{frappe.utils.get_url()}/app/leave-application/{self.name}",
                "sender_name": get_fullname(frappe.session.user),
                "sender_designation": frappe.db.get_value("Employee", frappe.session.user, "designation"),
                "status": self.status
            }

            subject = frappe.render_template(email_template.subject, email_context)
            message = frappe.render_template(email_template.response_, email_context)

            self.notify(
                {
                    # for post in messages
                    "message": message,
                    "message_to": self.leave_approver,
                    # for email
                    "subject": subject,
                }
            )