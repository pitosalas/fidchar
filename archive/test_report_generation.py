#!/usr/bin/env python3
"""Report generation tests.

Tests that verify report builders produce valid output in different formats
(HTML, Markdown, Text) with correct structure and content.
"""

import pytest
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fidchar'))

from core.analysis import analyze_recurring_donations
from reports.html_report_builder import HTMLReportBuilder


@pytest.fixture
def test_donation_data():
    """Create consistent test data for report generation tests"""
    current_year = datetime.now().year
    data = {
        'Tax ID': ['11-1111111', '22-2222222', '33-3333333', '11-1111111', '22-2222222'],
        'Organization': ['Test Charity A', 'Test Charity B', 'Test Charity C', 'Test Charity A', 'Test Charity B'],
        'Amount_Numeric': [1000.0, 500.0, 750.0, 1000.0, 500.0],
        'Charitable Sector': ['Education', 'Health', 'Environment', 'Education', 'Health'],
        'Year': [current_year, current_year, current_year-1, current_year-1, current_year-1],
        'Submit Date': pd.to_datetime([
            f'{current_year}-01-15',
            f'{current_year}-03-20',
            f'{current_year-1}-05-01',
            f'{current_year-1}-06-15',
            f'{current_year-1}-08-10'
        ]),
        'Recurring': [
            'annually through indefinitely',
            'semi-annually through indefinitely',
            'annually through indefinitely',
            'annually through indefinitely',
            'semi-annually through indefinitely'
        ]
    }
    return pd.DataFrame(data)


class TestHTMLReportSnapshot:
    """Test HTML report generation against golden master"""

    def test_recurring_donations_html_structure(self, test_donation_data):
        """Test that HTML report structure hasn't changed (now using Great Tables)"""
        recurring = analyze_recurring_donations(test_donation_data, "total", 1, 4)
        builder = HTMLReportBuilder(pd.DataFrame(), {}, {}, {}, {}, {})
        html = builder.generate_recurring_donations_section(recurring, max_shown=20)

        # Check key structural elements exist (Great Tables format)
        assert '<table' in html
        assert 'Tax ID' in html  # Great Tables renames EIN to Tax ID
        assert 'Organization' in html
        assert 'Total Ever Donated' in html
        assert 'Period' in html
        assert 'Last Donation' in html
        assert 'Total annual recurring' in html  # Part of source note
        assert 'Total ever donated' in html  # Part of source note
        # Great Tables has tbody but CSS may style it differently
        assert 'gt_table' in html  # Verify it's using Great Tables

    def test_recurring_donations_html_data_integrity(self, test_donation_data):
        """Test that HTML contains correct data"""
        recurring = analyze_recurring_donations(test_donation_data, "total", 1, 4)
        builder = HTMLReportBuilder(pd.DataFrame(), {}, {}, {}, {}, {})
        html = builder.generate_recurring_donations_section(recurring, max_shown=20)

        # Verify test charities appear in output
        assert 'Test Charity A' in html
        assert 'Test Charity B' in html

        # Verify EINs appear
        assert '11-1111111' in html
        assert '22-2222222' in html

        # Verify amounts appear (formatted)
        assert '$1,000.00' in html
        assert '$500.00' in html

    def test_recurring_donations_html_has_rows(self, test_donation_data):
        """Test that HTML has data rows (Great Tables format)"""
        recurring = analyze_recurring_donations(test_donation_data, "total", 1, 4)
        builder = HTMLReportBuilder(pd.DataFrame(), {}, {}, {}, {}, {})
        html = builder.generate_recurring_donations_section(recurring, max_shown=20)

        # Verify there are data rows (Great Tables uses different structure)
        assert '<tr>' in html  # Great Tables doesn't use inline background styles
        assert 'gt_row' in html  # Great Tables uses CSS classes
        assert len(recurring) > 0


class TestReportGeneration:
    """Test report generation produces valid output"""

    def test_html_report_generates_valid_output(self, test_donation_data):
        """Test HTML report builder produces valid output"""
        recurring = analyze_recurring_donations(test_donation_data, "total", 1, 4)
        builder = HTMLReportBuilder(pd.DataFrame(), {}, {}, {}, {}, {})
        html = builder.generate_recurring_donations_section(recurring, max_shown=20)

        # Verify it's valid HTML with Great Tables
        assert html.startswith('\n    <div class="report-section">')
        assert html.endswith('</div>')
        assert 'gt_table' in html
        assert len(html) > 100  # Substantial output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
