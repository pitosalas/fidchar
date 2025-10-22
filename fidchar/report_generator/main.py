import pandas as pd
from report_generator.models import ReportTable
from report_generator.utils import (
    render_text_document,
    render_markdown_document,
    render_html_document,
    render_profile_text,
    render_profile_markdown,
    render_profile_html
)

if __name__ == "__main__":
    # -----------------------------
    # First table: Top 15 Charities
    # -----------------------------
    data1 = {
        "Organization": [
            "47 PALMER INC",
            "JEWISH RECONSTRUCTIONIST FEDERATION N Y",
            "THE COMMONWEALTH FOR PRESERVING JUDAISM LTD",
            "COMMONWEALTH ZOOLOGICAL CORPORATION",
            "SCHWAB CHARITABLE FUND",
            "PLANNED PARENTHOOD FEDERATION OF",
            "INTERNATIONAL RESCUE COMMITTEE INC",
            "MEDECINS SANS FRONTIERES USA INC",
            "TIDES FOUNDATION",
            "PARTNERS IN HEALTH A NONPROFIT CORPORATION",
            "LAKES REGION CONSERVATION TRUST",
            "WOMEN FOR WOMEN INTERNATIONAL",
            "NEWFOUND FOUNDATION INC",
            "LOCAL EDUCATION OF MASSACHUSETTS INC",
            "GALAPAGOS CONSERVANCY INC"
        ],
        "Total Amount": [
            "$641,900", "$228,600", "$200,000", "$178,000", "$160,000",
            "$150,000", "$150,000", "$150,000", "$150,000", "$150,000",
            "$150,000", "$150,000", "$150,000", "$150,000", "$150,000"
        ],
        "Tax ID": [
            "04-3255536", "13-2500888", "13-3190716", "04-2103562", "94-3285362",
            "13-1644147", "13-5660870", "13-3433452", "51-0198509", "04-3567502",
            "02-6006033", "52-1838756", "20-2283667", "20-3281486", "13-3281486"
        ],
        "FOCUS": [
            True, False, True, False, False,
            True, True, True, False, True,
            False, False, False, False, True
        ]
    }
    df1 = pd.DataFrame(data1)
    table1 = ReportTable.from_dataframe(
        df1,
        title="Top 15 Charities by Total Donations",
        footnotes=["FOCUS organizations are marked with a yellow badge next to their name."],
        source="Uploaded table image",
        focus_column="FOCUS"
    )

    # ---------------------------------
    # Second table: Stopped Donations
    # ---------------------------------
    data2 = {
        "Organization": [
            "AMERICAN CIVIL LIBERTIES UNION FOUNDATION OF MASSACHUSETTS",
            "SOUTHERN POVERTY LAW CENTER INC",
            "PURE WATER FOR THE WORLD INC",
            "NORTH EAST ANIMAL SHELTER INC",
            "LEXINGTON COMMUNITY FARM COALITION INC"
        ],
        "Total Amount": [
            "$22,750.00", "$13,500.00", "$10,250.00", "$5,950.00", "$700.00"
        ],
        "Donations": [8, 8, 10, 17, 5],
        "First Date": [
            "01/12/2010", "03/24/2013", "09/04/2008", "12/28/2006", "04/04/2012"
        ],
        "Last Date": [
            "11/20/2019", "12/24/2018", "04/02/2020", "01/20/2023", "12/04/2017"
        ]
    }
    df2 = pd.DataFrame(data2)
    table2 = ReportTable.from_dataframe(
        df2,
        title="Stopped Recurring Donations",
        footnotes=["Stopped recurring donations total: $53,150.00"],
        source="Uploaded table image"
    )

    # -----------------------------
    # Render tables
    # -----------------------------
    tables = [table1, table2]

    text_content = render_text_document(tables)
    md_content = render_markdown_document(tables)
    html_content = render_html_document(tables, doc_title="Donation Reports")

    # -----------------------------
    # Append profile section
    # -----------------------------
    text_content += "\n\n" + render_profile_text()
    md_content += "\n\n" + render_profile_markdown()
    html_content += "\n" + render_profile_html()

    # -----------------------------
    # Save outputs
    # -----------------------------
    outputs = {
        "t1.txt": text_content,
        "t1.md": md_content,
        "t1.html": html_content
    }

    for filename, content in outputs.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved: {filename}")