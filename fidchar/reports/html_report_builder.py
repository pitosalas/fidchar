#!/usr/bin/env python3
"""HTML comprehensive report builder module - BOOTSTRAP VERSION.

Handles the creation of comprehensive HTML reports with all sections.
Uses Bootstrap CSS and report_generator renderers for cleaner code.
"""

import pandas as pd
from datetime import datetime
from typing import List
import reports.base_report_builder as brb
from report_generator.models import ReportTable, ReportCard, CardSection
from report_generator.renderers import HTMLSectionRenderer, HTMLCardRenderer


def _build_html_document(tables: List[ReportTable], doc_title, custom_header, custom_footer, custom_styles, container_class):
    """Build a complete HTML document with Bootstrap CSS.

    Private helper function for building HTML reports with custom header/footer/styles.
    """
    hr = HTMLSectionRenderer()
    sections = "\n".join(hr.render(t) for t in tables)

    styles_block = f"<style>\n{custom_styles}\n</style>" if custom_styles else ""
    header_block = custom_header if custom_header else ""
    footer_block = custom_footer if custom_footer else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  {styles_block}
</head>
<body>
<div class="{container_class}">
{header_block}
{sections}
{footer_block}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def generate_html_header_section(total_donations, total_amount, years_covered,
                                one_time_total, stopped_total, top_charities_count):
    """Generate the custom header and executive summary sections for fidchar report"""
    return f"""        <header class="text-center mb-5 pb-3 border-bottom">
            <h1 class="display-4">Charitable Donation Analysis Report</h1>
            <p class="text-muted">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="alert alert-light border">
                <strong>Total Donations:</strong> {total_donations:,} donations |
                <strong>Total Amount:</strong> ${total_amount:,.2f} |
                <strong>Years Covered:</strong> {years_covered}
            </div>
        </header>

        <div class="row mb-5">
            <div class="col-md-4">
                <div class="card border-start border-4 border-primary">
                    <div class="card-body">
                        <h5 class="card-title">One-Time Donations</h5>
                        <p class="card-text"><strong>78 organizations</strong></p>
                        <p class="card-text">Total: ${one_time_total:,.2f}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border-start border-4 border-warning">
                    <div class="card-body">
                        <h5 class="card-title">Stopped Recurring</h5>
                        <p class="card-text"><strong>5 organizations</strong></p>
                        <p class="card-text">Total: ${stopped_total:,.2f}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border-start border-4 border-success">
                    <div class="card-body">
                        <h5 class="card-title">Top {top_charities_count} Charities</h5>
                        <p class="card-text"><strong>Major recipients</strong></p>
                        <p class="card-text">Detailed analysis below</p>
                    </div>
                </div>
            </div>
        </div>"""


