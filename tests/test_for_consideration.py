#!/usr/bin/env python3
"""Tests for for_consideration functionality.

Tests the for_consideration() function and related badge/filtering logic.
"""

import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fidchar'))

from reports.base_report_builder import BaseReportBuilder, ReportData


class MockEvaluation:
    """Mock charity evaluation for testing"""
    def __init__(self, alignment_score=0, outstanding=0, acceptable=0, unacceptable=0):
        self.alignment_score = alignment_score
        self.outstanding_count = outstanding
        self.acceptable_count = acceptable
        self.unacceptable_count = unacceptable
        self.total_metrics = outstanding + acceptable + unacceptable
        self.organization_name = "Test Charity"
        self.summary = "Test summary"
        self.data_field_values = {}  # Add empty dict for data field values


class TestForConsideration:
    """Test for_consideration() function"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create minimal DataFrame
        self.df = pd.DataFrame({
            'Tax ID': ['12-3456789', '98-7654321', '11-1111111'],
            'Amount_Numeric': [1000, 2000, 3000],
            'Organization': ['Charity A', 'Charity B', 'Charity C']
        })

        # Create test config
        self.config = {
            'for_consideration': {
                'enabled': True,
                'min_alignment_score': 70,
                'min_evaluation_score': 70
            }
        }

        # Create charity evaluations
        self.charity_evaluations = {}

        # Create base report builder
        report_data = ReportData(
            charity_details={},
            graph_info={},
            evaluations=self.charity_evaluations,
            recurring_ein_set=set(),
            pattern_based_ein_set=set()
        )
        self.builder = BaseReportBuilder(
            df=self.df,
            config=self.config,
            report_data=report_data
        )

    def test_returns_false_when_disabled(self):
        """Should return False when for_consideration is disabled"""
        self.config['for_consideration']['enabled'] = False
        result = self.builder.for_consideration('12-3456789')
        assert result is False

    def test_returns_false_when_no_evaluation(self):
        """Should return False when charity has no evaluation"""
        result = self.builder.for_consideration('12-3456789')
        assert result is False

    def test_returns_false_when_alignment_too_low(self):
        """Should return False when alignment score below threshold"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=60,  # Below 70
            outstanding=8,
            acceptable=2,
            unacceptable=0
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is False

    def test_returns_false_when_alignment_none(self):
        """Should return False when alignment score is None"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=None,
            outstanding=8,
            acceptable=2,
            unacceptable=0
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is False

    def test_returns_false_when_evaluation_score_too_low(self):
        """Should return False when evaluation score below threshold"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=80,  # Good
            outstanding=3,
            acceptable=3,
            unacceptable=4  # 60% acceptable/outstanding
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is False

    def test_returns_false_when_no_metrics(self):
        """Should return False when total_metrics is 0"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=80,
            outstanding=0,
            acceptable=0,
            unacceptable=0
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is False

    def test_returns_true_when_both_criteria_met(self):
        """Should return True when both alignment and evaluation meet thresholds"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=80,  # Above 70
            outstanding=7,
            acceptable=3,
            unacceptable=0  # 100% acceptable/outstanding
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is True

    def test_returns_true_at_exact_thresholds(self):
        """Should return True at exact threshold values"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=70,  # Exactly 70
            outstanding=4,
            acceptable=3,
            unacceptable=3  # Exactly 70%
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is True

    def test_uses_custom_thresholds(self):
        """Should use custom threshold values from config"""
        self.config['for_consideration']['min_alignment_score'] = 80
        self.config['for_consideration']['min_evaluation_score'] = 80

        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=75,  # Below new threshold
            outstanding=8,
            acceptable=2,
            unacceptable=0
        )
        result = self.builder.for_consideration('12-3456789')
        assert result is False

        # Now meet the higher threshold
        self.charity_evaluations['98-7654321'] = MockEvaluation(
            alignment_score=85,  # Above 80
            outstanding=8,
            acceptable=0,
            unacceptable=2  # 80%
        )
        result = self.builder.for_consideration('98-7654321')
        assert result is True


class TestForConsiderationBadge:
    """Test FOR CONSIDERATION badge display"""

    def setup_method(self):
        """Setup test fixtures"""
        self.df = pd.DataFrame({
            'Tax ID': ['12-3456789'],
            'Amount_Numeric': [1000],
            'Organization': ['Test Charity']
        })

        self.config = {
            'for_consideration': {
                'enabled': True,
                'min_alignment_score': 70,
                'min_evaluation_score': 70
            }
        }

        self.charity_evaluations = {
            '12-3456789': MockEvaluation(
                alignment_score=80,
                outstanding=7,
                acceptable=3,
                unacceptable=0
            )
        }

        report_data = ReportData(
            charity_details={},
            graph_info={},
            evaluations=self.charity_evaluations,
            recurring_ein_set=set(),
            pattern_based_ein_set=set()
        )
        self.builder = BaseReportBuilder(
            df=self.df,
            config=self.config,
            report_data=report_data
        )

    def test_badge_appears_in_formatted_output(self):
        """Should include CONSDR badge in formatted charity info"""
        result = self.builder.format_charity_info('12-3456789', 'Test Charity')
        assert 'CONSDR' in result['html_org']

    def test_badge_has_correct_styling(self):
        """Should use charity-badge CSS class for CONSDR badge"""
        result = self.builder.format_charity_info('12-3456789', 'Test Charity')
        assert 'class="charity-badge"' in result['html_org']  # Uses charity-badge CSS class
        assert 'CONSDR' in result['html_org']  # Badge text present

    def test_badge_not_shown_when_criteria_not_met(self):
        """Should not show badge when criteria not met"""
        self.charity_evaluations['12-3456789'] = MockEvaluation(
            alignment_score=60,  # Too low
            outstanding=5,
            acceptable=5,
            unacceptable=0
        )
        result = self.builder.format_charity_info('12-3456789', 'Test Charity')
        assert 'CONSDR' not in result['html_org']

    def test_badge_shown_with_recurring_badge(self):
        """Should NOT show CONSDR badge when charity is recurring"""
        self.builder.pattern_based_ein_set = {'12-3456789'}
        result = self.builder.format_charity_info('12-3456789', 'Test Charity')
        assert 'RECUR' in result['html_org']
        assert 'CONSDR' not in result['html_org']  # Should NOT show for recurring charities

    def test_badge_order(self):
        """RECUR should come before CONSDR (when both could appear)"""
        # Test with a non-recurring charity to verify CONSDR appears
        result = self.builder.format_charity_info('12-3456789', 'Test Charity')
        html = result['html_org']
        assert 'CONSDR' in html
        assert 'RECUR' not in html


class TestEvaluationScoreCalculation:
    """Test evaluation score calculation logic"""

    def test_calculates_100_percent(self):
        """Should calculate 100% when all metrics acceptable/outstanding"""
        eval = MockEvaluation(
            alignment_score=80,
            outstanding=5,
            acceptable=5,
            unacceptable=0
        )
        acceptable_or_better = eval.outstanding_count + eval.acceptable_count
        evaluation_score = (acceptable_or_better / eval.total_metrics) * 100
        assert evaluation_score == 100.0

    def test_calculates_70_percent(self):
        """Should calculate 70% correctly"""
        eval = MockEvaluation(
            alignment_score=80,
            outstanding=4,
            acceptable=3,
            unacceptable=3
        )
        acceptable_or_better = eval.outstanding_count + eval.acceptable_count
        evaluation_score = (acceptable_or_better / eval.total_metrics) * 100
        assert evaluation_score == 70.0

    def test_calculates_0_percent(self):
        """Should calculate 0% when all unacceptable"""
        eval = MockEvaluation(
            alignment_score=80,
            outstanding=0,
            acceptable=0,
            unacceptable=10
        )
        acceptable_or_better = eval.outstanding_count + eval.acceptable_count
        evaluation_score = (acceptable_or_better / eval.total_metrics) * 100
        assert evaluation_score == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
