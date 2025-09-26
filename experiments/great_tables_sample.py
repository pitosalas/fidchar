#!/usr/bin/env python3

import pandas as pd
from great_tables import GT

# Sample data from your donation analysis
category_data = {
    'Charitable Sector': [
        'Arts and Culture',
        'Society Benefit',
        'Environment and Animals',
        'Human Services',
        'International Affairs',
        'Religion',
        'Education',
        'Health',
        'Other'
    ],
    'Total Amount': [
        900600.00,
        268225.00,
        211900.00,
        209330.00,
        189250.00,
        182210.00,
        140280.00,
        107525.00,
        15000.00
    ],
    'Percentage': [40.5, 12.1, 9.5, 9.4, 8.5, 8.2, 6.3, 4.8, 0.7]
}

top_charities_data = {
    'Rank': [1, 2, 3, 4, 5],
    'Organization': [
        '47 PALMER INC',
        'JEWISH RECONSTRUCTIONIST FEDERATION',
        'WORLD UNION FOR PROGRESSIVE JUDAISM',
        'COMMONWEALTH ZOOLOGICAL CORPORATION',
        'SCHWAB CHARITABLE FUND'
    ],
    'Total Amount': [641900.00, 228600.00, 80000.00, 72350.00, 50000.00],
    'Tax ID': ['04-3255365', '13-2500888', '13-1930176', '04-3129124', '31-1640316']
}

# Create DataFrames
df_categories = pd.DataFrame(category_data)
df_charities = pd.DataFrame(top_charities_data)

# Create Great Tables with Tufte-inspired styling
print("=== CHARITABLE SECTORS TABLE (Great Tables) ===")
gt_categories = (
    GT(df_categories)
    .tab_header(
        title="Charitable Donations by Sector",
        subtitle="Total donations: $2,224,320.00"
    )
    .fmt_currency(columns="Total Amount", currency="USD", decimals=2)
    .fmt_percent(columns="Percentage", scale_values=False, decimals=1)
    .cols_align(align="left", columns="Charitable Sector")
    .cols_align(align="right", columns=["Total Amount", "Percentage"])
    .tab_style(
        style=[
            {"font-weight": "bold"},
            {"border-bottom": "2px solid #000000"}
        ],
        locations={"cells_column_labels": True}
    )
    .tab_style(
        style={"font-family": "Georgia, serif"},
        locations={"cells_body": True}
    )
    .tab_options(
        table_font_size="12px",
        heading_align="left",
        column_labels_border_top_style="solid",
        column_labels_border_top_width="2px",
        column_labels_border_bottom_style="solid",
        column_labels_border_bottom_width="1px",
        table_border_top_style="none",
        table_border_bottom_style="solid",
        table_border_bottom_width="2px"
    )
)

print("=== TOP CHARITIES TABLE (Great Tables) ===")
gt_charities = (
    GT(df_charities)
    .tab_header(
        title="Top 5 Charities by Total Donations"
    )
    .fmt_currency(columns="Total Amount", currency="USD", decimals=2)
    .cols_align(align="center", columns="Rank")
    .cols_align(align="left", columns="Organization")
    .cols_align(align="right", columns="Total Amount")
    .cols_align(align="center", columns="Tax ID")
    .tab_style(
        style=[
            {"font-weight": "bold"},
            {"border-bottom": "2px solid #000000"}
        ],
        locations={"cells_column_labels": True}
    )
    .tab_style(
        style={"font-family": "Georgia, serif"},
        locations={"cells_body": True}
    )
    .tab_options(
        table_font_size="11px",
        heading_align="left",
        column_labels_border_top_style="solid",
        column_labels_border_top_width="2px",
        column_labels_border_bottom_style="solid",
        column_labels_border_bottom_width="1px",
        table_border_top_style="none",
        table_border_bottom_style="solid",
        table_border_bottom_width="2px"
    )
)

# Save as HTML files
gt_categories.save("../output/categories_gt_sample.html")
gt_charities.save("../output/charities_gt_sample.html")

print("Great Tables samples saved to:")
print("- ../output/categories_gt_sample.html")
print("- ../output/charities_gt_sample.html")
print("\nOpen these files in your browser to see the beautiful typeset tables!")

# Also try to show in terminal (will show the structure)
print("\n=== CATEGORY TABLE STRUCTURE ===")
print(gt_categories)

print("\n=== CHARITY TABLE STRUCTURE ===")
print(gt_charities)