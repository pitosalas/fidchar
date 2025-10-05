#!/usr/bin/env python3
"""HTML comprehensive report builder module.

Handles the creation of comprehensive HTML reports with all sections.
"""

import pandas as pd
from datetime import datetime


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
                <h3>Consistent Donors (5yr)</h3>
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


def generate_table_sections(gt_consistent_html, gt_categories_html,
                           gt_yearly_html, gt_top_charities_html, consistent_total, config=None):
    """Generate the main table sections in config-specified order"""

    # Get section order from config, default to standard order if not provided
    default_sections = [
        {"name": "sectors"}, {"name": "consistent"}, {"name": "yearly"}, {"name": "top_charities"}
    ]
    sections = config.get("sections", default_sections) if config else default_sections

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
        <h2 class="section-title">Consistent Donors (Last 5 Years, $500+ Annually)</h2>
        <p>Charities that received donations consistently for the last 5 years with at least $500 per year:</p>
        {gt_consistent_html}
        <p style="margin-top: 15px;"><strong>Total to consistent donors (5 years):</strong> ${consistent_total:,.2f}</p>
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

    return html_content


def generate_charity_detail_section(i, tax_id, org_donations, description, has_graph, evaluation):
    """Generate detailed section for a single charity"""
    org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
    sector = org_donations["Charitable Sector"].iloc[0] if pd.notna(org_donations["Charitable Sector"].iloc[0]) else "N/A"
    graph_filename = f"images/charity_{i:02d}_{tax_id.replace('-', '')}.png"

    html_content = f"""
        <div style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px;">
            <h3 style="color: #333; margin-bottom: 15px;">{i}. {org_name}</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px;">
                <div>
                    <p><strong>Tax ID:</strong> {tax_id}</p>
                    <p><strong>Sector:</strong> {sector}</p>
                    <p><strong>Total Donated:</strong> ${org_donations['Amount_Numeric'].sum():,.2f}</p>
                    <p><strong>Number of Donations:</strong> {len(org_donations)}</p>
                </div>"""

    if has_graph:
        html_content += f"""
                <div style="text-align: center;">
                    <img src="{graph_filename}" alt="10-year trend for {org_name}" style="max-width: 100%; height: auto;">
                    <p style="font-size: 12px; color: #666; margin-top: 5px;">10-Year Donation Trend</p>
                </div>"""
    else:
        html_content += f"""
                <div style="text-align: center; padding: 40px; background: #f8f9fa; border-radius: 5px;">
                    <p style="color: #666; font-style: italic;">No donations in last 10 years</p>
                </div>"""

    html_content += """
            </div>"""

    # Description if available
    if description and description != "API credentials not configured":
        desc_short = description[:200] + "..." if len(description) > 200 else description
        html_content += f"""
            <p style="font-style: italic; color: #555; margin-bottom: 15px;">{desc_short}</p>"""

    # Charity evaluation if available
    if evaluation:
        html_content += f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h4 style="margin-top: 0;">Charity Evaluation</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                    <div>⭐ Outstanding: {evaluation.outstanding_count}</div>
                    <div>✓ Acceptable: {evaluation.acceptable_count}</div>
                    <div>⚠ Unacceptable: {evaluation.unacceptable_count}</div>
                </div>
                <p style="margin-top: 10px; font-style: italic; color: #555;">{evaluation.summary}</p>
            </div>"""

    return html_content


def generate_donation_history_table(org_donations):
    """Generate scrollable donation history table"""
    html_content = f"""
            <h4 style="color: #333; margin-bottom: 10px;">Complete Donation History</h4>
            <div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 3px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <thead style="background: #f8f9fa; position: sticky; top: 0;">
                        <tr>
                            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Date</th>
                            <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>"""

    for _, donation in org_donations.iterrows():
        date_str = donation["Submit Date"].strftime("%m/%d/%Y")
        amount_str = f"${donation['Amount_Numeric']:,.2f}"
        html_content += f"""
                        <tr>
                            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">{date_str}</td>
                            <td style="padding: 6px 8px; text-align: right; border-bottom: 1px solid #eee;">{amount_str}</td>
                        </tr>"""

    html_content += """
                    </tbody>
                </table>
            </div>"""

    return html_content