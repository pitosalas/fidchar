#!/usr/bin/env python3
"""HTML comprehensive report builder module.

Handles the creation of comprehensive HTML reports with all sections.
"""

import pandas as pd
from datetime import datetime
import reports.base_report_builder as brb
import reports.formatters as fmt


def generate_html_header_section(total_donations, total_amount, years_covered,
                                one_time_total, stopped_total, top_charities_count):
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
                <h3>Top {top_charities_count} Charities</h3>
                <p><strong>Major recipients</strong></p>
                <p>Detailed analysis below</p>
            </div>
        </div>
    </div>"""


class HTMLReportBuilder(brb.BaseReportBuilder):
    """HTML report builder with inherited state"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set)
        self.formatter = fmt.HTMLFormatter(builder=self)

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities):
        """Generate complete HTML report by combining all sections"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)
        years_covered = f"{self.df['Year'].min()} - {self.df['Year'].max()}"
        one_time_total = one_time["Total_Amount"].sum()
        stopped_total = stopped_recurring["Total_Amount"].sum()

        # Augment data with focus flags
        augmented_charities = self.prepare_top_charities_data(top_charities)
        top_charities_count = len(top_charities)

        html_content = generate_html_header_section(
            total_donations, total_amount, years_covered,
            one_time_total, stopped_total, top_charities_count
        )

        # Generate HTML tables using formatter
        categories_html = self.formatter.format_category_table(category_totals, total_amount)
        yearly_html = self.formatter.format_yearly_table(yearly_amounts, yearly_counts)
        top_charities_html = self.formatter.format_top_charities_table(augmented_charities)

        html_content += generate_table_sections(
            categories_html,
            yearly_html,
            top_charities_html,
            one_time,
            stopped_recurring,
            self.config,
            self.charity_evaluations,
            self,
            top_charities_count
        )

        html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Detailed Analysis of Top {top_charities_count} Charities</h2>
        <p>Complete donation history and trend analysis for each of the top {top_charities_count} charities:</p>
"""

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            org_donations = self.charity_details[tax_id]
            description = self.charity_descriptions.get(tax_id, "No description available")
            has_graph = self.graph_info.get(tax_id) is not None
            evaluation = self.charity_evaluations.get(tax_id)

            html_content += generate_charity_detail_section(
                i, tax_id, org_donations, description, has_graph, evaluation
            )
            html_content += "\n        </div>"

        html_content += """
    </div>
</body>
</html>"""

        with open("../output/donation_analysis.html", "w") as f:
            f.write(html_content)


def generate_table_sections(categories_html, yearly_html, top_charities_html,
                           one_time, stopped_recurring, config: dict,
                           charity_evaluations=None, builder=None, top_charities_count=10):
    sections = config.get("sections", {})
    html_content = ""

    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")
        section_options = section.get("options", {}) if isinstance(section, dict) else {}
        if section_id == "sectors":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Donations by Charitable Sector</h2>
        {categories_html}
    </div>"""
        elif section_id == "yearly":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Yearly Analysis</h2>
        <div style="text-align: center; margin: 20px 0;">
            <img src="images/yearly_amounts.png" alt="Yearly Donation Amounts" style="max-width: 100%; height: auto; margin: 10px;">
            <img src="images/yearly_counts.png" alt="Yearly Donation Counts" style="max-width: 100%; height: auto; margin: 10px;">
        </div>
        {yearly_html}
    </div>"""
        elif section_id == "top_charities":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Top {top_charities_count} Charities by Total Donations</h2>
        {top_charities_html}
    </div>"""
        elif section_id == "patterns":
            if builder:
                one_time_table = builder.formatter.format_one_time_table(one_time)
                one_time_total = one_time["Total_Amount"].sum()
                one_time_count = len(one_time)
                overflow_one_time = max(0, one_time_count - 20)

                stopped_table = builder.formatter.format_stopped_recurring_table(stopped_recurring)
                stopped_total = stopped_recurring["Total_Amount"].sum()
                stopped_count = len(stopped_recurring)
                overflow_stopped = max(0, stopped_count - 15)

                html_content += f"""
    <div class="report-section">
        <h2 class="section-title">One-Time Donations</h2>
        <p>Organizations that received a single donation ({one_time_count} organizations):</p>
        {one_time_table}"""
                if overflow_one_time > 0:
                    html_content += f"""
        <p><em>... and {overflow_one_time} more organizations</em></p>"""
                html_content += f"""
        <p style="margin-top: 15px;"><strong>One-time donations total:</strong> ${one_time_total:,.2f}</p>
    </div>

    <div class="report-section">
        <h2 class="section-title">Stopped Recurring Donations</h2>
        <p>Organizations with recurring donations that appear to have stopped ({stopped_count} organizations):</p>
        {stopped_table}"""
                if overflow_stopped > 0:
                    html_content += f"""
        <p><em>... and {overflow_stopped} more organizations</em></p>"""
                html_content += f"""
        <p style="margin-top: 15px;"><strong>Stopped recurring donations total:</strong> ${stopped_total:,.2f}</p>
    </div>"""
        elif section_id == "focus_summary":
            if builder:
                data = builder.prepare_focus_summary_data()
                html_content += builder.formatter.format_focus_summary_section(data)

    return html_content


def generate_charity_detail_section(i, tax_id, org_donations, description, has_graph, evaluation):
    """Generate detailed section for a single charity - wrapper for comprehensive report"""
    charity_details_dict = {tax_id: org_donations}
    charity_descriptions = {tax_id: description}
    graph_info = {tax_id: True} if has_graph else {}
    charity_evaluations = {tax_id: evaluation}

    builder = HTMLReportBuilder(pd.DataFrame(), {}, charity_details_dict, charity_descriptions, graph_info, charity_evaluations)
    data = builder.prepare_charity_detail_data(i, tax_id)

    return f"""
        <div style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px;">
            {builder.formatter.format_charity_detail_section(data)}
        </div>"""


def generate_donation_history_table(org_donations):
    """Generate scrollable donation history table using Great Tables"""
    org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
    gt_table = gtb.create_gt_donation_history_table(org_donations, org_name)

    return f"""
            <h4 style="color: #333; margin-bottom: 10px;">Complete Donation History</h4>
            {gt_table.as_raw_html()}"""