class HTMLReportBuilder(brb.BaseReportBuilder):
    """HTML report builder with inherited state - BOOTSTRAP VERSION"""

    def __init__(self, df, config, charity_details, graph_info, charity_evaluations, focus_ein_set=None):
        super().__init__(df, config, charity_details, graph_info, charity_evaluations, focus_ein_set)
        self.table_renderer = HTMLSectionRenderer()
        self.card_renderer = HTMLCardRenderer()

    def generate_top_charities_bootstrap(self, top_charities):
        """Generate top charities table using Bootstrap renderer"""
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

    def generate_category_table_bootstrap(self, category_totals, total_amount):
        """Generate category totals table using Bootstrap renderer"""
        df = category_totals.reset_index()
        df.columns = ['Charitable Sector', 'Total Amount']
        df['Percentage'] = (df['Total Amount'] / total_amount * 100).apply(lambda x: f"{x:.1f}%")
        df['Total Amount'] = df['Total Amount'].apply(lambda x: f"${x:,.0f}")

        table = ReportTable.from_dataframe(
            df,
            title="Donations by Charitable Sector"
        )
        return self.table_renderer.render(table)

    def generate_yearly_table_bootstrap(self, yearly_amounts, yearly_counts):
        """Generate yearly analysis table using Bootstrap renderer"""
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

    def generate_one_time_table_bootstrap(self, one_time, max_shown=20):
        """Generate one-time donations table using Bootstrap renderer"""
        df = one_time.head(max_shown).reset_index()[['Organization_Name', 'Total_Amount', 'First_Date']]
        df['Total_Amount'] = df['Total_Amount'].apply(lambda x: f"${x:,.2f}")
        df['First_Date'] = df['First_Date'].dt.strftime("%m/%d/%Y")
        df.columns = ['Organization', 'Amount', 'Date']

        table = ReportTable.from_dataframe(
            df,
            title=f"One-Time Donations ({len(one_time)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_stopped_table_bootstrap(self, stopped_recurring, max_shown=15):
        """Generate stopped recurring table using Bootstrap renderer"""
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

    def generate_focus_summary_section_html(self, data):
        """Generate focus charities summary as HTML using HTMLSectionRenderer"""
        if data is None:
            return """
    <div class="report-section">
        <h2 class="section-title">Focus Charities Summary</h2>
        <p>No focus charities identified.</p>
    </div>"""

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
            title=None  # Title will be in section header
        )
        table_html = self.table_renderer.render(table)

        return f"""
    <div class="report-section">
        <h2 class="section-title">Focus Charities Summary</h2>
        <p>{data['count']} charities identified as strategic focus based on your donation patterns:</p>
        {table_html}
        <p style="font-weight: bold; margin-top: 20px;">
            Total donated to focus charities: ${data['total']:,.2f}
        </p>
    </div>"""

    def generate_charity_card_bootstrap(self, i, tax_id):
        """Generate charity detail as Bootstrap card"""
        org_donations = self.charity_details[tax_id]
        has_graph = self.graph_info.get(tax_id) is not None
        evaluation = self.charity_evaluations.get(tax_id)

        # Get description from charapi evaluation
        description = getattr(evaluation, 'summary', None) if evaluation else None
        if not description:
            description = "No description available"

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
                color = 'success' if evaluation.alignment_score >= 70 else 'warning' if evaluation.alignment_score >= 50 else 'danger'
                sections.append(CardSection(
                    section_type="progress_bar",
                    title="Alignment with Your Goals",
                    content={
                        "label": f"Alignment Score: {evaluation.alignment_score}/100",
                        "value": evaluation.alignment_score,
                        "max": 100,
                        "color": color
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
            image_position="right"
        )

        return self.card_renderer.render(card)

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities):
        """Generate complete HTML report using render_html_document base"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)
        years_covered = f"{self.df['Year'].min()} - {self.df['Year'].max()}"
        one_time_total = one_time["Total_Amount"].sum()
        stopped_total = stopped_recurring["Total_Amount"].sum()
        top_charities_count = len(top_charities)

        # Generate custom header
        custom_header = generate_html_header_section(
            total_donations, total_amount, years_covered,
            one_time_total, stopped_total, top_charities_count
        )

        # Generate HTML tables using Bootstrap renderers
        categories_html = self.generate_category_table_bootstrap(category_totals, total_amount)
        yearly_html = self.generate_yearly_table_bootstrap(yearly_amounts, yearly_counts)
        top_charities_html = self.generate_top_charities_bootstrap(top_charities)

        sections_html = generate_table_sections(
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

        # Generate charity cards section
        charity_cards_html = f"""
    <div class="report-section">
        <h2 class="section-title">Detailed Analysis of Top {top_charities_count} Charities</h2>
        <p>Complete donation history and trend analysis for each of the top {top_charities_count} charities:</p>
"""
        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            charity_cards_html += self.generate_charity_card_bootstrap(i, tax_id)
        charity_cards_html += "\n    </div>"

        # Combine body content: sections + charity cards
        body_content = f"{sections_html}\n{charity_cards_html}"

        # Generate footer
        custom_footer = """
    <footer class="mt-5 pt-3 border-top text-center text-muted">
        <small>Generated by fidchar donation analysis tool</small>
    </footer>"""

        # Custom styles for print
        custom_styles = """@media print {
            .card { page-break-inside: avoid; }
        }"""

        # Build complete HTML document
        html_content = _build_html_document(
            [],  # Empty tables list - we're using custom_header/footer for all content
            doc_title="Charitable Donation Analysis Report",
            custom_header=custom_header + body_content,
            custom_footer=custom_footer,
            custom_styles=custom_styles,
            container_class="container my-5"
        )

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
                one_time_table = builder.generate_one_time_table_bootstrap(one_time)
                one_time_total = one_time["Total_Amount"].sum()
                one_time_count = len(one_time)
                overflow_one_time = max(0, one_time_count - 20)

                stopped_table = builder.generate_stopped_table_bootstrap(stopped_recurring)
                stopped_total = stopped_recurring["Total_Amount"].sum()
                stopped_count = len(stopped_recurring)
                overflow_stopped = max(0, stopped_count - 15)

                html_content += f"{one_time_table}"
                if overflow_one_time > 0:
                    html_content += f"""
        <p><em>... and {overflow_one_time} more organizations</em></p>"""
                html_content += f"""
        <p style="margin-top: 15px;"><strong>One-time donations total:</strong> ${one_time_total:,.2f}</p>

    {stopped_table}"""
                if overflow_stopped > 0:
                    html_content += f"""
        <p><em>... and {overflow_stopped} more organizations</em></p>"""
                html_content += f"""
        <p style="margin-top: 15px;"><strong>Stopped recurring donations total:</strong> ${stopped_total:,.2f}</p>"""
        elif section_id == "focus_summary":
            if builder:
                data = builder.prepare_focus_summary_data()
                html_content += builder.generate_focus_summary_section_html(data)

    return html_content