#!/usr/bin/env python3
"""Text report builder module for charitable donation analysis.

Generates plain text reports with ASCII table formatting.
"""

import pandas as pd
from datetime import datetime
from tables.table_builder import (
    create_category_summary_table, create_yearly_analysis_table,
    create_one_time_donations_table, create_stopped_recurring_table,
    create_top_charities_table, create_donation_history_table,
    create_consistent_donors_table
)


def generate_text_report_header(df, total_amount, total_donations):
    """Generate the text report header section"""
    report = f"""CHARITABLE DONATION ANALYSIS REPORT
{'=' * 80}

Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

SUMMARY
{'-' * 80}
Total Donations:  {total_donations:,} donations
Total Amount:     ${total_amount:,.2f}
Years Covered:    {df['Year'].min()} - {df['Year'].max()}

"""
    return report


def generate_text_category_section(category_totals, total_amount):
    """Generate the category analysis section with inline table"""
    section = f"""DONATIONS BY CHARITABLE SECTOR
{'-' * 80}

{create_category_summary_table(category_totals, total_amount)}

Total: ${total_amount:,.2f}

"""
    return section


def generate_text_yearly_section(yearly_amounts, yearly_counts):
    """Generate the yearly analysis section with inline table"""
    section = f"""YEARLY ANALYSIS
{'-' * 80}

Note: Charts available in images/yearly_amounts.png and images/yearly_counts.png

{create_yearly_analysis_table(yearly_amounts, yearly_counts)}

"""
    return section


def generate_text_one_time_section(one_time):
    """Generate the one-time donations section with inline table"""
    one_time_table = create_one_time_donations_table(one_time)
    one_time_total = one_time["Total_Amount"].sum()

    section = f"""ONE-TIME DONATIONS
{'-' * 80}

Organizations that received a single donation ({len(one_time)} organizations):

{one_time_table}
"""

    if len(one_time) > 20:
        section += f"\n... and {len(one_time) - 20} more organizations\n"

    section += f"\nOne-time donations total: ${one_time_total:,.2f}\n\n"

    return section


def generate_text_stopped_recurring_section(stopped_recurring):
    """Generate the stopped recurring donations section with inline table"""
    stopped_table = create_stopped_recurring_table(stopped_recurring)
    stopped_total = stopped_recurring["Total_Amount"].sum()

    section = f"""STOPPED RECURRING DONATIONS
{'-' * 80}

Organizations with recurring donations that appear to have stopped ({len(stopped_recurring)} organizations):

{stopped_table}
"""

    if len(stopped_recurring) > 15:
        section += f"\n... and {len(stopped_recurring) - 15} more organizations\n"

    section += f"\nStopped recurring donations total: ${stopped_total:,.2f}\n\n"

    return section


def generate_text_top_charities_section(top_charities):
    """Generate the top charities ranking section with inline table"""
    section = f"""TOP 10 CHARITIES BY TOTAL DONATIONS
{'-' * 80}

{create_top_charities_table(top_charities)}

"""
    return section


def generate_text_consistent_donors_section(consistent_donors):
    """Generate the consistent donors section with inline table"""
    if not consistent_donors:
        section = f"""CONSISTENT DONORS (LAST 5 YEARS, $500+ ANNUALLY)
{'-' * 80}

No charities meet the criteria for consistent donations over the last 5 years.

"""
        return section

    section = f"""CONSISTENT DONORS (LAST 5 YEARS, $500+ ANNUALLY)
{'-' * 80}

Charities that received donations consistently for the last 5 years with at least
$500 per year ({len(consistent_donors)} organizations):

{create_consistent_donors_table(consistent_donors)}

"""

    total_consistent = sum(donor['total_5_year'] for donor in consistent_donors.values())
    section += f"Total to consistent donors (5 years): ${total_consistent:,.2f}\n\n"

    return section


def generate_text_charity_detail_section(i, tax_id, charity_details, charity_descriptions, graph_info, charity_evaluations):
    """Generate detailed section for a single charity in text format"""
    org_donations = charity_details[tax_id]
    org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
    sector = org_donations["Charitable Sector"].iloc[0] if pd.notna(org_donations["Charitable Sector"].iloc[0]) else "N/A"
    description = charity_descriptions.get(tax_id, "No description available")

    section = f"""{i}. {org_name}
{'-' * 80}
Tax ID:              {tax_id}
Sector:              {sector}
Total Donated:       ${org_donations['Amount_Numeric'].sum():,.2f}
Number of Donations: {len(org_donations)}
"""

    has_graph = graph_info.get(tax_id) is not None
    if has_graph:
        graph_filename = f"images/charity_{i:02d}_{tax_id.replace('-', '')}.png"
        section += f"10-Year Trend:       {graph_filename}\n"
    else:
        section += f"10-Year Trend:       No donations in last 10 years\n"

    if description and description != "API credentials not configured":
        desc_short = description[:150] + "..." if len(description) > 150 else description
        section += f"\n{desc_short}\n"

    evaluation = charity_evaluations.get(tax_id)
    if evaluation:
        section += f"\nCharity Evaluation:\n"
        section += f"  Outstanding:    {evaluation.outstanding_count} metrics\n"
        section += f"  Acceptable:     {evaluation.acceptable_count} metrics\n"
        section += f"  Unacceptable:   {evaluation.unacceptable_count} metrics\n"
        section += f"\n{evaluation.summary}\n\n"

    return section


def generate_text_report(category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring,
                        top_charities, charity_details, charity_descriptions, graph_info, consistent_donors,
                        charity_evaluations, config):
    """Generate complete text report by combining all sections"""
    total_amount = category_totals.sum()
    total_donations = len(df)

    report = generate_text_report_header(df, total_amount, total_donations)

    default_sections = [
        {"name": "exec"}, {"name": "sectors"}, {"name": "consistent"},
        {"name": "yearly"}, {"name": "top_charities"}, {"name": "patterns"}, {"name": "detailed"}
    ]
    sections = config.get("sections", default_sections)

    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")
        if section_id == "exec":
            pass
        elif section_id == "sectors":
            report += generate_text_category_section(category_totals, total_amount)
        elif section_id == "consistent":
            report += generate_text_consistent_donors_section(consistent_donors)
        elif section_id == "yearly":
            report += generate_text_yearly_section(yearly_amounts, yearly_counts)
        elif section_id == "top_charities":
            report += generate_text_top_charities_section(top_charities)
        elif section_id == "patterns":
            report += generate_text_one_time_section(one_time)
            report += generate_text_stopped_recurring_section(stopped_recurring)
        elif section_id == "detailed":
            pass

    report += f"""DETAILED DONATION HISTORY
{'=' * 80}

"""

    for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
        report += generate_text_charity_detail_section(i, tax_id, charity_details, charity_descriptions, graph_info, charity_evaluations)

    with open("../output/donation_analysis.txt", "w") as f:
        f.write(report)
