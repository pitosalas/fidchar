#!/usr/bin/env python3
"""Report builder module for charitable donation analysis.

Orchestrates the creation of the complete markdown report.
"""

import pandas as pd
from datetime import datetime
from table_builder import (
    create_category_summary_table, create_yearly_analysis_table,
    create_one_time_donations_table, create_stopped_recurring_table,
    create_top_charities_table, create_donation_history_table,
    create_consistent_donors_table
)
from great_tables_builder import save_all_gt_tables


def generate_report_header(df, total_amount, total_donations):
    """Generate the report header section"""
    report = f"""# Charitable Donation Analysis Report

*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

## Summary

- **Total Donations:** {total_donations:,} donations
- **Total Amount:** ${total_amount:,.2f}
- **Years Covered:** {df['Year'].min()} - {df['Year'].max()}

"""
    return report


def generate_category_section(category_totals, total_amount, html_files=None):
    """Generate the category analysis section"""
    section = """## Donations by Charitable Sector

"""

    section += f"[View Category Analysis Table]({html_files['categories']})\n\n"

    section += f"**Total:** ${total_amount:,.2f}\n\n"

    return section


def generate_yearly_section(yearly_amounts, yearly_counts, html_files=None):
    """Generate the yearly analysis section"""
    section = """## Yearly Analysis

### Total Donation Amounts by Year

![Yearly Amounts](yearly_amounts.png)

"""

    section += f"[View Yearly Analysis Table]({html_files['yearly']})\n\n"

    section += "\n### Number of Donations by Year\n\n![Yearly Counts](yearly_counts.png)\n"

    return section


def generate_one_time_section(one_time):
    """Generate the one-time donations section"""
    one_time_table = create_one_time_donations_table(one_time)
    one_time_total = one_time["Total_Amount"].sum()

    section = f"\n## One-Time Donations\n\n"
    section += f"Organizations that received a single donation ({len(one_time)} organizations):\n\n"
    section += one_time_table

    if len(one_time) > 20:
        section += f"\n*... and {len(one_time) - 20} more organizations*\n"

    section += f"\n**One-time donations total:** ${one_time_total:,.2f}\n"

    return section


def generate_stopped_recurring_section(stopped_recurring):
    """Generate the stopped recurring donations section"""
    stopped_table = create_stopped_recurring_table(stopped_recurring)
    stopped_total = stopped_recurring["Total_Amount"].sum()

    section = f"\n## Stopped Recurring Donations\n\n"
    section += f"Organizations with recurring donations that appear to have stopped ({len(stopped_recurring)} organizations):\n\n"
    section += stopped_table

    if len(stopped_recurring) > 15:
        section += f"\n*... and {len(stopped_recurring) - 15} more organizations*\n"

    section += f"\n**Stopped recurring donations total:** ${stopped_total:,.2f}\n"

    return section


def generate_top_charities_section(top_charities, html_files=None):
    """Generate the top charities ranking section"""
    section = f"\n## Top 10 Charities by Total Donations\n\n"

    section += f"[View Top Charities Table]({html_files['top_charities']})\n\n"

    return section


def generate_consistent_donors_section(consistent_donors, html_files=None):
    """Generate the consistent donors section"""
    if not consistent_donors:
        section = f"\n## Consistent Donors (Last 5 Years, $500+ Annually)\n\n"
        section += "No charities meet the criteria for consistent donations over the last 5 years.\n"
        return section

    section = f"\n## Consistent Donors (Last 5 Years, $500+ Annually)\n\n"
    section += f"Charities that received donations consistently for the last 5 years with at least $500 per year ({len(consistent_donors)} organizations):\n\n"

    section += f"[View Consistent Donors Table]({html_files['consistent']})\n\n"

    total_consistent = sum(donor['total_5_year'] for donor in consistent_donors.values())
    section += f"**Total to consistent donors (5 years):** ${total_consistent:,.2f}\n"

    return section


