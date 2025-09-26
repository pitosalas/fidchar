#!/usr/bin/env python3

import pandas as pd
from great_tables import GT, style, loc

# Sample data from your donation analysis
category_data = {
    'Charitable Sector': [
        'Arts and Culture',
        'Society Benefit',
        'Environment and Animals',
        'Human Services',
        'International Affairs'
    ],
    'Total Amount': [900600.00, 268225.00, 211900.00, 209330.00, 189250.00],
    'Percentage': [40.5, 12.1, 9.5, 9.4, 8.5]
}

top_charities_data = {
    'Rank': [1, 2, 3],
    'Organization': [
        '47 PALMER INC',
        'JEWISH RECONSTRUCTIONIST FEDERATION',
        'WORLD UNION FOR PROGRESSIVE JUDAISM'
    ],
    'Total Amount': [641900.00, 228600.00, 80000.00],
    'Tax ID': ['04-3255365', '13-2500888', '13-1930176']
}

# Create DataFrames
df_categories = pd.DataFrame(category_data)
df_charities = pd.DataFrame(top_charities_data)

print("=== BASIC GREAT TABLES EXAMPLE ===")

# Simple Great Table with Tufte-style clean formatting
gt_simple = (
    GT(df_categories)
    .tab_header(
        title="Charitable Donations by Sector",
        subtitle="Clean, typeset presentation"
    )
    .fmt_currency(columns="Total Amount", currency="USD")
    .fmt_percent(columns="Percentage", scale_values=False, decimals=1)
    .cols_align(align="left", columns="Charitable Sector")
    .cols_align(align="right", columns=["Total Amount", "Percentage"])
)

print("Basic Great Table created!")
print(gt_simple)

print("\n=== TOP CHARITIES EXAMPLE ===")

gt_charities = (
    GT(df_charities)
    .tab_header(title="Top 3 Charities")
    .fmt_currency(columns="Total Amount", currency="USD")
    .cols_align(align="center", columns="Rank")
    .cols_align(align="left", columns="Organization")
    .cols_align(align="right", columns="Total Amount")
    .cols_align(align="center", columns="Tax ID")
)

print(gt_charities)

# Try to save HTML versions
try:
    gt_simple.save("output/gt_categories_sample.html")
    gt_charities.save("output/gt_charities_sample.html")
    print("\nHTML files saved to output/ directory!")
    print("- output/gt_categories_sample.html")
    print("- output/gt_charities_sample.html")
except Exception as e:
    print(f"\nCouldn't save HTML files: {e}")
    print("But the Great Tables objects were created successfully!")

print("\nGreat Tables provides:")
print("- Professional typography")
print("- Automatic currency/percentage formatting")
print("- Clean, publication-ready appearance")
print("- Export to HTML, PNG, PDF formats")
print("- Much more sophisticated than tabulate!")