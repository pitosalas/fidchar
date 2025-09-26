#!/usr/bin/env python3
"""Comprehensive HTML report generator.

Creates complete HTML reports with all analysis sections.
"""

import pandas as pd
from html_report_builder import (
    generate_html_header_section, generate_table_sections,
    generate_charity_detail_section, generate_donation_history_table
)


def create_comprehensive_html_report(category_totals, yearly_amounts, yearly_counts,
                                   consistent_donors, top_charities, total_amount, df,
                                   one_time, stopped_recurring, charity_details=None,
                                   charity_descriptions=None, graph_info=None):
    """Create a comprehensive HTML report with all tables and analysis"""

    # Calculate summary stats
    total_donations = len(df)
    years_covered = f"{df['Year'].min()} - {df['Year'].max()}"
    one_time_total = one_time["Total_Amount"].sum()
    stopped_total = stopped_recurring["Total_Amount"].sum()
    consistent_total = sum(donor['total_5_year'] for donor in consistent_donors.values())

    # Generate HTML content sections
    html_content = generate_html_header_section(
        total_donations, total_amount, years_covered,
        one_time_total, stopped_total, consistent_total, len(consistent_donors)
    )

    return html_content


def add_table_sections_to_report(html_content, gt_consistent, gt_categories,
                                gt_yearly, gt_top_charities, consistent_total, config=None):
    """Add main data table sections to the report"""
    html_content += generate_table_sections(
        gt_consistent.as_raw_html(),
        gt_categories.as_raw_html(),
        gt_yearly.as_raw_html(),
        gt_top_charities.as_raw_html(),
        consistent_total,
        config
    )
    return html_content


def add_detailed_charity_analysis(html_content, top_charities, charity_details,
                                 charity_descriptions, graph_info):
    """Add detailed analysis section for top 10 charities"""
    html_content += """
    <div class="report-section">
        <h2 class="section-title">Detailed Analysis of Top 10 Charities</h2>
        <p>Complete donation history and trend analysis for each of the top 10 charities:</p>
"""

    for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
        org_donations = charity_details[tax_id]
        description = charity_descriptions.get(tax_id, "No description available")
        has_graph = graph_info.get(tax_id) is not None

        # Add charity detail section
        html_content += generate_charity_detail_section(
            i, tax_id, org_donations, description, has_graph
        )

        # Add donation history table
        html_content += generate_donation_history_table(org_donations)
        html_content += "\n        </div>"

    html_content += """
    </div>
</body>
</html>"""

    return html_content