def generate_charity_detail_section(i, tax_id, charity_details, charity_descriptions, graph_info):
    """Generate detailed section for a single charity"""
    org_donations = charity_details[tax_id]
    org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
    sector = org_donations["Charitable Sector"].iloc[0] if pd.notna(org_donations["Charitable Sector"].iloc[0]) else "N/A"
    description = charity_descriptions.get(tax_id, "No description available")

    # Generate graph filename
    graph_filename = f"charity_{i:02d}_{tax_id.replace('-', '')}.png"

    # Create two-column layout: detailed info | mini graph
    section = f"#### {i}. {org_name}\n\n"

    # Check if graph exists for this charity
    has_graph = graph_info.get(tax_id) is not None

    # Two-column table: detailed info in first column, graph in second
    if has_graph:
        section += f"| Charity Details | 10-Year Trend |\n"
        section += f"|:----------------|:-------------:|\n"
        section += f"| **Tax ID:** {tax_id}<br>**Sector:** {sector}<br>**Total Donated:** ${org_donations['Amount_Numeric'].sum():,.2f}<br>**Number of Donations:** {len(org_donations)} | ![10-year trend]({graph_filename}) |\n\n"
    else:
        # No graph - just show info in single column
        section += f"| Charity Details |\n"
        section += f"|:----------------|\n"
        section += f"| **Tax ID:** {tax_id}<br>**Sector:** {sector}<br>**Total Donated:** ${org_donations['Amount_Numeric'].sum():,.2f}<br>**Number of Donations:** {len(org_donations)}<br>*No donations in last 10 years* |\n\n"

    # Description on separate line if available
    if description and description != "API credentials not configured":
        desc_short = description[:150] + "..." if len(description) > 150 else description
        section += f"*{desc_short}*\n\n"

    # Complete donation history
    donation_history_table = create_donation_history_table(org_donations)
    section += "**Complete Donation History:**\n\n"
    section += donation_history_table
    section += "\n"

    return section


def generate_markdown_report(category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring,
                           top_charities, charity_details, charity_descriptions, graph_info, consistent_donors, config=None):
    """Generate complete markdown report by combining all sections"""
    total_amount = category_totals.sum()
    total_donations = len(df)

    # Generate Great Tables HTML files
    print("Generating Great Tables HTML files...")
    html_files = save_all_gt_tables(category_totals, yearly_amounts, yearly_counts,
                                   consistent_donors, top_charities, total_amount,
                                   df, one_time, stopped_recurring, charity_details,
                                   charity_descriptions, graph_info)

    if not html_files:
        raise RuntimeError("Failed to generate Great Tables HTML files")

    # Build report section by section using config ordering
    report = generate_report_header(df, total_amount, total_donations)

    # Get section order from config, default to all sections if not provided
    default_sections = [
        {"name": "exec"}, {"name": "sectors"}, {"name": "consistent"},
        {"name": "yearly"}, {"name": "top_charities"}, {"name": "patterns"}, {"name": "detailed"}
    ]
    sections = config.get("sections", default_sections) if config else default_sections

    # Generate sections in the specified order
    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")
        section_options = section.get("options", {}) if isinstance(section, dict) else {}
        if section_id == "exec":
            # Executive Summary is already included in header
            pass
        elif section_id == "sectors":
            report += generate_category_section(category_totals, total_amount, html_files)
        elif section_id == "consistent":
            report += generate_consistent_donors_section(consistent_donors, html_files)
        elif section_id == "yearly":
            report += generate_yearly_section(yearly_amounts, yearly_counts, html_files)
        elif section_id == "top_charities":
            report += generate_top_charities_section(top_charities, html_files)
        elif section_id == "patterns":
            report += generate_one_time_section(one_time)
            report += generate_stopped_recurring_section(stopped_recurring)
        elif section_id == "detailed":
            pass  # Detailed analysis added after the loop

    # Add detailed sections for each top charity
    report += "\n### Detailed Donation History\n\n"

    for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
        report += generate_charity_detail_section(i, tax_id, charity_details, charity_descriptions, graph_info)

    with open("../output/donation_analysis.md", "w") as f:
        f.write(report)

    print(f"HTML tables generated: {list(html_files.values())}")