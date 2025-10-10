#!/usr/bin/env python3
"""Base report builder with common business logic.
This module contains shared logic for extracting and processing data,
independent of output format (HTML, Markdown, Text).
"""
import pandas as pd

class BaseReportBuilder:
    """Base class for report builders with shared state and common logic"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations, focus_ein_set=None):
        self.df = df
        self.config = config
        self.charity_details = charity_details
        self.charity_descriptions = charity_descriptions
        self.graph_info = graph_info
        self.charity_evaluations = charity_evaluations
        self.focus_ein_set = focus_ein_set or set()

    def extract_charity_details(self, tax_id):
        """Extract common charity details - single implementation"""
        org_donations = self.charity_details[tax_id]
        org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"

        sector_value = org_donations["Charitable Sector"].iloc[0] if not org_donations.empty else None
        sector = sector_value if pd.notna(sector_value) else "N/A"

        description = self.charity_descriptions.get(tax_id, "No description available")
        total_donated = org_donations['Amount_Numeric'].sum()
        donation_count = len(org_donations)

        return {
            'org_name': org_name,
            'sector': sector,
            'description': description,
            'total_donated': total_donated,
            'donation_count': donation_count
        }

    def get_graph_info(self, i, tax_id):
        """Get graph filename and existence - single implementation"""
        graph_filename = f"images/charity_{i:02d}_{tax_id.replace('-', '')}.png"
        has_graph = self.graph_info.get(tax_id) is not None
        return graph_filename, has_graph

    def truncate_description(self, description, max_length=150):
        """Truncate description - single implementation"""
        if not description or description == "API credentials not configured":
            return None
        return description[:max_length] + "..." if len(description) > max_length else description

    def calculate_recurring_totals(self, recurring_donations):
        """Calculate recurring totals - single implementation"""
        if recurring_donations.empty:
            return {'total_recurring': 0.0, 'total_ever': 0.0}
        return {
            'total_recurring': recurring_donations['Amount'].sum(),
            'total_ever': recurring_donations['Total_Ever_Donated'].sum()
        }

    def parse_section_config(self, section):
        """Parse section configuration - single implementation"""
        section_id = section if isinstance(section, str) else section.get("name")
        section_options = section.get("options", {}) if isinstance(section, dict) else {}
        return section_id, section_options

    def prepare_recurring_data(self, recurring_donations, max_shown=20):
        """Prepare recurring donations data - single implementation"""
        if recurring_donations.empty:
            return None

        rows = []
        for _, row in recurring_donations.head(max_shown).iterrows():
            rows.append({
                'ein': row['EIN'],
                'organization': row['Organization'],
                'first_year': row['First_Year'],
                'years': row['Years_Supported'],
                'amount': row['Amount'],
                'total_ever': row['Total_Ever_Donated'],
                'last_date': row['Last_Donation_Date'],
                'is_focus': self.is_focus_charity(row['EIN'])
            })

        totals = self.calculate_recurring_totals(recurring_donations)
        overflow_count = len(recurring_donations) - max_shown if len(recurring_donations) > max_shown else 0

        return {
            'org_count': len(recurring_donations),
            'rows': rows,
            'totals': totals,
            'overflow_count': overflow_count
        }

    def prepare_charity_detail_data(self, i, tax_id):
        """Prepare charity detail data - single implementation"""
        details = self.extract_charity_details(tax_id)
        graph_filename, has_graph = self.get_graph_info(i, tax_id)
        description = self.truncate_description(details['description'])
        evaluation = self.charity_evaluations.get(tax_id)

        return {
            'index': i,
            'tax_id': tax_id,
            'org_name': details['org_name'],
            'sector': details['sector'],
            'total_donated': details['total_donated'],
            'donation_count': details['donation_count'],
            'description': description,
            'graph_filename': graph_filename,
            'has_graph': has_graph,
            'evaluation': evaluation,
            'focus_charity': getattr(evaluation, 'focus_charity', False) if evaluation else False
        }

    def prepare_top_charities_data(self, top_charities):
        """Augment top charities DataFrame with focus flags"""
        result = top_charities.copy()
        result['is_focus'] = result.index.map(lambda tax_id: self.is_focus_charity(tax_id))
        return result

    # Focus charities helpers
    def is_focus_charity(self, ein):
        """Check if a given EIN is a focus charity"""
        if not self.charity_evaluations or ein not in self.charity_evaluations:
            return False
        evaluation = self.charity_evaluations[ein]
        return getattr(evaluation, 'focus_charity', False)

    def format_charity_info(self, ein, org_name, total_donated=None):
        """Generate unified charity info for all formats.

        Returns dict with:
        - ein: The EIN string
        - org_name: The organization name
        - is_focus: Boolean indicating if charity is a focus charity
        - total_donated: Optional total donated amount
        - html_org: HTML-formatted org name with focus badge
        - markdown_org: Markdown-formatted org name with focus badge
        - text_org: Plain text org name with focus badge
        """
        is_focus = self.is_focus_charity(ein)

        # HTML format with styled badge
        html_badge = " <span style=\"background:#ffd24d; color:#333; padding:2px 6px; border-radius:4px; font-size:12px; font-weight:600;\">FOCUS</span>"
        html_org = org_name + (html_badge if is_focus else "")

        # Markdown format with bold badge
        markdown_badge = " **[FOCUS]**"
        markdown_org = org_name + (markdown_badge if is_focus else "")

        # Text format with simple badge
        text_badge = " [FOCUS]"
        text_org = org_name + (text_badge if is_focus else "")

        result = {
            'ein': ein,
            'org_name': org_name,
            'is_focus': is_focus,
            'html_org': html_org,
            'markdown_org': markdown_org,
            'text_org': text_org
        }

        if total_donated is not None:
            result['total_donated'] = total_donated

        return result

    def get_focus_charities(self):
        """Return dict of EIN -> evaluation objects flagged as focus charities"""
        if not self.charity_evaluations:
            return {}
        return {ein: ev for ein, ev in self.charity_evaluations.items() if getattr(ev, 'focus_charity', False)}

    def focus_charity_stats(self):
        """Compute count and total donated for focus charities using charity_details."""
        focus = self.get_focus_charities()
        total = 0.0
        for ein in focus.keys():
            if ein in self.charity_details:
                org_df = self.charity_details[ein]
                if not org_df.empty and 'Amount_Numeric' in org_df.columns:
                    total += org_df['Amount_Numeric'].sum()
        return len(focus), total

    def build_focus_rows(self):
        """Construct rows for focus charities section."""
        focus = self.get_focus_charities()
        rows = []
        for ein, evaluation in focus.items():
            org_df = self.charity_details.get(ein)
            if org_df is not None and not org_df.empty:
                years = sorted(org_df['Year'].unique()) if 'Year' in org_df.columns else []
                first_year = years[0] if years else None
                last_year = years[-1] if years else None
                period = f"{first_year}-{last_year}" if first_year and last_year else "—"
                sector_val = org_df['Charitable Sector'].iloc[0] if 'Charitable Sector' in org_df.columns and not org_df.empty else 'N/A'
                total_donated = org_df['Amount_Numeric'].sum() if 'Amount_Numeric' in org_df.columns else 0.0
            else:
                period = "—"
                sector_val = 'N/A'
                total_donated = 0.0
                years = []
            rows.append({
                'ein': ein,
                'organization': getattr(evaluation, 'organization_name', 'Unknown'),
                'sector': sector_val,
                'years_supported': len(years),
                'period': period,
                'total_donated': total_donated,
                'alignment_score': getattr(evaluation, 'alignment_score', None),
            })
        # sort by total donated desc
        rows.sort(key=lambda r: r['total_donated'], reverse=True)
        return rows

    def prepare_focus_summary_data(self):
        """Prepare focus charities summary with last donation date and total donated.

        Uses the focus_ein_set which contains ALL focus charities identified from the dataset,
        not just those in the top 10 evaluated charities.
        """
        if not self.focus_ein_set:
            return None

        rows = []
        for ein in self.focus_ein_set:
            org_df = self.df[self.df['Tax ID'] == ein]
            if not org_df.empty:
                org_name = org_df['Organization'].iloc[0]
                total_donated = org_df['Amount_Numeric'].sum() if 'Amount_Numeric' in org_df.columns else 0.0
                last_date = org_df['Submit Date'].max() if 'Submit Date' in org_df.columns else None

                rows.append({
                    'ein': ein,
                    'organization': org_name,
                    'last_date': last_date,
                    'total_donated': total_donated
                })

        # Sort by total donated descending
        rows.sort(key=lambda r: r['total_donated'], reverse=True)

        total_focus_donated = sum(r['total_donated'] for r in rows)

        return {
            'rows': rows,
            'count': len(rows),
            'total': total_focus_donated
        }
