from ..data.charity_evaluation_result import TrendAnalysis
from typing import List, Dict


class TrendAnalyzer:
    def analyze_trends(self, filings: List[Dict]) -> TrendAnalysis:
        return TrendAnalysis(
            revenue_growth_rate=0.05,
            growth_consistency_score=8.0,
            volatility_penalty=-2.0,
            years_analyzed=len(filings)
        )
    
    def calculate_modifier(self, trend_analysis: TrendAnalysis) -> float:
        return trend_analysis.growth_consistency_score + trend_analysis.volatility_penalty