#!/usr/bin/env python3
"""Table builder module for eliminating tabulate code duplication.

Provides generic table creation functions following DRY principles.
"""

import pandas as pd
from tabulate import tabulate


def create_table_from_data(data_rows, headers, tablefmt="pipe"):
    """Generic table creator to eliminate duplication"""
    return tabulate(data_rows, headers=headers, tablefmt=tablefmt)


def create_category_summary_table(category_totals, total_amount):
    """Create category totals table using generic builder"""
    data_rows = []
    for category, amount in category_totals.items():
        percentage = (amount / total_amount) * 100
        data_rows.append([category, f"${amount:,.2f}", f"{percentage:.1f}%"])

    return create_table_from_data(
        data_rows,
        ["Charitable Sector", "Total Amount", "Percentage"]
    )


def create_yearly_analysis_table(yearly_amounts, yearly_counts):
    """Create yearly analysis table using generic builder"""
    data_rows = []
    for year in sorted(yearly_amounts.index):
        amount = yearly_amounts[year]
        count = yearly_counts[year]
        data_rows.append([year, f"${amount:,.2f}", count])

    return create_table_from_data(
        data_rows,
        ["Year", "Total Amount", "Number of Donations"]
    )


def create_one_time_donations_table(one_time):
    """Create one-time donations table using generic builder"""
    data_rows = []
    for tax_id, data in one_time.head(20).iterrows():  # Show top 20
        org_name = data["Organization_Name"]
        data_rows.append([
            org_name,
            f"${data['Total_Amount']:,.2f}",
            data["First_Date"].strftime("%m/%d/%Y")
        ])

    return create_table_from_data(
        data_rows,
        ["Organization", "Amount", "Date"]
    )


def create_stopped_recurring_table(stopped_recurring):
    """Create stopped recurring donations table using generic builder"""
    data_rows = []
    for tax_id, data in stopped_recurring.head(15).iterrows():  # Show top 15
        org_name = data["Organization_Name"]
        data_rows.append([
            org_name,
            f"${data['Total_Amount']:,.2f}",
            data["Donation_Count"],
            data["First_Date"].strftime("%m/%d/%Y"),
            data["Last_Date"].strftime("%m/%d/%Y")
        ])

    return create_table_from_data(
        data_rows,
        ["Organization", "Total Amount", "Donations", "First Date", "Last Date"]
    )


def create_top_charities_table(top_charities):
    """Create top charities ranking table using generic builder"""
    data_rows = []
    for i, (tax_id, data) in enumerate(top_charities.iterrows(), 1):
        focus_badge = " **[FOCUS]**" if data.get('is_focus', False) else ""
        org_name = data["Organization"] + focus_badge
        tax_id_display = tax_id if pd.notna(tax_id) else "N/A"
        data_rows.append([i, org_name, f"${data['Amount_Numeric']:,.2f}", tax_id_display])

    return create_table_from_data(
        data_rows,
        ["Rank", "Organization", "Total Amount", "Tax ID"]
    )


def create_donation_history_table(org_donations):
    """Create individual charity donation history table using generic builder"""
    data_rows = []
    for _, donation in org_donations.iterrows():
        data_rows.append([
            donation["Submit Date"].strftime("%m/%d/%Y"),
            f"${donation['Amount_Numeric']:,.2f}"
        ])

    return create_table_from_data(
        data_rows,
        ["Date", "Amount"]
    )


def create_consistent_donors_table(consistent_donors):
    """Create consistent donors table using generic builder"""
    data_rows = []
    for tax_id, donor_info in consistent_donors.items():
        focus_badge = " **[FOCUS]**" if donor_info.get('is_focus', False) else ""
        org_name = donor_info['organization'] + focus_badge
        sector = donor_info['sector']
        total_5_year = donor_info['total_5_year']
        avg_per_year = donor_info['average_per_year']

        # Format yearly amounts for display
        yearly_str = ", ".join([f"{year}: ${amount:,.0f}" for year, amount in sorted(donor_info['yearly_amounts'].items())])

        data_rows.append([
            org_name,
            tax_id,
            sector,
            f"${total_5_year:,.2f}",
            f"${avg_per_year:,.2f}",
            yearly_str
        ])

    return create_table_from_data(
        data_rows,
        ["Organization", "Tax ID", "Sector", "5-Year Total", "Average/Year", "Yearly Breakdown"]
    )