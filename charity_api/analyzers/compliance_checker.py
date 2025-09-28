from ..data.charity_evaluation_result import ComplianceCheck


class ComplianceChecker:
    def __init__(self, irs_data_path: str):
        self.irs_data_path = irs_data_path
    
    def check_compliance(self, ein: str) -> ComplianceCheck:
        return ComplianceCheck(
            is_compliant=True,
            issues=[],
            in_pub78=True,
            is_revoked=False,
            has_recent_filing=True
        )