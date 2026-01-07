#!/usr/bin/env python3
"""Base report builder with common business logic.
This module contains shared logic for extracting and processing data,
independent of output format (HTML, Markdown, Text).
"""
import pandas as pd

class BaseReportBuilder:
    """Base class for report builders with shared state and common logic"""

    def __init__(self, df, config, charity_details, graph_info, charity_evaluations, recurring_ein_set=None, pattern_based_ein_set=None):
        self.df = df
        self.config = config
        self.charity_details = charity_details
        self.graph_info = graph_info
        self.charity_evaluations = charity_evaluations
        self.recurring_ein_set = recurring_ein_set or set()
        self.pattern_based_ein_set = pattern_based_ein_set or set()

    def extract_charity_details(self, tax_id):
        """Extract common charity details - single implementation"""
        org_donations = self.charity_details[tax_id]
        org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"

        sector_value = org_donations["Charitable Sector"].iloc[0] if not org_donations.empty else None
        sector = sector_value if pd.notna(sector_value) else "N/A"

        # Get description from charapi evaluation
        evaluation = self.charity_evaluations.get(tax_id)
        description = getattr(evaluation, 'summary', None) if evaluation else None
        if not description:
            description = "No description available"

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
        if not description or description == "No description available":
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
                'is_recurring': self.is_recurring_charity(row['EIN'])
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
            'recurring_charity': tax_id in self.recurring_ein_set
        }

    def prepare_charities_data(self, charities):
        """Augment charities DataFrame with recurring and alignment flags"""
        result = charities.copy()
        result['is_recurring'] = result.index.map(lambda tax_id: self.is_recurring_charity(tax_id))
        result['alignment_status'] = result.index.map(lambda tax_id: self.get_alignment_status(tax_id))
        return result

    # Recurring charities helpers
    def is_recurring_charity(self, ein):
        """Check if a given EIN is a rule-based recurring charity"""
        return ein in self.pattern_based_ein_set

    def for_consideration(self, ein):
        """Check if a charity meets 'for consideration' criteria.

        A charity is 'for consideration' if it meets quality thresholds:
        - Alignment score >= min_alignment_score
        - Evaluation score >= min_evaluation_score

        Evaluation score is calculated as percentage of metrics that are acceptable or outstanding.
        """
        for_consideration_config = self.config.get("for_consideration", {})

        if not for_consideration_config.get("enabled", False):
            return False

        evaluation = self.charity_evaluations.get(ein)
        if not evaluation:
            return False

        # Check alignment score
        min_alignment = for_consideration_config.get("min_alignment_score", 70)
        alignment_score = getattr(evaluation, 'alignment_score', None)
        if alignment_score is None or alignment_score < min_alignment:
            return False

        # Calculate evaluation score (percentage of metrics that are acceptable or outstanding)
        total_metrics = evaluation.total_metrics
        if total_metrics == 0:
            return False

        acceptable_or_better = evaluation.outstanding_count + evaluation.acceptable_count
        evaluation_score = (acceptable_or_better / total_metrics) * 100

        min_evaluation = for_consideration_config.get("min_evaluation_score", 70)
        if evaluation_score < min_evaluation:
            return False

        return True

    def get_alignment_status(self, ein):
        """Get alignment status for a charity based on alignment score.

        Returns: 'aligned' if score >= 70, 'not_aligned' if score < 70, None if no evaluation
        """
        if not self.charity_evaluations or ein not in self.charity_evaluations:
            return None

        evaluation = self.charity_evaluations[ein]
        alignment_score = getattr(evaluation, 'alignment_score', None)

        if alignment_score is None:
            return None

        return 'aligned' if alignment_score >= 70 else 'not_aligned'

    def get_alignment_badge_info(self, alignment_score):
        """Get star rating and color for an alignment score.

        Returns: dict with 'stars', 'bg_color', 'text_color'
        Color scheme: Grey (1 star) -> Light Green -> Medium Green -> Dark Green -> Pure Green (5 stars)
        """
        if alignment_score >= 90:
            return {"stars": "⭐⭐⭐⭐⭐", "bg_color": "#00c853", "text_color": "#fff"}  # Pure green
        elif alignment_score >= 70:
            return {"stars": "⭐⭐⭐⭐", "bg_color": "#43a047", "text_color": "#fff"}  # Dark green
        elif alignment_score >= 50:
            return {"stars": "⭐⭐⭐", "bg_color": "#66bb6a", "text_color": "#fff"}  # Medium green
        elif alignment_score >= 30:
            return {"stars": "⭐⭐", "bg_color": "#81c784", "text_color": "#fff"}  # Soft light green
        else:
            return {"stars": "⭐", "bg_color": "#9e9e9e", "text_color": "#fff"}  # Grey

    def format_charity_info(self, ein, org_name, total_donated=None):
        """Generate charity info with HTML formatting.

        Returns dict with:
        - ein: The EIN string
        - org_name: The organization name
        - is_recurring: Boolean indicating if charity is a recurring charity
        - alignment_status: 'aligned', 'not_aligned', or None
        - total_donated: Optional total donated amount
        - html_org: HTML-formatted org name with recurring and alignment badges
        """
        is_recurring = self.is_recurring_charity(ein)
        alignment_status = self.get_alignment_status(ein)

        # Get Charity Navigator URL if available, fix URL format, or fallback to ProPublica
        profile_url = None
        if ein in self.charity_evaluations:
            evaluation = self.charity_evaluations[ein]
            cn_url = evaluation.data_field_values.get('charity_navigator_url')
            if cn_url:
                # Fix Charity Navigator URL to include 'www' subdomain
                if cn_url.startswith('https://charitynavigator.org/'):
                    profile_url = cn_url.replace('https://charitynavigator.org/', 'https://www.charitynavigator.org/')
                else:
                    profile_url = cn_url

        # Fallback to ProPublica Nonprofit Explorer if no CN URL
        if not profile_url:
            ein_no_dash = ein.replace('-', '')
            profile_url = f'https://projects.propublica.org/nonprofits/organizations/{ein_no_dash}'

        # Wrap org name in link
        org_name_html = f'<a href="{profile_url}" target="_blank" class="text-decoration-none text-reset">{org_name}</a>'

        # Build HTML badges with CSS classes
        badges_html = ""

        # Recurring badge
        if is_recurring:
            badges_html += f" <span class=\"charity-badge\">RECUR</span>"

        # For Consideration badge (only if NOT recurring)
        if not is_recurring and self.for_consideration(ein):
            badges_html += f" <span class=\"charity-badge\">CONSDR</span>"

        # Alignment badge with percentage
        if ein in self.charity_evaluations:
            evaluation = self.charity_evaluations[ein]
            alignment_score = getattr(evaluation, 'alignment_score', None)

            if alignment_score is not None and alignment_score > 0:
                badges_html += f" <span class=\"charity-badge\">ALIGN: {alignment_score}%</span>"

        html_org = org_name_html + badges_html

        result = {
            'ein': ein,
            'org_name': org_name,
            'is_recurring': is_recurring,
            'alignment_status': alignment_status,
            'html_org': html_org
        }

        if total_donated is not None:
            result['total_donated'] = total_donated

        return result

    def get_recurring_charities(self):
        """Return dict of EIN -> evaluation objects for focus charities"""
        if not self.charity_evaluations:
            return {}
        return {ein: ev for ein, ev in self.charity_evaluations.items() if ein in self.recurring_ein_set}

    def recurring_charity_stats(self):
        """Compute count and total donated for focus charities using charity_details."""
        focus = self.get_recurring_charities()
        total = 0.0
        for ein in focus.keys():
            if ein in self.charity_details:
                org_df = self.charity_details[ein]
                if not org_df.empty and 'Amount_Numeric' in org_df.columns:
                    total += org_df['Amount_Numeric'].sum()
        return len(focus), total

    def build_focus_rows(self):
        """Construct rows for focus charities section."""
        focus = self.get_recurring_charities()
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

    def prepare_recurring_summary_data(self, max_shown=20):
        """Prepare focus charities summary with last donation date and total donated.

        Uses the recurring_ein_set which contains ALL focus charities identified from the dataset,
        not just those in the top 10 evaluated charities.

        Args:
            max_shown: Maximum number of charities to include in the table (default: 20)
        """
        if not self.recurring_ein_set:
            return None

        rows = []
        for ein in self.recurring_ein_set:
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

        # Limit to max_shown
        total_count = len(rows)
        rows = rows[:max_shown]

        total_focus_donated = sum(r['total_donated'] for r in rows)

        return {
            'rows': rows,
            'count': total_count,  # Total count (before limiting)
            'total': total_focus_donated
        }

    def prepare_remaining_charities_data(self, one_time, charities, max_shown=100):
        """Prepare remaining charities: multi-year/multi-donation but not recurring

        These are charities with multiple donations across multiple years that don't
        meet the recurring threshold (5 years with ≥$1000 each).

        Args:
            one_time: DataFrame of one-time donations
            charities: DataFrame of filtered charities (to exclude)
            max_shown: Maximum number to show (default: 100)
        """
        # Get all charities grouped
        all_charities = self.df.groupby('Tax ID').agg({
            'Amount_Numeric': 'sum',
            'Organization': 'first',
            'Submit Date': 'max'
        }).reset_index()

        # Count donations and unique years for each
        donation_counts = self.df.groupby('Tax ID').size()
        unique_years = self.df.groupby('Tax ID')['Year'].nunique()

        all_charities['donation_count'] = all_charities['Tax ID'].map(donation_counts)
        all_charities['unique_years'] = all_charities['Tax ID'].map(unique_years)

        # Filter for gap charities
        one_time_eins = set(one_time.index) if one_time is not None and hasattr(one_time, 'index') else set()
        charity_eins = set(charities.index) if charities is not None and hasattr(charities, 'index') else set()

        remaining = all_charities[
            (all_charities['donation_count'] > 1) &  # Not one-time
            (all_charities['unique_years'] > 1) &     # Multiple years
            (~all_charities['Tax ID'].isin(self.recurring_ein_set)) &  # Not recurring
            (~all_charities['Tax ID'].isin(charity_eins)) &  # Not in filtered charities
            (~all_charities['Tax ID'].isin(one_time_eins))  # Not one-time
        ].copy()

        # Sort by total amount
        remaining = remaining.sort_values('Amount_Numeric', ascending=False)

        total_count = len(remaining)
        total_amount = remaining['Amount_Numeric'].sum()

        # Limit to max_shown
        remaining = remaining.head(max_shown)

        rows = []
        for _, row in remaining.iterrows():
            rows.append({
                'ein': row['Tax ID'],
                'organization': row['Organization'],
                'total_donated': row['Amount_Numeric'],
                'last_date': row['Submit Date'],
                'donation_count': row['donation_count'],
                'unique_years': row['unique_years']
            })

        return {
            'rows': rows,
            'count': total_count,
            'total': total_amount
        }

    def prepare_combined_recurring_data(self, csv_recurring_df, max_shown=100):
        """Prepare combined recurring charities data from both rule-based and CSV sources.

        Combines charities from:
        1. Rule-based recurring (in self.recurring_ein_set)
        2. CSV-based recurring (from csv_recurring_df)

        Args:
            csv_recurring_df: DataFrame with CSV-based recurring charities (from get_csv_recurring_details)
            max_shown: Maximum number to show (default: 100)

        Returns:
            DataFrame with columns: Organization, Total, Count, Years, Source
            where Source is 'rule', 'csv', or 'both'
        """
        from fidchar.core import analysis as an

        # Get stopped recurring EINs FIRST (from analyze_donation_patterns)
        from datetime import datetime
        current_year = datetime.now().year
        org_donations = self.df.groupby("Tax ID").agg({
            "Amount_Numeric": ["sum", "count"],
            "Submit Date": ["min", "max"],
            "Recurring": "first",
            "Organization": "first"
        }).round(2)
        org_donations.columns = ["Total_Amount", "Donation_Count", "First_Date", "Last_Date", "Recurring_Status", "Organization_Name"]

        stopped_recurring = org_donations[
            (org_donations["Donation_Count"] > 1) &
            (org_donations["Last_Date"].dt.year < current_year - 1) &
            (org_donations["Recurring_Status"].str.contains("annually|semi-annually", case=False, na=False))
        ]
        stopped_eins = set(stopped_recurring.index)

        # Get CSV recurring EINs (excluding stopped ones)
        csv_eins_all = set(csv_recurring_df.index) if csv_recurring_df is not None and not csv_recurring_df.empty else set()
        csv_eins = csv_eins_all - stopped_eins  # Remove stopped from active CSV

        # Get rule-based recurring EINs (excluding stopped ones - though rule-based shouldn't include stopped anyway)
        rule_eins = self.recurring_ein_set - stopped_eins

        # Get all unique EINs (include rule, csv, AND stopped)
        all_eins = csv_eins | rule_eins | stopped_eins

        if not all_eins:
            return None

        # Build combined data
        rows = []
        for ein in all_eins:
            org_df = self.df[self.df['Tax ID'] == ein]
            if org_df.empty:
                continue

            # Determine source
            in_csv = ein in csv_eins
            in_rule = ein in rule_eins
            in_stopped = ein in stopped_eins

            # Determine source label
            if in_stopped:
                # Stopped recurring - check what it was originally
                was_in_csv = ein in csv_eins_all
                was_in_rule = ein in self.recurring_ein_set

                if was_in_csv and was_in_rule:
                    source = 'stopped (was both)'
                elif was_in_csv:
                    source = 'stopped (was csv)'
                elif was_in_rule:
                    source = 'stopped (was rule)'
                else:
                    source = 'stopped'
            elif in_csv and in_rule:
                source = 'both'
            elif in_csv:
                source = 'csv'
            else:
                source = 'rule'

            # Get charity details
            org_name = org_df['Organization'].iloc[0]
            total = org_df['Amount_Numeric'].sum()
            count = len(org_df)
            years = ', '.join(sorted(set(str(y)[-2:] for y in org_df['Year'])))

            rows.append({
                'EIN': ein,
                'Organization': org_name,
                'Total': total,
                'Count': count,
                'Years': years,
                'Source': source
            })

        # Create DataFrame and sort by total
        result_df = pd.DataFrame(rows)
        result_df = result_df.set_index('EIN')
        result_df = result_df.sort_values('Total', ascending=False)

        # Limit to max_shown
        if len(result_df) > max_shown:
            result_df = result_df.head(max_shown)

        return result_df

    def prepare_all_charities_data(self, csv_recurring_df, max_shown=None, filter_func=None):
        """Prepare comprehensive list of all charities with detailed columns.

        Columns:
        - Organization: Charity name
        - Total: Total donated across all years
        - CSV: "✓" if in CSV recurring field
        - Rule: "✓" if meets rule-based recurring criteria
        - Years: List of years that received donations (e.g., "10,11,12,13,14,15")
        - [Current Year]: Amount donated in most recent year in data
        - Count: Total number of donations

        Args:
            csv_recurring_df: DataFrame with CSV-based recurring charities
            max_shown: Maximum number to show (default: None = show all)
            filter_func: Optional function(ein, in_csv, in_rule, evaluation) -> bool
                        to filter which charities to include

        Returns:
            DataFrame with all charities sorted by total donation amount
        """
        from fidchar.core import analysis as an
        from datetime import datetime

        # Get CSV recurring EINs
        csv_eins = set(csv_recurring_df.index) if csv_recurring_df is not None and not csv_recurring_df.empty else set()

        # Get rule-based recurring EINs (pattern-based only, not combined)
        rule_eins = self.pattern_based_ein_set

        # Get all charities
        all_charities = self.df.groupby('Tax ID').agg({
            'Organization': 'first',
            'Amount_Numeric': 'sum'
        }).sort_values('Amount_Numeric', ascending=False)

        # Use the most recent year in the data, not current calendar year
        current_year = self.df['Year'].max()

        rows = []
        for ein, row in all_charities.iterrows():
            charity_df = self.df[self.df['Tax ID'] == ein]

            # Get years donated (as 2-digit strings, sorted)
            years = sorted(set(charity_df['Year'].astype(int)))
            years_str = ', '.join(str(y)[-2:] for y in years)

            # Get most recent year donation amount
            amount_current_year = charity_df[charity_df['Year'] == current_year]['Amount_Numeric'].sum()

            # Check if in CSV or Rule
            in_csv = ein in csv_eins
            in_rule = ein in rule_eins

            # Get evaluation for this charity
            evaluation = self.charity_evaluations.get(ein)

            # Apply filter if provided
            if filter_func and not filter_func(ein, in_csv, in_rule, evaluation):
                continue

            rows.append({
                'EIN': ein,
                'Organization': row['Organization'],
                'Total': row['Amount_Numeric'],
                'Rule': "✓" if in_rule else "",
                'Years': years_str,
                f'{current_year}': amount_current_year,
                'Count': len(charity_df)
            })

        # Create DataFrame
        result_df = pd.DataFrame(rows)
        result_df = result_df.set_index('EIN')

        # Already sorted by total (from all_charities)
        # Limit if specified
        if max_shown is not None and len(result_df) > max_shown:
            result_df = result_df.head(max_shown)

        return result_df
