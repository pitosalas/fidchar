#!/usr/bin/env python3
"""Tests for core analysis functions.

These tests verify the business logic of data analysis,
NOT the report formatting/structure.
"""

import pytest
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fidchar'))

from core.analysis import (
    analyze_by_category,
    analyze_by_year,
    analyze_recurring_donations,
    analyze_consistent_donors,
    analyze_donation_patterns,
    get_top_charities_basic
)


@pytest.fixture
def sample_df():
    """Create sample donation data for testing"""
    data = {
        'Tax ID': ['11-1111111', '22-2222222', '11-1111111', '33-3333333', '22-2222222'],
        'Organization': ['Charity A', 'Charity B', 'Charity A', 'Charity C', 'Charity B'],
        'Amount_Numeric': [1000.0, 500.0, 1500.0, 750.0, 600.0],
        'Charitable Sector': ['Education', 'Health', 'Education', 'Environment', 'Health'],
        'Year': [2024, 2024, 2025, 2024, 2025],
        'Submit Date': pd.to_datetime(['2024-01-15', '2024-03-20', '2025-02-10', '2024-05-01', '2025-01-05']),
        'Recurring': ['annually through indefinitely', '', 'annually through indefinitely', '', 'semi-annually through indefinitely']
    }
    return pd.DataFrame(data)


@pytest.fixture
def recurring_donations_df():
    """Create sample recurring donations data"""
    data = {
        'Tax ID': ['11-1111111', '22-2222222', '33-3333333', '44-4444444'],
        'Organization': ['Active Charity A', 'Active Charity B', 'Old Charity C', 'Active Charity D'],
        'Amount_Numeric': [1000.0, 500.0, 750.0, 2000.0],
        'Recurring': [
            'annually through indefinitely',
            'semi-annually through indefinitely',
            'annually through indefinitely',
            'annually through indefinitely'
        ],
        'Submit Date': pd.to_datetime(['2025-01-15', '2024-12-20', '2022-05-01', '2024-11-10'])
    }
    return pd.DataFrame(data)


@pytest.fixture
def consistent_donors_df():
    """Create sample data for consistent donors testing"""
    current_year = datetime.now().year
    data = {
        'Tax ID': ['11-1111111'] * 5 + ['22-2222222'] * 5 + ['33-3333333'] * 4,
        'Organization': ['Consistent A'] * 5 + ['Consistent B'] * 5 + ['Not Consistent'] * 4,
        'Amount_Numeric': [600, 700, 800, 900, 1000, 500, 550, 600, 650, 700, 600, 700, 400, 500],
        'Year': list(range(current_year - 4, current_year + 1)) * 2 + list(range(current_year - 3, current_year + 1)),
        'Charitable Sector': ['Education'] * 14,
        'Submit Date': pd.to_datetime([f'{year}-06-15' for year in
                                      list(range(current_year - 4, current_year + 1)) * 2 +
                                      list(range(current_year - 3, current_year + 1))])
    }
    return pd.DataFrame(data)


class TestAnalyzeByCategory:
    """Test category analysis function"""

    def test_returns_series(self, sample_df):
        result = analyze_by_category(sample_df)
        assert isinstance(result, pd.Series)

    def test_correct_totals(self, sample_df):
        result = analyze_by_category(sample_df)
        assert result['Education'] == 2500.0
        assert result['Health'] == 1100.0
        assert result['Environment'] == 750.0

    def test_sorted_descending(self, sample_df):
        result = analyze_by_category(sample_df)
        values = result.values
        assert all(values[i] >= values[i+1] for i in range(len(values)-1))

    def test_empty_dataframe(self):
        empty_df = pd.DataFrame(columns=['Charitable Sector', 'Amount_Numeric'])
        result = analyze_by_category(empty_df)
        assert len(result) == 0


class TestAnalyzeByYear:
    """Test yearly analysis function"""

    def test_returns_two_series(self, sample_df):
        yearly_amounts, yearly_counts = analyze_by_year(sample_df)
        assert isinstance(yearly_amounts, pd.Series)
        assert isinstance(yearly_counts, pd.Series)

    def test_correct_yearly_amounts(self, sample_df):
        yearly_amounts, _ = analyze_by_year(sample_df)
        assert yearly_amounts[2024] == 2250.0
        assert yearly_amounts[2025] == 2100.0

    def test_correct_yearly_counts(self, sample_df):
        _, yearly_counts = analyze_by_year(sample_df)
        assert yearly_counts[2024] == 3
        assert yearly_counts[2025] == 2

    def test_sorted_by_year(self, sample_df):
        yearly_amounts, yearly_counts = analyze_by_year(sample_df)
        assert list(yearly_amounts.index) == sorted(yearly_amounts.index)
        assert list(yearly_counts.index) == sorted(yearly_counts.index)


