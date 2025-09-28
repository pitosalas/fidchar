import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.charity_evaluator import evaluate_charity
from data.charity_evaluation_result import CharityEvaluationResult


def test_evaluate_charity_mock_mode():
    config_path = "config/test_config.yaml"
    red_cross_ein = "530196605"
    
    result = evaluate_charity(red_cross_ein, config_path)
    
    assert result.ein == red_cross_ein
    assert result.organization_name == "AMERICAN NATIONAL RED CROSS"
    assert result.grade in ["A", "B", "C", "D", "F"]
    assert result.total_score > 0
    assert result.financial_score > 0
    assert result.data_sources_used == ["ProPublica", "IRS", "Charity Navigator"]
    assert "2025-" in result.evaluation_timestamp
    
    assert result.financial_metrics.total_revenue > 0
    assert result.financial_metrics.net_assets > 0
    assert result.trend_analysis.years_analyzed == 5
    assert result.compliance_check.is_compliant == True
    assert result.external_validation.charity_navigator_rating == 4


def test_evaluate_charity_salvation_army():
    config_path = "config/test_config.yaml"
    salvation_army_ein = "136161001"
    
    result = evaluate_charity(salvation_army_ein, config_path)
    
    assert result.ein == salvation_army_ein
    assert result.organization_name == "THE SALVATION ARMY NATIONAL CORPORATION"
    assert result.grade in ["A", "B", "C", "D", "F"]
    assert result.total_score > 0


def test_evaluate_unknown_charity():
    config_path = "config/test_config.yaml"
    unknown_ein = "999999999"
    
    result = evaluate_charity(unknown_ein, config_path)
    
    assert result.ein == unknown_ein
    assert "Mock Organization" in result.organization_name
    assert result.grade in ["A", "B", "C", "D", "F"]


if __name__ == "__main__":
    test_evaluate_charity_mock_mode()
    test_evaluate_charity_salvation_army()
    test_evaluate_unknown_charity()
    print("All tests passed!")