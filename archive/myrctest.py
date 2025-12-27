from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd

# -----------------------------
# 📦 Core Data Structure
# -----------------------------
@dataclass
class ReportTable:
    title: Optional[str]
    columns: List[str]
    rows: List[List[Union[str, int, float]]]
    footnotes: Optional[List[str]] = field(default_factory=list)
    source: Optional[str] = None
    focus_flags: Optional[List[bool]] = field(default_factory=list)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, title: Optional[str] = None,
                       footnotes: Optional[List[str]] = None, source: Optional[str] = None,
                       focus_column: Optional[str] = None):
        df = df.copy()
        focus_flags = df[focus_column].tolist() if focus_column and focus_column in df.columns else [False] * len(df)
        if focus_column:
            df.drop(columns=[focus_column], inplace=True)
        return cls(
            title=title,
            columns=list(df.columns),
            rows=df.values.tolist(),
            footnotes=footnotes,
            source=source,
            focus_flags=focus_flags
        )

# -----------------------------
# 🧩 Renderer Interface
# -----------------------------
class TableRenderer:
    def render(self, table: ReportTable) -> str:
        raise NotImplementedError("Subclasses must implement render()")

# -----------------------------
# 📄 Text Renderer
# -----------------------------
class TextRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        lines = []
        if table.title:
            lines.append(table.title)
            lines.append("=" * len(table.title))
        lines.append(" | ".join(table.columns))
        lines.append("-" * len(lines[-1]))
        for i, row in enumerate(table.rows):
            row_copy = row.copy()
            if table.focus_flags[i]:
                row_copy[0] += " [FOCUS]"  # Organization column
            lines.append(" | ".join(str(cell) for cell in row_copy))
        if table.footnotes:
            lines.append("\nFootnotes:")
            for i, note in enumerate(table.footnotes, 1):
                lines.append(f"[{i}] {note}")
        if table.source:
            lines.append(f"\nSource: {table.source}")
        return "\n".join(lines)

# -----------------------------
# 📝 Markdown Renderer
# -----------------------------
class MarkdownRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        lines = []
        if table.title:
            lines.append(f"## {table.title}")
        lines.append("| " + " | ".join(table.columns) + " |")
        lines.append("| " + " | ".join("---" for _ in table.columns) + " |")
        for i, row in enumerate(table.rows):
            row_copy = row.copy()
            if table.focus_flags[i]:
                row_copy[0] += " **[FOCUS]**"
            lines.append("| " + " | ".join(str(cell) for cell in row_copy) + " |")
        if table.footnotes:
            lines.append("\n**Footnotes**")
            for i, note in enumerate(table.footnotes, 1):
                lines.append(f"[{i}] {note}")
        if table.source:
            lines.append(f"\n_Source: {table.source}_")
        return "\n".join(lines)

# -----------------------------
# 🌐 HTML Renderer (Bootstrap)
# -----------------------------
class HTMLRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        html = []

        html.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{table.title or "Report"}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container my-4">
""")

        if table.title:
            html.append(f"<h2 class='mb-4'>{table.title}</h2>")

        html.append("<div class='table-responsive'>")
        html.append("<table class='table table-bordered table-striped'>")
        html.append("<thead class='table-dark'><tr>" + "".join(f"<th>{col}</th>" for col in table.columns) + "</tr></thead>")
        html.append("<tbody>")
        for i, row in enumerate(table.rows):
            row_cells = []
            for j, cell in enumerate(row):
                if j == 0 and table.focus_flags[i]:  # Organization column
                    cell = f"{cell} <span class='badge bg-warning text-dark ms-2'>FOCUS</span>"
                row_cells.append(f"<td>{cell}</td>")
            html.append("<tr>" + "".join(row_cells) + "</tr>")
        html.append("</tbody></table>")
        html.append("</div>")

        if table.footnotes:
            html.append("<div class='mt-4'><strong>Footnotes:</strong><ul>")
            for note in table.footnotes:
                html.append(f"<li>{note}</li>")
            html.append("</ul></div>")

        if table.source:
            html.append(f"<div class='mt-2'><em>Source: {table.source}</em></div>")

        html.append("</div></body></html>")
        return "\n".join(html)

# -----------------------------
# 🚀 Main Execution
# -----------------------------
if __name__ == "__main__":
    data = {
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

    df = pd.DataFrame(data)

    table = ReportTable.from_dataframe(
        df,
        title="Top 15 Charities by Total Donations",
        footnotes=["FOCUS organizations are marked with a yellow badge next to their name."],
        source="Uploaded table image",
        focus_column="FOCUS"
    )

    outputs = {
        "t1.txt": TextRenderer().render(table),
        "t1.md": MarkdownRenderer().render(table),
        "t1.html": HTMLRenderer().render(table)
    }

    for filename, content in outputs.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved: {filename}")