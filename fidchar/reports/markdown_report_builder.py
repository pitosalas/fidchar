#!/usr/bin/env python3
"""Markdown report builder module - NEW VERSION using report_generator.

Generates markdown reports using MarkdownRenderer from report_generator.
"""

import pandas as pd
from datetime import datetime
from reports.base_report_builder import BaseReportBuilder
from report_generator.models import ReportTable, ReportCard, CardSection
from report_generator.renderers import MarkdownRenderer, MarkdownCardRenderer


class MarkdownReportBuilder(BaseReportBuilder):
    """Markdown report builder with inherited state"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set)
        self.table_renderer = MarkdownRenderer()
        self.card_renderer = MarkdownCardRenderer()

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

    def generate_category_table(self, category_totals, total_amount):
        """Generate category totals table using MarkdownRenderer"""
        df = category_totals.reset_index()
        df.columns = ['Charitable Sector', 'Total Amount']
        df['Percentage'] = (df['Total Amount'] / total_amount * 100).apply(lambda x: f"{x:.1f}%")
        df['Total Amount'] = df['Total Amount'].apply(lambda x: f"${x:,.0f}")

        table = ReportTable.from_dataframe(
            df,
            title="Donations by Charitable Sector"
        )
        return self.table_renderer.render(table)

    def generate_yearly_table(self, yearly_amounts, yearly_counts):
        """Generate yearly analysis table using MarkdownRenderer"""
        df = pd.DataFrame({
            'Year': sorted(yearly_amounts.index),
            'Total Amount': [f"${yearly_amounts[year]:,.0f}" for year in sorted(yearly_amounts.index)],
            'Number of Donations': [yearly_counts[year] for year in sorted(yearly_amounts.index)]
        })

        table = ReportTable.from_dataframe(
            df,
            title="Yearly Analysis"
        )
        return self.table_renderer.render(table)

    def generate_top_charities_table(self, top_charities):
        """Generate top charities table using MarkdownRenderer"""
        augmented = self.prepare_top_charities_data(top_charities)
        df_for_table = augmented.reset_index()[['Organization', 'Amount_Numeric', 'is_focus']]
        df_for_table['Amount_Numeric'] = df_for_table['Amount_Numeric'].apply(lambda x: f"${x:,.0f}")
        df_for_table.columns = ['Organization', 'Total Amount', 'FOCUS']

        table = ReportTable.from_dataframe(
            df_for_table,
            title=f"Top {len(top_charities)} Charities by Total Donations",
            focus_column='FOCUS'
        )
        return self.table_renderer.render(table)

    def generate_one_time_table(self, one_time, max_shown=20):
        """Generate one-time donations table using MarkdownRenderer"""
        df = one_time.head(max_shown).reset_index()[['Organization_Name', 'Total_Amount', 'First_Date']]
        df['Total_Amount'] = df['Total_Amount'].apply(lambda x: f"${x:,.2f}")
        df['First_Date'] = df['First_Date'].dt.strftime("%m/%d/%Y")
        df.columns = ['Organization', 'Amount', 'Date']

        table = ReportTable.from_dataframe(
            df,
            title=f"One-Time Donations ({len(one_time)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_stopped_table(self, stopped_recurring, max_shown=15):
        """Generate stopped recurring table using MarkdownRenderer"""
        df = stopped_recurring.head(max_shown).reset_index()[
            ['Organization_Name', 'Total_Amount', 'Donation_Count', 'First_Date', 'Last_Date']
        ]
        df['Total_Amount'] = df['Total_Amount'].apply(lambda x: f"${x:,.2f}")
        df['First_Date'] = df['First_Date'].dt.strftime("%m/%d/%Y")
        df['Last_Date'] = df['Last_Date'].dt.strftime("%m/%d/%Y")
        df.columns = ['Organization', 'Total Amount', 'Donations', 'First Date', 'Last Date']

        table = ReportTable.from_dataframe(
            df,
            title=f"Stopped Recurring Donations ({len(stopped_recurring)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_charity_card(self, i, tax_id):
        """Generate charity detail as markdown card using MarkdownCardRenderer"""
        org_donations = self.charity_details[tax_id]
        description = self.charity_descriptions.get(tax_id, "No description available")
        has_graph = self.graph_info.get(tax_id) is not None
        evaluation = self.charity_evaluations.get(tax_id)

        org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
        sector = org_donations["Charitable Sector"].iloc[0] if not org_donations.empty else "Unknown"
        total_donated = org_donations["Amount_Numeric"].sum()
        donation_count = len(org_donations)

        is_focus = tax_id in self.focus_ein_set if self.focus_ein_set else False

        sections = [
            CardSection(
                section_type="key_value",
                content={
                    "Tax ID": tax_id,
                    "Sector": sector,
                    "Total Donated": f"${total_donated:,.2f}",
                    "Number of Donations": str(donation_count)
                }
            )
        ]

        if description and description != "No description available":
            sections.append(CardSection(
                section_type="text",
                content=description
            ))

        if evaluation:
            sections.append(CardSection(
                section_type="list",
                title="Charity Evaluation:",
                content=[
                    f"⭐ Outstanding: {evaluation.outstanding_count} metrics",
                    f"✓ Acceptable: {evaluation.acceptable_count} metrics",
                    f"⚠ Unacceptable: {evaluation.unacceptable_count} metrics"
                ]
            ))

            if evaluation.alignment_score is not None:
                sections.append(CardSection(
                    section_type="progress_bar",
                    title="Alignment with Your Goals",
                    content={
                        "label": f"Alignment Score: {evaluation.alignment_score}/100",
                        "value": evaluation.alignment_score,
                        "max": 100,
                        "color": "success"
                    }
                ))

            if evaluation.summary:
                sections.append(CardSection(
                    section_type="text",
                    content=evaluation.summary
                ))

        graph_filename = f"images/charity_{i:02d}_{tax_id.replace('-', '')}.png" if has_graph else None

        card = ReportCard(
            title=f"{i}. {org_name}",
            badge="FOCUS" if is_focus else None,
            sections=sections,
            image_url=graph_filename,
            image_position="bottom"
        )

        return self.card_renderer.render(card)

    def generate_focus_charities_section(self):
        """Generate focus charities table section"""
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
        """Generate focus charities summary section using MarkdownRenderer"""
        data = self.prepare_focus_summary_data()
        if data is None:
            return "\n## Focus Charities Summary\n\nNo focus charities identified.\n\n"

        section = f"""## Focus Charities Summary

