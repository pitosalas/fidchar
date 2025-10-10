#!/usr/bin/env python3
"""Report builder module for charitable donation analysis.

Orchestrates the creation of the complete markdown report.
"""

from datetime import datetime
from tables.table_builder import (
    create_category_summary_table, create_yearly_analysis_table,
    create_one_time_donations_table, create_stopped_recurring_table,
    create_top_charities_table
)
from reports.base_report_builder import BaseReportBuilder
from reports.formatters import MarkdownFormatter


class MarkdownReportBuilder(BaseReportBuilder):
    """Markdown report builder with inherited state"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set)
        self.formatter = MarkdownFormatter(builder=self)

    def generate_report_header(self, total_amount, total_donations):
        """Generate the report header section"""
        report = f"""# Charitable Donation Analysis Report

*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

## Summary

- **Total Donations:** {total_donations:,} donations
- **Total Amount:** ${total_amount:,.2f}
- **Years Covered:** {self.df['Year'].min()} - {self.df['Year'].max()}

"""
        return report

    def generate_category_section(self, category_totals, total_amount):
        """Generate the category analysis section"""
        section = """## Donations by Charitable Sector

"""
        category_table = create_category_summary_table(category_totals, total_amount)
        section += f"{category_table}\n\n"
        section += f"**Total:** ${total_amount:,.2f}\n\n"

        return section

    def generate_yearly_section(self, yearly_amounts, yearly_counts):
        """Generate the yearly analysis section"""
        section = """## Yearly Analysis

### Total Donation Amounts by Year

![Yearly Amounts](images/yearly_amounts.png)

"""
        yearly_table = create_yearly_analysis_table(yearly_amounts, yearly_counts)
        section += f"{yearly_table}\n\n"
        section += "\n### Number of Donations by Year\n\n![Yearly Counts](images/yearly_counts.png)\n\n"

        return section

    def generate_one_time_section(self, one_time):
        """Generate the one-time donations section"""
        one_time_table = create_one_time_donations_table(one_time)
        one_time_total = one_time["Total_Amount"].sum()
        section = "\n## One-Time Donations\n\n"
        section += f"Organizations that received a single donation ({len(one_time)} organizations):\n\n"
        section += one_time_table

        if len(one_time) > 20:
            section += f"\n*... and {len(one_time) - 20} more organizations*\n"

        section += f"\n**One-time donations total:** ${one_time_total:,.2f}\n"

        return section

    def generate_stopped_recurring_section(self, stopped_recurring):
        """Generate the stopped recurring donations section"""
        stopped_table = create_stopped_recurring_table(stopped_recurring)
        stopped_total = stopped_recurring["Total_Amount"].sum()
        section = "\n## Stopped Recurring Donations\n\n"
        section += f"Organizations with recurring donations that appear to have stopped ({len(stopped_recurring)} organizations):\n\n"
        section += stopped_table

        if len(stopped_recurring) > 15:
            section += f"\n*... and {len(stopped_recurring) - 15} more organizations*\n"

        section += f"\n**Stopped recurring donations total:** ${stopped_total:,.2f}\n"

        return section

    def generate_top_charities_section(self, top_charities):
        """Generate the top charities ranking section"""
        # Augment with focus flags
        augmented_charities = self.prepare_top_charities_data(top_charities)
        count = len(top_charities)

        section = f"\n## Top {count} Charities by Total Donations\n\n"
        top_charities_table = create_top_charities_table(augmented_charities)
        section += f"{top_charities_table}\n\n"

        return section

    def generate_charity_detail_section(self, i, tax_id):
        """Generate detailed section for a single charity"""
        data = self.prepare_charity_detail_data(i, tax_id)
        return self.formatter.format_charity_detail_section(data)

    def generate_focus_charities_section(self):
        rows = self.build_focus_rows()
        if not rows:
            return "\n## Focus Charities\n\nNo focus charities identified.\n"
        section = "\n## Focus Charities\n\nCharities flagged as strategic focus (from evaluation):\n\n"
        section += "| EIN | Organization | Sector | Years | Period | Total Donated | Alignment |\n"
        section += "|:----|:-------------|:-------|------:|:------:|-------------:|----------:|\n"
        for r in rows:
            align_disp = r['alignment_score'] if r['alignment_score'] is not None else '—'
            org_name = r['organization'] + " **[FOCUS]**"
            section += f"| {r['ein']} | {org_name} | {r['sector']} | {r['years_supported']} | {r['period']} | ${r['total_donated']:,.2f} | {align_disp} |\n"
        return section

    def generate_focus_summary_section(self):
        """Generate focus charities summary section"""
        data = self.prepare_focus_summary_data()
        return self.formatter.format_focus_summary_section(data)

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities):
        """Generate complete markdown report by combining all sections"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)

        report = self.generate_report_header(total_amount, total_donations)

        sections = self.config.get("sections", {})

        # Auto-insert focus section after top_charities if focus charities exist and not explicitly listed
        if not any((s.get('name') if isinstance(s, dict) else s) == 'focus' for s in sections):
            if self.get_focus_charities():
                augmented = []
                for s in sections:
                    augmented.append(s)
                    sid = s.get('name') if isinstance(s, dict) else s
                    if sid == 'top_charities':
                        augmented.append({'name': 'focus'})
                sections = augmented

        for section in sections:
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
            elif section_id == "focus":
                report += self.generate_focus_charities_section()
            elif section_id == "focus_summary":
                report += self.generate_focus_summary_section()
            elif section_id == "detailed":
                pass

        report += "\n### Detailed Donation History\n\n"

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            report += self.generate_charity_detail_section(i, tax_id)

        with open("../output/donation_analysis.md", "w") as f:
            f.write(report)
