#!/usr/bin/env python3
"""Base report builder with common business logic.

This module contains shared logic for extracting and processing data,
independent of output format (HTML, Markdown, Text).
"""

import pandas as pd


class BaseReportBuilder:
    """Base class for report builders with shared state and common logic"""

    def __init__(self, df, config, charity_details, charity_descriptions, graph_info, charity_evaluations):
        self.df = df
        self.config = config
        self.charity_details = charity_details
        self.charity_descriptions = charity_descriptions
        self.graph_info = graph_info
        self.charity_evaluations = charity_evaluations

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

    def get_section_order(self):
        """Get section order from config - single implementation"""
        default_sections = [
            {"name": "exec"}, {"name": "sectors"}, {"name": "consistent"},
            {"name": "yearly"}, {"name": "top_charities"}, {"name": "patterns"},
            {"name": "recurring"}, {"name": "detailed"}
        ]
        return self.config.get("sections", default_sections) if self.config else default_sections

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
                'amount': row['Amount'],
                'total_ever': row['Total_Ever_Donated'],
                'period': row['Period'],
                'last_date': row['Last_Donation_Date']
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
            'evaluation': evaluation
        }
