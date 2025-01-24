



from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import CompensatoryLeaveRequest


class CustomCompensatoryLeaveRequest(CompensatoryLeaveRequest):
    def validate_attendance(self):
        pass
    def validate_holidays(self):
        pass