from ..data.charity_evaluation_result import FinancialMetrics


class FinancialAnalyzer:
    def extract_metrics(self, filing_data: dict) -> FinancialMetrics:
        return FinancialMetrics(
            program_expense_ratio=0.0,
            admin_expense_ratio=0.0,
            fundraising_expense_ratio=0.0,
            net_assets=filing_data.get("totassetsend", 0) - filing_data.get("totliabend", 0),
            total_revenue=filing_data.get("totrevenue", 0),
            total_expenses=filing_data.get("totfuncexpns", 0),
            program_expenses=filing_data.get("totprogrevexp", 0),
            admin_expenses=filing_data.get("totadminexp", 0),
            fundraising_expenses=filing_data.get("totfndrsexp", 0),
            total_assets=filing_data.get("totassetsend", 0),
            total_liabilities=filing_data.get("totliabend", 0)
        )
    
    def calculate_score(self, metrics: FinancialMetrics) -> float:
        return 75.0