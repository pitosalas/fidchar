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
from reports.base_report_builder import BaseReportBuilder
from reports.formatters import TextFormatter


class TextReportBuilder(BaseReportBuilder):
    """Text report builder with inherited state"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations)
        self.formatter = TextFormatter()

    def generate_report_header(self, total_amount, total_donations):
        """Generate the text report header section"""
        report = f"""CHARITABLE DONATION ANALYSIS REPORT
{'=' * 80}

Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

SUMMARY
{'-' * 80}
Total Donations:  {total_donations:,} donations
Total Amount:     ${total_amount:,.2f}
Years Covered:    {self.df['Year'].min()} - {self.df['Year'].max()}

"""
        return report

    def generate_category_section(self, category_totals, total_amount):
        """Generate the category analysis section with inline table"""
        section = f"""DONATIONS BY CHARITABLE SECTOR
{'-' * 80}

{create_category_summary_table(category_totals, total_amount)}

Total: ${total_amount:,.2f}

"""
        return section

    def generate_yearly_section(self, yearly_amounts, yearly_counts):
        """Generate the yearly analysis section with inline table"""
        section = f"""YEARLY ANALYSIS
{'-' * 80}

Note: Charts available in images/yearly_amounts.png and images/yearly_counts.png

{create_yearly_analysis_table(yearly_amounts, yearly_counts)}

"""
        return section

    def generate_one_time_section(self, one_time):
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

    def generate_stopped_recurring_section(self, stopped_recurring):
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

    def generate_top_charities_section(self, top_charities):
        """Generate the top charities ranking section with inline table"""
        section = f"""TOP 10 CHARITIES BY TOTAL DONATIONS
{'-' * 80}

{create_top_charities_table(top_charities)}

"""
        return section

    def generate_consistent_donors_section(self, consistent_donors):
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

    def generate_recurring_donations_section(self, recurring_donations, max_shown=20):
        """Generate the recurring donations section with inline table"""
        data = self.prepare_recurring_data(recurring_donations, max_shown)
        return self.formatter.format_recurring_section(data)

    def generate_charity_detail_section(self, i, tax_id):
        """Generate detailed section for a single charity in text format"""
        data = self.prepare_charity_detail_data(i, tax_id)
        return self.formatter.format_charity_detail_section(data)

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities, consistent_donors, recurring_donations):
        """Generate complete text report by combining all sections"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)

        report = self.generate_report_header(total_amount, total_donations)

        sections = self.get_section_order()

        for section in sections:
            section_id, section_options = self.parse_section_config(section)

            if section_id == "exec":
                pass
            elif section_id == "sectors":
                report += self.generate_category_section(category_totals, total_amount)
            elif section_id == "consistent":
                report += self.generate_consistent_donors_section(consistent_donors)
            elif section_id == "yearly":
                report += self.generate_yearly_section(yearly_amounts, yearly_counts)
            elif section_id == "top_charities":
                report += self.generate_top_charities_section(top_charities)
            elif section_id == "patterns":
                report += self.generate_one_time_section(one_time)
                report += self.generate_stopped_recurring_section(stopped_recurring)
            elif section_id == "recurring":
                max_shown = section_options.get("max_shown", 20)
                report += self.generate_recurring_donations_section(recurring_donations, max_shown)
            elif section_id == "detailed":
                pass

        report += f"""DETAILED DONATION HISTORY
{'=' * 80}

"""

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            report += self.generate_charity_detail_section(i, tax_id)

        with open("../output/donation_analysis.txt", "w") as f:
            f.write(report)
