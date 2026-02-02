#!/usr/bin/env python3
"""HTML Section Generator Mixin.

Contains all generate_* methods for creating specific HTML report sections.
These methods are mixed into HTMLReportBuilder via inheritance.

Author: Pito Salas and Claude Code
Open Source Under MIT license
"""

import pandas as pd
from fidchar.reports import html_templates as templates
from fidchar.report_generator.models import ReportTable, ReportCard, CardSection


class HTMLSectionGeneratorsMixin:
    """Mixin class containing all section generation methods."""

    def generate_top_charities_bootstrap(self, charities):
        """Generate charities table using Bootstrap renderer - two columns for print"""
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in charities.iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization'], row['Amount_Numeric'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Amount': f"${row['Amount_Numeric']:,.0f}"
            })

        return self._render_two_column_table(
            df_data,
            title=f"Charities by Total Donations ({len(charities)} charities)"
        )

    def generate_category_table_bootstrap(self, category_totals, total_amount, show_percentages=False):
        """Generate category totals table using Bootstrap renderer"""
        df = category_totals.reset_index()
        df.columns = ['Charitable Sector', 'Total Amount']

        if show_percentages:
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
        """Generate one-time donations table using Bootstrap renderer - two columns for print"""
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

        return self._render_two_column_table(
            df_data,
            title=f"One-Time Donations ({len(one_time)} organizations)"
        )

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
        """Generate recurring charities summary as HTML - two columns for print"""
        if data is None:
            return templates.no_recurring_charities()

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

        columns_html = self._render_two_column_table(df_data)

        return templates.recurring_charities_section(
            min_years=self.recurring_min_years,
            min_amount=self.recurring_min_amount,
            count=data['count'],
            total=data['total'],
            columns_html=columns_html
        )

    def generate_csv_recurring_section_html(self, csv_recurring_df, max_shown):
        """Generate CSV-based recurring charities section as HTML"""
        if csv_recurring_df is None or csv_recurring_df.empty:
            return templates.no_csv_recurring_charities()

        display_df = csv_recurring_df.head(max_shown)
        total_amount = csv_recurring_df['Total'].sum()

        df_data = []
        for ein, row in display_df.iterrows():
            charity_info = self.format_charity_info(ein, row['Organization'], row['Total'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total': f"${row['Total']:,.2f}",
                'Donations': int(row['Count']),
                'Years': row['Years']
            })

        table_df = pd.DataFrame(df_data)
        table = ReportTable.from_dataframe(table_df, title=None)
        table_html = self.table_renderer.render(table)

        return templates.csv_recurring_section(
            csv_count=len(csv_recurring_df),
            display_count=len(display_df),
            table_html=table_html,
            total_amount=total_amount
        )

    def generate_combined_recurring_section_html(self, combined_df, max_shown):
        """Generate combined recurring charities section as HTML.

        Combines both rule-based and CSV-based recurring charities with a Source column.
        """
        if combined_df is None or combined_df.empty:
            return """
    <div class="report-section">
        <h2 class="section-title">Recurring Charities</h2>
        <p>No recurring charities found.</p>
    </div>"""

        display_df = combined_df.head(max_shown)
        total_amount = combined_df['Total'].sum()
        total_count = len(combined_df)

        df_data = []
        for ein, row in display_df.iterrows():
            charity_info = self.format_charity_info(ein, row['Organization'], row['Total'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total': f"${row['Total']:,.2f}",
                'Donations': int(row['Count']),
                'Years': row['Years'],
                'Source': row['Source']
            })

        table_df = pd.DataFrame(df_data)
        table = ReportTable.from_dataframe(table_df, title=None)
        table_html = self.table_renderer.render(table)

        # Count by source
        source_counts = combined_df['Source'].value_counts().to_dict()
        both_count = source_counts.get('both', 0)
        rule_only = source_counts.get('rule', 0)
        csv_only = source_counts.get('csv', 0)

        # Count stopped charities
        stopped_count = sum(1 for s in source_counts.keys() if 'stopped' in s)
        active_count = total_count - stopped_count

        breakdown = f"{both_count} in both, {rule_only} rule-based only, {csv_only} CSV-based only"
        if stopped_count > 0:
            breakdown += f", {stopped_count} stopped"

        return templates.combined_recurring_section(
            min_years=self.recurring_min_years,
            min_amount=self.recurring_min_amount,
            total_count=total_count,
            display_count=len(display_df),
            active_count=active_count,
            breakdown=breakdown,
            table_html=table_html,
            total_amount=total_amount
        )

    def generate_all_charities_section_html(self, all_charities_df, max_shown, title="All Charities", subtitle=None):
        """Generate comprehensive all charities list as HTML.

        Shows all charities with CSV/Rule indicators, years donated, current year amount, etc.

        Args:
            all_charities_df: DataFrame with charity data
            max_shown: Maximum number to display
            title: Section title (default: "All Charities")
            subtitle: Optional custom subtitle. If None, uses default based on showing_text and rule_count
        """
        if all_charities_df is None or all_charities_df.empty:
            return f"""
    <div class="report-section">
        <h2 class="section-title">{title}</h2>
        <p>No charities found.</p>
    </div>"""

        display_df = all_charities_df if max_shown is None else all_charities_df.head(max_shown)
        total_charities = len(all_charities_df)
        total_amount = all_charities_df['Total'].sum()

        # Get current year from column name
        current_year_col = [col for col in all_charities_df.columns if col.isdigit()][0]

        df_data = []
        for ein, row in display_df.iterrows():
            charity_info = self.format_charity_info(ein, row['Organization'], row['Total'])

            df_data.append({
                'EIN': ein,
                'Organization': charity_info['html_org'],
                'Total': f"${row['Total']:,.0f}",
                'Recurr': row['Rule'],
                'Count': int(row['Count']),
                'Years': row['Years'],
                'Current Year': f"${row[current_year_col]:,.0f}" if row[current_year_col] > 0 else ""
            })

        table_df = pd.DataFrame(df_data)
        table = ReportTable.from_dataframe(table_df, title=None)
        table_html = self.table_renderer.render(table)

        # Count Rule-based recurring charities
        rule_count = (all_charities_df['Rule'] == '✓').sum()

        showing_text = f"showing all {total_charities}" if max_shown is None else f"showing top {len(display_df)} of {total_charities}"

        # Generate default subtitle if not provided
        if subtitle is None:
            subtitle = f"Complete list of all charities from your donation history, ordered by total amount donated ({showing_text}). CSV and Rule columns indicate recurring status: {rule_count} meet rule-based recurring criteria (≥{self.recurring_min_years} years, ≥${self.recurring_min_amount:,}/year)."

        return templates.all_charities_section(
            title=title,
            subtitle=subtitle,
            table_html=table_html,
            total_amount=total_amount
        )

    def generate_remaining_charities_section_html(self, data):
        """Generate remaining charities section as HTML - two columns for print"""
        if data is None or data['count'] == 0:
            return ""

        # Build DataFrame from rows
        df_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'

            # Get formatted org name with badges
            charity_info = self.format_charity_info(row['ein'], row['organization'], row['total_donated'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Donated': f"${row['total_donated']:,.2f}",
                'Donations': row['donation_count'],
                'Years': row['unique_years']
            })

        columns_html = self._render_two_column_table(df_data)

        return templates.remaining_charities_section(
            count=data['count'],
            min_years=self.recurring_min_years,
            min_amount=self.recurring_min_amount,
            columns_html=columns_html,
            total=data['total']
        )

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
        total_donated = org_donations["Amount_Numeric"].sum()
        donation_count = len(org_donations)

        # Get most recent donation info
        most_recent_donation = org_donations.loc[org_donations["Submit Date"].idxmax()]
        most_recent_date = most_recent_donation["Submit Date"].strftime("%b %d, %Y")
        most_recent_amount = most_recent_donation["Amount_Numeric"]

        # Get formatted org name with badges
        charity_info = self.format_charity_info(tax_id, org_name, total_donated)
        org_name_with_badges = charity_info['html_org']

        # Get tags and service areas from evaluation data
        tags = "Not specified"
        service_area = "Not specified"
        if evaluation and hasattr(evaluation, 'data_field_values'):
            tags_data = evaluation.data_field_values.get('tags', [])
            if tags_data:
                if isinstance(tags_data, list):
                    tags = ", ".join(tags_data)
                else:
                    tags = str(tags_data)

            service_areas_data = evaluation.data_field_values.get('service_areas', [])
            if service_areas_data:
                if isinstance(service_areas_data, list):
                    service_area = ", ".join(service_areas_data)
                else:
                    service_area = str(service_areas_data)

        sections = [
            CardSection(
                section_type="key_value",
                content={
                    "Tax ID": tax_id,
                    "Mission": tags,
                    "Service Area": service_area,
                    "Donations": f"${total_donated:,.0f} ({donation_count}x) | Latest: ${most_recent_amount:,.0f} on {most_recent_date}"
                }
            )
        ]

        if evaluation:
            # Calculate overall evaluation score (percentage of acceptable or better)
            total_metrics = evaluation.total_metrics
            if total_metrics > 0:
                acceptable_or_better = evaluation.outstanding_count + evaluation.acceptable_count
                eval_score = int((acceptable_or_better / total_metrics) * 100)
                eval_content = [
                    f"<strong>Overall: {eval_score}% ({acceptable_or_better}/{total_metrics})</strong>",
                    f"⭐ Outstanding: {evaluation.outstanding_count} metrics",
                    f"✓ Acceptable: {evaluation.acceptable_count} metrics",
                    f"⚠ Unacceptable: {evaluation.unacceptable_count} metrics"
                ]
            else:
                eval_content = [
                    f"⭐ Outstanding: {evaluation.outstanding_count} metrics",
                    f"✓ Acceptable: {evaluation.acceptable_count} metrics",
                    f"⚠ Unacceptable: {evaluation.unacceptable_count} metrics"
                ]

            sections.append(CardSection(
                section_type="list",
                title="Charity Evaluation:",
                content=eval_content
            ))

            if evaluation.alignment_score is not None and evaluation.alignment_score > 0:
                # Get preference metrics breakdown
                alignment_score = evaluation.alignment_score
                from charapi.data.charity_evaluation_result import MetricCategory
                preference_metrics = [m for m in evaluation.metrics if m.category == MetricCategory.PREFERENCE]

                breakdown_items = [f"<strong>Overall Score: {alignment_score}/100</strong>"]
                for metric in preference_metrics:
                    status_icon = "⭐" if metric.status.value == "outstanding" else "✓" if metric.status.value == "acceptable" else "⚠"
                    # Shorten label: "Mission Alignment" -> "Mission"
                    short_name = metric.name.replace(" Alignment", "")
                    breakdown_items.append(f"{status_icon} {short_name}: {metric.display_value}")

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
            title=f"{org_name_with_badges}",
            badge=None,  # Badges are now in the title
            sections=sections,
            image_url=graph_filename,
            image_position="right"  # Right position - will need custom rendering
        )

        return self.card_renderer.render(card)

