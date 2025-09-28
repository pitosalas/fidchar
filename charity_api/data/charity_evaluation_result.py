from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FinancialMetrics:
    program_expense_ratio: float
    admin_expense_ratio: float
    fundraising_expense_ratio: float
    net_assets: float
    total_revenue: int
    total_expenses: int
    program_expenses: int
    admin_expenses: int
    fundraising_expenses: int
    total_assets: int
    total_liabilities: int


@dataclass
class TrendAnalysis:
    revenue_growth_rate: float
    growth_consistency_score: float
    volatility_penalty: float
    years_analyzed: int


@dataclass
class ComplianceCheck:
    is_compliant: bool
    issues: List[str]
    in_pub78: bool
    is_revoked: bool
    has_recent_filing: bool


@dataclass
class ExternalValidation:
    charity_navigator_rating: Optional[int]
    charity_navigator_score: float
    has_transparency_seal: bool
    has_advisory_alerts: bool
    negative_news_alerts: int


@dataclass
class CharityEvaluationResult:
    ein: str
    organization_name: str
    total_score: float
    grade: str
    financial_score: float
    trend_modifier: float
    validation_bonus: float
    compliance_penalty: float
    financial_metrics: FinancialMetrics
    trend_analysis: TrendAnalysis
    compliance_check: ComplianceCheck
    external_validation: ExternalValidation
    evaluation_timestamp: str
    data_sources_used: List[str]