class TestAnalyzeRecurringDonations:
    """Test recurring donations analysis"""

    def test_returns_dataframe(self, recurring_donations_df):
        result = analyze_recurring_donations(recurring_donations_df, "total", 1, 4)
        assert isinstance(result, pd.DataFrame)

    def test_filters_old_donations(self, recurring_donations_df):
        result = analyze_recurring_donations(recurring_donations_df, "total", 1, 2)
        eins = result['EIN'].tolist()
        assert '33-3333333' not in eins

    def test_includes_recent_donations(self, recurring_donations_df):
        result = analyze_recurring_donations(recurring_donations_df, "total", 1, 4)
        eins = result['EIN'].tolist()
        assert '11-1111111' in eins
        assert '22-2222222' in eins
        assert '44-4444444' in eins

    def test_has_required_columns(self, recurring_donations_df):
        result = analyze_recurring_donations(recurring_donations_df, "total", 1, 4)
        required_cols = ['EIN', 'Organization', 'Amount', 'Total_Ever_Donated', 'Period', 'Last_Donation_Date']
        assert all(col in result.columns for col in required_cols)

    def test_sorted_by_amount_descending(self, recurring_donations_df):
        result = analyze_recurring_donations(recurring_donations_df, "total", 1, 4)
        amounts = result['Amount'].values
        assert all(amounts[i] >= amounts[i+1] for i in range(len(amounts)-1))

    def test_calculates_total_ever_donated(self, recurring_donations_df):
        result = analyze_recurring_donations(recurring_donations_df, "total", 1, 4)
        charity_d = result[result['EIN'] == '44-4444444'].iloc[0]
        assert charity_d['Total_Ever_Donated'] == 2000.0

    def test_empty_recurring_field(self):
        data = {
            'Tax ID': ['11-1111111'],
            'Organization': ['No Recurring'],
            'Amount_Numeric': [1000.0],
            'Recurring': [''],
            'Submit Date': pd.to_datetime(['2025-01-15'])
        }
        df = pd.DataFrame(data)
        result = analyze_recurring_donations(df, "total", 1, 4)
        assert len(result) == 0


class TestAnalyzeConsistentDonors:
    """Test consistent donors analysis"""

    def test_returns_dict(self, consistent_donors_df):
        result = analyze_consistent_donors(consistent_donors_df)
        assert isinstance(result, dict)

    def test_identifies_consistent_donors(self, consistent_donors_df):
        result = analyze_consistent_donors(consistent_donors_df)
        assert '11-1111111' in result
        assert '22-2222222' in result

    def test_excludes_non_consistent(self, consistent_donors_df):
        result = analyze_consistent_donors(consistent_donors_df)
        assert '33-3333333' not in result

    def test_donor_has_required_fields(self, consistent_donors_df):
        result = analyze_consistent_donors(consistent_donors_df)
        if result:
            first_donor = list(result.values())[0]
            assert 'organization' in first_donor
            assert 'sector' in first_donor
            assert 'yearly_amounts' in first_donor
            assert 'total_5_year' in first_donor
            assert 'average_per_year' in first_donor

    def test_calculates_5_year_total(self, consistent_donors_df):
        result = analyze_consistent_donors(consistent_donors_df)
        if '11-1111111' in result:
            assert result['11-1111111']['total_5_year'] == 4000.0


class TestGetTopCharitiesBasic:
    """Test top charities extraction"""

    def test_returns_dataframe(self, sample_df):
        result = get_top_charities_basic(sample_df, top_n=2)
        assert isinstance(result, pd.DataFrame)

    def test_respects_top_n(self, sample_df):
        result = get_top_charities_basic(sample_df, top_n=2)
        assert len(result) == 2

    def test_sorted_by_amount_descending(self, sample_df):
        result = get_top_charities_basic(sample_df, top_n=10)
        amounts = result['Amount_Numeric'].values
        assert all(amounts[i] >= amounts[i+1] for i in range(len(amounts)-1))

    def test_groups_by_tax_id(self, sample_df):
        result = get_top_charities_basic(sample_df, top_n=10)
        assert result.loc['11-1111111']['Amount_Numeric'] == 2500.0


class TestAnalyzeDonationPatterns:
    """Test donation patterns analysis"""

    def test_returns_two_dataframes(self, sample_df):
        one_time, stopped_recurring = analyze_donation_patterns(sample_df)
        assert isinstance(one_time, pd.DataFrame)
        assert isinstance(stopped_recurring, pd.DataFrame)

    def test_one_time_has_single_donation(self, sample_df):
        one_time, _ = analyze_donation_patterns(sample_df)
        for _, row in one_time.iterrows():
            assert row['Donation_Count'] == 1

    def test_stopped_recurring_multiple_donations(self, sample_df):
        one_time, stopped_recurring = analyze_donation_patterns(sample_df)
        for _, row in stopped_recurring.iterrows():
            assert row['Donation_Count'] > 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
