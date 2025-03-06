app_name = "realty_reflex_hrms"
app_title = "Realty Reflex Hrms"
app_publisher = "Hybrow"
app_description = "HRMS"
app_email = "info@hybrow.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "realty_reflex_hrms",
# 		"logo": "/assets/realty_reflex_hrms/logo.png",
# 		"title": "Realty Reflex Hrms",
# 		"route": "/realty_reflex_hrms",
# 		"has_permission": "realty_reflex_hrms.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/realty_reflex_hrms/css/realty_reflex_hrms.css"
# app_include_js = "/assets/realty_reflex_hrms/js/realty_reflex_hrms.js"

# include js, css files in header of web template
# web_include_css = "/assets/realty_reflex_hrms/css/realty_reflex_hrms.css"
# web_include_js = "/assets/realty_reflex_hrms/js/realty_reflex_hrms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "realty_reflex_hrms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"Attendance" : "public/js/attendance_calender.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "realty_reflex_hrms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "realty_reflex_hrms.utils.jinja_methods",
# 	"filters": "realty_reflex_hrms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "realty_reflex_hrms.install.before_install"
# after_install = "realty_reflex_hrms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "realty_reflex_hrms.uninstall.before_uninstall"
# after_uninstall = "realty_reflex_hrms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "realty_reflex_hrms.utils.before_app_install"
# after_app_install = "realty_reflex_hrms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "realty_reflex_hrms.utils.before_app_uninstall"
# after_app_uninstall = "realty_reflex_hrms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "realty_reflex_hrms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Compensatory Leave Request": "realty_reflex_hrms.comp_off.CustomCompensatoryLeaveRequest",
    "Leave Application": "realty_reflex_hrms.leave_application.CustomLeaveApplication",
    "Web Form":"realty_reflex_hrms.realty_reflex_hrms.web_form.CustomWebForm"


}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Attendance Request": {
		# "validate": "realty_reflex_hrms.realty_reflex_hrms.attedance.validate_short_leave",
        "on_submit": "realty_reflex_hrms.realty_reflex_hrms.overtime_compoff.create_comp_off",

	},
    "Employee Checkin": {"before_save":"realty_reflex_hrms.realty_reflex_hrms.employee_checkin.is_inside_geofence"}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron":{
	"00 08 * * *": [
            "realty_reflex_hrms.realty_reflex_hrms.overtime_compoff.generate_compoff_ot",
            "realty_reflex_hrms.realty_reflex_hrms.overtime_compoff.laps_compoff"
        ],
    "30 23 * * *":[
        "realty_reflex_hrms.atte_calender.setup_time"
    ]
    }

}

# Testing
# -------

# before_tests = "realty_reflex_hrms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "realty_reflex_hrms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "realty_reflex_hrms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["realty_reflex_hrms.utils.before_request"]
# after_request = ["realty_reflex_hrms.utils.after_request"]

# Job Events
# ----------
# before_job = ["realty_reflex_hrms.utils.before_job"]
# after_job = ["realty_reflex_hrms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"realty_reflex_hrms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

