#!/usr/bin/env python3
"""Report builder module for charitable donation analysis.

Orchestrates the creation of the complete markdown report.
"""

from datetime import datetime
from tables.table_builder import (
    create_category_summary_table, create_yearly_analysis_table,
    create_one_time_donations_table, create_stopped_recurring_table,
    create_top_charities_table,
    create_consistent_donors_table
)
from tables.great_tables_builder import save_all_gt_tables
from reports.base_report_builder import BaseReportBuilder
from reports.formatters import MarkdownFormatter


class MarkdownReportBuilder(BaseReportBuilder):
    """Markdown report builder with inherited state"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set)
        self.formatter = MarkdownFormatter()

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

    def generate_category_section(self, category_totals, total_amount, html_files):
        """Generate the category analysis section"""
        section = """## Donations by Charitable Sector

"""

        if html_files:
            section += f"[View Category Analysis Table]({html_files['categories']})\n\n"
        else:
            category_table = create_category_summary_table(category_totals, total_amount)
            section += f"{category_table}\n\n"

        section += f"**Total:** ${total_amount:,.2f}\n\n"

        return section

    def generate_yearly_section(self, yearly_amounts, yearly_counts, html_files):
        """Generate the yearly analysis section"""
        section = """## Yearly Analysis

### Total Donation Amounts by Year

![Yearly Amounts](images/yearly_amounts.png)

"""

        if html_files:
            section += f"[View Yearly Analysis Table]({html_files['yearly']})\n\n"
        else:
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

    def generate_top_charities_section(self, top_charities, html_files):
        """Generate the top charities ranking section"""
        # Augment with focus flags
        augmented_charities = self.prepare_top_charities_data(top_charities)

        section = "\n## Top 10 Charities by Total Donations\n\n"

        if html_files:
            section += f"[View Top Charities Table]({html_files['top_charities']})\n\n"
        else:
            top_charities_table = create_top_charities_table(augmented_charities)
            section += f"{top_charities_table}\n\n"

        return section

    def generate_consistent_donors_section(self, consistent_donors, html_files):
        """Generate the consistent donations section"""
        if not consistent_donors:
            section = "\n## Consistent Donations (Last 5 Years, $500+ Annually)\n\n"
            section += "No charities meet the criteria for consistent donations over the last 5 years.\n"
            return section

        # Augment with focus flags
        augmented_donors = self.prepare_consistent_donors_data(consistent_donors)

        section = "\n## Consistent Donations (Last 5 Years, $500+ Annually)\n\n"
        section += f"Charities that received donations consistently for the last 5 years with at least $500 per year ({len(augmented_donors)} organizations):\n\n"

        if html_files:
            section += f"[View Consistent Donations Table]({html_files['consistent']})\n\n"
        else:
            consistent_table = create_consistent_donors_table(augmented_donors)
            section += f"{consistent_table}\n\n"

        total_consistent = sum(donor['total_5_year'] for donor in augmented_donors.values())
        section += f"**Total to consistent donors (5 years):** ${total_consistent:,.2f}\n"

        return section

    def generate_recurring_donations_section(self, recurring_donations, max_shown=20):
        """Generate the recurring donations section"""
        data = self.prepare_recurring_data(recurring_donations, max_shown)
        return self.formatter.format_recurring_section(data)

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

    def generate_analysis_section(self):
        """Generate strategic analysis section with visualizations"""
        section = """
<div style="page-break-before: always;"></div>

## Strategic Analysis

This section provides insights to help you optimize your charitable giving strategy.

### Efficiency Frontier Analysis

![Efficiency Frontier](images/efficiency_frontier.png)

**How to read this chart:**
- **X-axis (Evaluation Score)**: Outstanding×2 + Acceptable - Unacceptable (can be negative)
- **Y-axis (Total Donated)**: How much you've given to them
- Higher scores (right side) indicate better-performing charities
- Reference lines at 0 and 5 show score thresholds

**Key Insights:**
- **Ideal**: Most of your giving should be to charities with higher scores (≥5)
- **Consider**: Are you giving large amounts to lower-rated charities (score <0)?
- **Opportunity**: Are there highly-rated charities you could support more?

"""
        return section

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities, consistent_donors, recurring_donations):
        """Generate complete markdown report by combining all sections"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)

        # Augment data with focus flags for Great Tables
        augmented_donors = self.prepare_consistent_donors_data(consistent_donors)
        augmented_charities = self.prepare_top_charities_data(top_charities)

        html_files = None
        if self.config.get("generate_html", False):
            print("Generating Great Tables HTML files...")
            html_files = save_all_gt_tables(category_totals, yearly_amounts, yearly_counts,
                                           augmented_donors, augmented_charities, total_amount, self.config,
                                           self.df, one_time, stopped_recurring, self.charity_details,
                                           self.charity_descriptions, self.graph_info, self.charity_evaluations)
            if not html_files:
                raise RuntimeError("Failed to generate Great Tables HTML files")

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
                report += self.generate_category_section(category_totals, total_amount, html_files)
            elif section_id == "consistent":
                report += self.generate_consistent_donors_section(consistent_donors, html_files)
            elif section_id == "yearly":
                report += self.generate_yearly_section(yearly_amounts, yearly_counts, html_files)
            elif section_id == "top_charities":
                report += self.generate_top_charities_section(top_charities, html_files)
            elif section_id == "patterns":
                report += self.generate_one_time_section(one_time)
                report += self.generate_stopped_recurring_section(stopped_recurring)
            elif section_id == "focus":
                report += self.generate_focus_charities_section()
            elif section_id == "focus_summary":
                report += self.generate_focus_summary_section()
            elif section_id == "recurring":
                max_shown = section_options.get("max_shown", 20)
                report += self.generate_recurring_donations_section(recurring_donations, max_shown)
            elif section_id == "detailed":
                pass
            elif section_id == "analysis":
                pass  # Analysis handled separately after detailed section

        report += "\n### Detailed Donation History\n\n"

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            report += self.generate_charity_detail_section(i, tax_id)

        # Add analysis section if requested
        if any(s.get("name") == "analysis" if isinstance(s, dict) else s == "analysis" for s in sections):
            report += self.generate_analysis_section()

        with open("../output/donation_analysis.md", "w") as f:
            f.write(report)
