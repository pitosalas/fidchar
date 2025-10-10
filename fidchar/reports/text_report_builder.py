#!/usr/bin/env python3
"""Text report builder module for charitable donation analysis.

Generates plain text reports with ASCII table formatting.
"""

from datetime import datetime
import tables.table_builder as tab
import reports.formatters as fmt
from reports.base_report_builder import BaseReportBuilder

class TextReportBuilder(BaseReportBuilder):

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set)
        self.formatter = fmt.TextFormatter(builder=self)

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

{tab.create_category_summary_table(category_totals, total_amount)}

Total: ${total_amount:,.2f}

"""
        return section

    def generate_yearly_section(self, yearly_amounts, yearly_counts):
        """Generate the yearly analysis section with inline table"""
        section = f"""YEARLY ANALYSIS
{'-' * 80}

Note: Charts available in images/yearly_amounts.png and images/yearly_counts.png

{tab.create_yearly_analysis_table(yearly_amounts, yearly_counts)}

"""
        return section

    def generate_one_time_section(self, one_time):
        """Generate the one-time donations section with inline table"""
        one_time_table = tab.create_one_time_donations_table(one_time)
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
        stopped_table = tab.create_stopped_recurring_table(stopped_recurring)
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
        # Augment with focus flags
        augmented_charities = self.prepare_top_charities_data(top_charities)
        count = len(top_charities)

        section = f"""TOP {count} CHARITIES BY TOTAL DONATIONS
{'-' * 80}

{tab.create_top_charities_table(augmented_charities)}

"""
        return section

    def generate_charity_detail_section(self, i, tax_id):
        """Generate detailed section for a single charity in text format"""
        data = self.prepare_charity_detail_data(i, tax_id)
        return self.formatter.format_charity_detail_section(data)

    def generate_focus_summary_section(self):
        """Generate focus charities summary section"""
        data = self.prepare_focus_summary_data()
        return self.formatter.format_focus_summary_section(data)

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities):
        """Generate complete text report by combining all sections"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)

        report = self.generate_report_header(total_amount, total_donations)
        for section in self.config.get("sections", {}) :
            section_id, section_options = self.parse_section_config(section)

            if section_id == "exec":
                pass
            elif section_id == "sectors":
                report += self.generate_category_section(category_totals, total_amount)
            elif section_id == "yearly":
                report += self.generate_yearly_section(yearly_amounts, yearly_counts)
            elif section_id == "top_charities":
                report += self.generate_top_charities_section(top_charities)
            elif section_id == "patterns":
                report += self.generate_one_time_section(one_time)
                report += self.generate_stopped_recurring_section(stopped_recurring)
            elif section_id == "focus_summary":
                report += self.generate_focus_summary_section()
            elif section_id == "detailed":
                pass

        report += f"""DETAILED DONATION HISTORY
{'=' * 80}

"""

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            report += self.generate_charity_detail_section(i, tax_id)

        with open("../output/donation_analysis.txt", "w") as f:
            f.write(report)
