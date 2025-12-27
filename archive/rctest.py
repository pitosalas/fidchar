import report_creator as rc

# Define the data manually for full formatting control
rows = [
    (1, "47 PALMER INC", "$641,900", "04-3255536", True),
    (2, "JEWISH RECONSTRUCTIONIST FEDERATION N Y", "$228,600", "13-2500888", True),
    (3, "THE COMMONWEALTH FOR PRESERVING JUDAISM LTD", "$200,000", "13-3190716", True),
    (4, "COMMONWEALTH ZOOLOGICAL CORPORATION", "$200,000", "04-2301992", True),
    (5, "SCHWAB CHARITABLE FUND", "$200,000", "94-3285362", True),
    (6, "PLANNED PARENTHOOD FEDERATION OF", "$170,543", "13-1644147", False),
    (7, "INTERNATIONAL RESCUE COMMITTEE INC", "$150,000", "13-5660870", False),
    (8, "MEDECINS SANS FRONTIERES USA INC", "$150,000", "13-3433452", False),
    (9, "TIDES FOUNDATION", "$150,000", "51-0198509", False),
    (10, "PARTNERS IN HEALTH A NONPROFIT CORPORATION", "$150,000", "04-3567502", False),
    (11, "LAKES REGION CONSERVATION TRUST", "$150,000", "02-0398023", False),
    (12, "WOMEN FOR WOMEN INTERNATIONAL", "$150,000", "52-1838756", False),
    (13, "NETA FOUNDATION INC", "$150,000", "82-3223667", False),
    (14, "EQUAL OUTCOME OF MASSACHUSETTS INC", "$150,000", "83-3281486", False),
    (15, "GALAPAGOS CONSERVANCY INC", "$150,000", "13-3281486", False),
]

# Build HTML table manually
table_html = """
<table style="width:100%; border-collapse:collapse;">
  <thead>
    <tr style="background-color:#f2f2f2;">
      <th style="text-align:left; padding:8px;">Rank</th>
      <th style="text-align:left; padding:8px;">Organization</th>
      <th style="text-align:left; padding:8px;">Total Amount</th>
      <th style="text-align:left; padding:8px;">Tax ID</th>
    </tr>
  </thead>
  <tbody>
"""

for rank, org, amount, tax_id, is_focus in rows:
    badge = (
        '<span style="background-color:gold; color:black; padding:2px 6px; border-radius:4px; font-size:0.8em; font-weight:bold; margin-left:6px;">FOCUS</span>'
        if is_focus else ""
    )
    table_html += f"""
    <tr>
      <td style="padding:8px;">{rank}</td>
      <td style="padding:8px;">{org} {badge}</td>
      <td style="padding:8px;">{amount}</td>
      <td style="padding:8px;">{tax_id}</td>
    </tr>
    """

table_html += "</tbody></table>"

# Generate the report
with rc.ReportCreator(title="Top 15 Charities by Total Donations", description="A ranked list of charitable organizations by donation amount") as report:
    view = rc.Block(
        rc.Markdown("## 🏆 Top 15 Charities by Total Donations"),
        rc.Html(table_html),
        rc.Text("Note: Organizations marked with the gold FOCUS badge are highlighted for special attention.", label="Footnote")
    )
    report.save(view, "charity_donations_report.html")