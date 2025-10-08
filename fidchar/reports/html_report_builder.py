#!/usr/bin/env python3
"""HTML comprehensive report builder module.

Handles the creation of comprehensive HTML reports with all sections.
"""

import pandas as pd
from datetime import datetime
from reports.base_report_builder import BaseReportBuilder
from reports.formatters import HTMLFormatter
from tables.great_tables_builder import create_gt_recurring_donations_table, create_gt_donation_history_table


def generate_html_header_section(total_donations, total_amount, years_covered,
                                one_time_total, stopped_total, consistent_total,
                                consistent_count):
    """Generate the HTML header and executive summary sections"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Charitable Donation Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 'Fira Sans', 'Droid Sans', Arial, sans-serif;
            line-height: 1.4;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        .report-header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
        }}
        .report-section {{
            margin: 40px 0;
            page-break-inside: avoid;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        .summary-stats {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #333;
            margin: 20px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #333;
        }}
        .summary-box h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #333;
        }}
        .summary-box p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        @media print {{
            body {{ margin: 0; }}
            .report-section {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>Charitable Donation Analysis Report</h1>
        <p><em>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</em></p>
        <div class="summary-stats">
            <strong>Total Donations:</strong> {total_donations:,} donations |
            <strong>Total Amount:</strong> ${total_amount:,.2f} |
            <strong>Years Covered:</strong> {years_covered}
        </div>
    </div>

    <div class="report-section">
        <h2 class="section-title">Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-box">
                <h3>One-Time Donations</h3>
                <p><strong>78 organizations</strong></p>
                <p>Total: ${one_time_total:,.2f}</p>
            </div>
            <div class="summary-box">
                <h3>Stopped Recurring</h3>
                <p><strong>5 organizations</strong></p>
                <p>Total: ${stopped_total:,.2f}</p>
            </div>
            <div class="summary-box">
                <h3>Consistent Donations (5yr)</h3>
                <p><strong>{consistent_count} organizations</strong></p>
                <p>Total: ${consistent_total:,.2f}</p>
            </div>
            <div class="summary-box">
                <h3>Top 10 Charities</h3>
                <p><strong>Major recipients</strong></p>
                <p>Detailed analysis below</p>
            </div>
        </div>
    </div>"""


class HTMLReportBuilder(BaseReportBuilder):
    """HTML report builder with inherited state"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations)
        self.formatter = HTMLFormatter()

    def generate_recurring_donations_section(self, recurring_donations, max_shown=20):
        """Generate HTML for recurring donations section using Great Tables"""
        if recurring_donations.empty:
            return """
    <div class="report-section">
        <h2 class="section-title">Recurring Donations</h2>
        <p>No recurring donations found.</p>
    </div>"""

        gt_table = create_gt_recurring_donations_table(recurring_donations, max_shown)
        if gt_table is None:
            return """
    <div class="report-section">
        <h2 class="section-title">Recurring Donations</h2>
        <p>No recurring donations found.</p>
    </div>"""

        return f"""
    <div class="report-section">
        {gt_table.as_raw_html()}
    </div>"""


def generate_table_sections(gt_consistent_html, gt_categories_html,
                           gt_yearly_html, gt_top_charities_html, consistent_total,
                           recurring_donations, config: dict):
    sections = config.get("sections", {})
    html_content = ""

    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")
        section_options = section.get("options", {}) if isinstance(section, dict) else {}
        if section_id == "sectors":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Donations by Charitable Sector</h2>
        {gt_categories_html}
    </div>"""
        elif section_id == "consistent":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Consistent Donations (Last 5 Years, $500+ Annually)</h2>
        <p>Charities that received donations consistently for the last 5 years with at least $500 per year:</p>
        {gt_consistent_html}
        <p style="margin-top: 15px;"><strong>Total to consistent donations (5 years):</strong> ${consistent_total:,.2f}</p>
    </div>"""
        elif section_id == "yearly":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Yearly Analysis</h2>
        <div style="text-align: center; margin: 20px 0;">
            <img src="images/yearly_amounts.png" alt="Yearly Donation Amounts" style="max-width: 100%; height: auto; margin: 10px;">
            <img src="images/yearly_counts.png" alt="Yearly Donation Counts" style="max-width: 100%; height: auto; margin: 10px;">
        </div>
        {gt_yearly_html}
    </div>"""
        elif section_id == "top_charities":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Top 10 Charities by Total Donations</h2>
        {gt_top_charities_html}
    </div>"""
        elif section_id == "recurring":
            if recurring_donations is not None and not recurring_donations.empty:
                max_shown = section_options.get("max_shown", 20)
                builder = HTMLReportBuilder(pd.DataFrame(), config or {}, {}, {}, {}, {})
                html_content += builder.generate_recurring_donations_section(recurring_donations, max_shown)
        elif section_id == "analysis":
            html_content += """
    <div class="report-section">
        <h2 class="section-title">Strategic Analysis</h2>
        <p>Insights to help you optimize your charitable giving strategy.</p>

        <h3>Efficiency Frontier Analysis</h3>
        <img src="images/efficiency_frontier.png" alt="Efficiency Frontier" style="max-width: 100%; height: auto; margin: 20px 0;">

        <h4>How to read this chart:</h4>
        <ul>
            <li><strong>X-axis (Evaluation Score):</strong> Outstanding×2 + Acceptable - Unacceptable (can be negative)</li>
            <li><strong>Y-axis (Total Donated):</strong> How much you've given to them</li>
            <li>Higher scores (right side) indicate better-performing charities</li>
            <li>Reference lines at 0 and 5 show score thresholds</li>
        </ul>

        <h4>Key Insights:</h4>
        <ul>
            <li><strong>Ideal:</strong> Most of your giving should be to charities with higher scores (≥5)</li>
            <li><strong>Consider:</strong> Are you giving large amounts to lower-rated charities (score <0)?</li>
            <li><strong>Opportunity:</strong> Are there highly-rated charities you could support more?</li>
        </ul>
    </div>"""

    return html_content


def generate_charity_detail_section(i, tax_id, org_donations, description, has_graph, evaluation):
    """Generate detailed section for a single charity - wrapper for comprehensive report"""
    charity_details_dict = {tax_id: org_donations}
    charity_descriptions = {tax_id: description}
    graph_info = {tax_id: True} if has_graph else {}
    charity_evaluations = {tax_id: evaluation}

    builder = HTMLReportBuilder(pd.DataFrame(), {}, charity_details_dict, charity_descriptions, graph_info, charity_evaluations)
    formatter = HTMLFormatter()

    data = builder.prepare_charity_detail_data(i, tax_id)

    return f"""
        <div style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px;">
            {formatter.format_charity_detail_section(data)}
        </div>"""


def generate_donation_history_table(org_donations):
    """Generate scrollable donation history table using Great Tables"""
    org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
    gt_table = create_gt_donation_history_table(org_donations, org_name)

    return f"""
            <h4 style="color: #333; margin-bottom: 10px;">Complete Donation History</h4>
            {gt_table.as_raw_html()}"""