{data['count']} charities identified as strategic focus based on your donation patterns:

"""

        # Build DataFrame from rows
        df_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'
            df_data.append({
                'EIN': row['ein'],
                'Organization': row['organization'],
                'Total Donated': f"${row['total_donated']:,.2f}",
                'Last Donation': last_date_str
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=None  # Title already in section header
        )
        section += self.table_renderer.render(table)
        section += f"\n**Total donated to focus charities:** ${data['total']:,.2f}\n\n"

        return section

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
                report += "## Donations by Charitable Sector\n\n"
                report += self.generate_category_table(category_totals, total_amount)
                report += f"\n\n**Total:** ${total_amount:,.2f}\n\n"
            elif section_id == "yearly":
                report += """## Yearly Analysis

### Total Donation Amounts by Year

![Yearly Amounts](images/yearly_amounts.png)

"""
                report += self.generate_yearly_table(yearly_amounts, yearly_counts)
                report += "\n\n### Number of Donations by Year\n\n![Yearly Counts](images/yearly_counts.png)\n\n"
            elif section_id == "top_charities":
                count = len(top_charities)
                report += f"\n## Top {count} Charities by Total Donations\n\n"
                report += self.generate_top_charities_table(top_charities)
                report += "\n\n"
            elif section_id == "patterns":
                one_time_total = one_time["Total_Amount"].sum()
                stopped_total = stopped_recurring["Total_Amount"].sum()

                report += "\n## One-Time Donations\n\n"
                report += f"Organizations that received a single donation ({len(one_time)} organizations):\n\n"
                report += self.generate_one_time_table(one_time)

                if len(one_time) > 20:
                    report += f"\n*... and {len(one_time) - 20} more organizations*\n"

                report += f"\n**One-time donations total:** ${one_time_total:,.2f}\n"

                report += "\n## Stopped Recurring Donations\n\n"
                report += f"Organizations with recurring donations that appear to have stopped ({len(stopped_recurring)} organizations):\n\n"
                report += self.generate_stopped_table(stopped_recurring)

                if len(stopped_recurring) > 15:
                    report += f"\n*... and {len(stopped_recurring) - 15} more organizations*\n"

                report += f"\n**Stopped recurring donations total:** ${stopped_total:,.2f}\n"

            elif section_id == "focus":
                report += self.generate_focus_charities_section()
            elif section_id == "focus_summary":
                report += self.generate_focus_summary_section()
            elif section_id == "detailed":
                pass

        report += "\n### Detailed Donation History\n\n"

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            report += self.generate_charity_card(i, tax_id)

        with open("../output/donation_analysis.md", "w") as f:
            f.write(report)
