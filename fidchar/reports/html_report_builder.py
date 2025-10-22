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

    def __init__(self, df, config, charity_details, graph_info, charity_evaluations, recurring_ein_set=None):
        super().__init__(df, config, charity_details, graph_info, charity_evaluations, recurring_ein_set)
        self.table_renderer = HTMLSectionRenderer()
        self.card_renderer = HTMLCardRenderer()

    def generate_top_charities_bootstrap(self, top_charities):
        """Generate top charities table using Bootstrap renderer"""
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in top_charities.iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization'], row['Amount_Numeric'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Amount': f"${row['Amount_Numeric']:,.0f}"
            })

        df_for_table = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df_for_table,
            title=f"Top {len(top_charities)} Charities by Total Donations"
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
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in one_time.head(max_shown).iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization_Name'], row['Total_Amount'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Amount': f"${row['Total_Amount']:,.2f}",
                'Date': row['First_Date'].strftime("%m/%d/%Y")
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=f"One-Time Donations ({len(one_time)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_stopped_table_bootstrap(self, stopped_recurring, max_shown=15):
        """Generate stopped recurring table using Bootstrap renderer"""
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in stopped_recurring.head(max_shown).iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization_Name'], row['Total_Amount'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Amount': f"${row['Total_Amount']:,.2f}",
                'Donations': row['Donation_Count'],
                'First Date': row['First_Date'].strftime("%m/%d/%Y"),
                'Last Date': row['Last_Date'].strftime("%m/%d/%Y")
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=f"Stopped Recurring Donations ({len(stopped_recurring)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_recurring_summary_section_html(self, data):
        """Generate recurring charities summary as HTML using HTMLSectionRenderer"""
        if data is None:
            return """
    <div class="report-section">
        <h2 class="section-title">Recurring Charities Summary</h2>
        <p>No recurring charities identified.</p>
    </div>"""

        # Build DataFrame from rows
        df_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'

            # Get formatted org name with badges
            charity_info = self.format_charity_info(row['ein'], row['organization'], row['total_donated'])

            df_data.append({
                'EIN': row['ein'],
                'Organization': charity_info['html_org'],
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
        <h2 class="section-title">Recurring Charities Summary</h2>
        <p>{data['count']} charities identified as recurring based on your donation patterns:</p>
        {table_html}
        <p style="font-weight: bold; margin-top: 20px;">
            Total donated to recurring charities: ${data['total']:,.2f}
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

        # Get formatted org name with badges
        charity_info = self.format_charity_info(tax_id, org_name, total_donated)
        org_name_with_badges = charity_info['html_org']

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

        # Add mission statement if available
        mission_text = None
        if evaluation:
            # Try to get mission from evaluation
            mission_text = getattr(evaluation, 'mission', None)

            # If no mission from API, generate from NTEE code
            if not mission_text:
                from charapi.data.ntee_mapper import NTEEMapper
                # Get NTEE code from metrics
                from charapi.data.charity_evaluation_result import MetricCategory
                mission_metric = next((m for m in evaluation.metrics if m.category == MetricCategory.PREFERENCE and "Mission" in m.name), None)
                if mission_metric and mission_metric.value:
                    ntee_code = mission_metric.value
                    mission_text = NTEEMapper.get_description(ntee_code)

        if mission_text:
            sections.append(CardSection(
                section_type="text",
                title="Mission:",
                content=mission_text
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

            if evaluation.alignment_score is not None and evaluation.alignment_score > 0:
                # Get alignment badge (star rating) from centralized method
                alignment_score = evaluation.alignment_score
                badge_info = self.get_alignment_badge_info(alignment_score)

                badge_html = f"<span style='background:{badge_info['bg_color']}; color:{badge_info['text_color']}; padding:4px 8px; border-radius:4px; font-size:14px; font-weight:600;'>ALIGNMENT: {badge_info['stars']}</span>"

                # Get preference metrics breakdown
                from charapi.data.charity_evaluation_result import MetricCategory
                preference_metrics = [m for m in evaluation.metrics if m.category == MetricCategory.PREFERENCE]

                breakdown_items = [f"<strong>Overall Score: {alignment_score}/100</strong> {badge_html}"]
                for metric in preference_metrics:
                    status_icon = "⭐" if metric.status.value == "outstanding" else "✓" if metric.status.value == "acceptable" else "⚠"
                    breakdown_items.append(f"{status_icon} {metric.name}: {metric.display_value}")

                sections.append(CardSection(
                    section_type="list",
                    title="Alignment with Your Goals:",
                    content=breakdown_items
                ))

            if evaluation.summary:
                sections.append(CardSection(
                    section_type="text",
                    content=evaluation.summary
                ))

        graph_filename = f"images/charity_{i:02d}_{tax_id.replace('-', '')}.png" if has_graph else None

        card = ReportCard(
            title=f"{i}. {org_name_with_badges}",
            badge=None,  # Badges are now in the title
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

        # Generate sections HTML (excluding definitions which will be added at the end)
        sections_html = generate_table_sections(
            categories_html,
            yearly_html,
            top_charities_html,
            one_time,
            stopped_recurring,
            self.config,
            self.charity_evaluations,
            self,
            top_charities_count,
            exclude_definitions=True  # We'll add this manually at the end
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

        # Generate definitions section (at the very end)
        definitions_html = generate_definitions_section()

        # Combine body content: sections + charity cards + definitions
        body_content = f"{sections_html}\n{charity_cards_html}\n{definitions_html}"

        # Generate footer
        custom_footer = """
    <footer class="mt-5 pt-3 border-top text-center text-muted">
        <small>Generated by fidchar donation analysis tool</small>
    </footer>"""

        # Custom styles for print/PDF and definitions
        custom_styles = """
        /* Reduce table row padding for more compact display */
        .table td,
        .table th {
            padding: 0.4rem 0.5rem;
        }

        /* Definitions section styling */
        .definitions-content {
            font-size: 0.95rem;
            line-height: 1.6;
        }
        .definitions-content h1 {
            font-size: 2rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 0.5rem;
        }
        .definitions-content h2 {
            font-size: 1.4rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #0d6efd;
        }
        .definitions-content h3 {
            font-size: 1.1rem;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .definitions-content p {
            margin-bottom: 0.75rem;
        }
        .definitions-content ul {
            margin-bottom: 1rem;
        }

        @media print {
            .report-section {
                page-break-after: always;
                page-break-inside: avoid;
            }
            .card {
                page-break-inside: avoid;
                page-break-after: auto;
            }
            /* Prevent page break after the last section */
            .report-section:last-of-type {
                page-break-after: auto;
            }
            /* Keep executive summary header with its content */
            .section-title {
                page-break-after: avoid;
            }
            /* Keep definition headers with their content */
            .definitions-content h2,
            .definitions-content h3 {
                page-break-after: avoid;
            }
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
                           charity_evaluations=None, builder=None, top_charities_count=10,
                           exclude_definitions=False):
    sections = config.get("sections", {})
    html_content = ""

    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")

        # Skip definitions if we're excluding it (will be added manually at the end)
        if exclude_definitions and section_id == "definitions":
            continue
        section_options = section.get("options", {}) if isinstance(section, dict) else {}
        if section_id == "sectors":
            html_content += f"""
    <div class="report-section">
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
        elif section_id == "recurring_summary":
            if builder:
                data = builder.prepare_recurring_summary_data()
                html_content += builder.generate_recurring_summary_section_html(data)

    return html_content


def generate_definitions_section():
    """Generate the definitions section from markdown file"""
    import os
    from markdown_it import MarkdownIt

    md = MarkdownIt()
    definitions_path = os.path.join(os.path.dirname(__file__), "..", "definitions.md")

    try:
        with open(definitions_path, "r") as f:
            markdown_content = f.read()
            html_definitions = md.render(markdown_content)

        return f"""
    <div class="report-section">
        <div class="definitions-content">
            {html_definitions}
        </div>
    </div>"""
    except FileNotFoundError:
        return """
    <div class="report-section">
        <h2 class="section-title">Definitions</h2>
        <p><em>Definitions file not found.</em></p>
    </div>"""