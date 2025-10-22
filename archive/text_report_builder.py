#!/usr/bin/env python3
"""Text report builder module - NEW VERSION using report_generator.

Generates plain text reports using TextRenderer from report_generator.
"""

import pandas as pd
from datetime import datetime
from reports.base_report_builder import BaseReportBuilder
from report_generator.models import ReportTable, ReportCard, CardSection
from report_generator.renderers import TextRenderer, TextCardRenderer


class TextReportBuilder(BaseReportBuilder):

    def __init__(self, df, config, charity_details, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, graph_info, charity_evaluations, focus_ein_set)
        self.table_renderer = TextRenderer()
        self.card_renderer = TextCardRenderer()

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

    def generate_category_table(self, category_totals, total_amount):
        """Generate category totals table using TextRenderer"""
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
        """Generate yearly analysis table using TextRenderer"""
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
        """Generate top charities table using TextRenderer"""
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
        """Generate one-time donations table using TextRenderer"""
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
        """Generate stopped recurring table using TextRenderer"""
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
        """Generate charity detail as text card using TextCardRenderer"""
        org_donations = self.charity_details[tax_id]
        description = getattr(self.charity_evaluations.get(tax_id), "summary", None) or "No description available"
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
                    f"Outstanding: {evaluation.outstanding_count} metrics",
                    f"Acceptable: {evaluation.acceptable_count} metrics",
                    f"Unacceptable: {evaluation.unacceptable_count} metrics"
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
            image_url=graph_filename
        )

        return self.card_renderer.render(card)

    def generate_focus_summary_section(self):
        """Generate focus charities summary section using TextRenderer"""
        data = self.prepare_focus_summary_data()
        if data is None:
            return f"""FOCUS CHARITIES SUMMARY
{'-' * 80}

No focus charities identified.

"""

        section = f"""FOCUS CHARITIES SUMMARY
{'-' * 80}

{data['count']} charities identified as strategic focus based on your donation patterns:

"""

        # Build DataFrame from rows
        df_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'
            df_data.append({
                'EIN': row['ein'],
                'Organization': row['organization'][:40],
                'Total Donated': f"${row['total_donated']:,.2f}",
                'Last Donation': last_date_str
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=None  # Title already in section header
        )
        section += self.table_renderer.render(table)
        section += f"\n\nTotal donated to focus charities: ${data['total']:,.2f}\n\n"

        return section

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities):
        """Generate complete text report by combining all sections"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)

        report = self.generate_report_header(total_amount, total_donations)

        for section in self.config.get("sections", {}):
            section_id, section_options = self.parse_section_config(section)

            if section_id == "exec":
                pass
            elif section_id == "sectors":
                report += f"""DONATIONS BY CHARITABLE SECTOR
{'-' * 80}

{self.generate_category_table(category_totals, total_amount)}

Total: ${total_amount:,.2f}

"""
            elif section_id == "yearly":
                report += f"""YEARLY ANALYSIS
{'-' * 80}

Note: Charts available in images/yearly_amounts.png and images/yearly_counts.png

{self.generate_yearly_table(yearly_amounts, yearly_counts)}

"""
            elif section_id == "top_charities":
                count = len(top_charities)
                report += f"""TOP {count} CHARITIES BY TOTAL DONATIONS
{'-' * 80}

{self.generate_top_charities_table(top_charities)}

"""
            elif section_id == "patterns":
                one_time_total = one_time["Total_Amount"].sum()
                stopped_total = stopped_recurring["Total_Amount"].sum()

                report += f"""ONE-TIME DONATIONS
{'-' * 80}

Organizations that received a single donation ({len(one_time)} organizations):

{self.generate_one_time_table(one_time)}
"""
                if len(one_time) > 20:
                    report += f"\n... and {len(one_time) - 20} more organizations\n"

                report += f"\nOne-time donations total: ${one_time_total:,.2f}\n\n"

                report += f"""STOPPED RECURRING DONATIONS
{'-' * 80}

Organizations with recurring donations that appear to have stopped ({len(stopped_recurring)} organizations):

{self.generate_stopped_table(stopped_recurring)}
"""
                if len(stopped_recurring) > 15:
                    report += f"\n... and {len(stopped_recurring) - 15} more organizations\n"

                report += f"\nStopped recurring donations total: ${stopped_total:,.2f}\n\n"

            elif section_id == "focus_summary":
                report += self.generate_focus_summary_section()
            elif section_id == "detailed":
                pass

        report += f"""DETAILED DONATION HISTORY
{'=' * 80}

"""

        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            report += self.generate_charity_card(i, tax_id)

        with open("../output/donation_analysis.txt", "w") as f:
            f.write(report)
