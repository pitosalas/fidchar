from models import ReportTable

class TableRenderer:
    def render(self, table: ReportTable) -> str:
        raise NotImplementedError

class TextRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        lines: list[str] = []
        if table.title:
            lines.append(table.title)
            lines.append("=" * len(table.title))
        lines.append(" | ".join(table.columns))
        lines.append("-" * len(lines[-1]))
        for i, row in enumerate(table.rows):
            row_copy = list(row)
            if table.focus_flags and i < len(table.focus_flags) and table.focus_flags[i]:
                row_copy[0] = f"{row_copy[0]} [FOCUS]"
            lines.append(" | ".join(str(cell) for cell in row_copy))
        if table.footnotes:
            lines.append("\nFootnotes:")
            for idx, note in enumerate(table.footnotes, 1):
                lines.append(f"[{idx}] {note}")
        if table.source:
            lines.append(f"\nSource: {table.source}")
        return "\n".join(lines)

class MarkdownRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        lines: list[str] = []
        if table.title:
            lines.append(f"## {table.title}")
        lines.append("| " + " | ".join(table.columns) + " |")
        lines.append("| " + " | ".join("---" for _ in table.columns) + " |")
        for i, row in enumerate(table.rows):
            row_copy = list(row)
            if table.focus_flags and i < len(table.focus_flags) and table.focus_flags[i]:
                row_copy[0] = f"{row_copy[0]} **[FOCUS]**"
            lines.append("| " + " | ".join(str(cell) for cell in row_copy) + " |")
        if table.footnotes:
            lines.append("\n**Footnotes**")
            for idx, note in enumerate(table.footnotes, 1):
                lines.append(f"[{idx}] {note}")
        if table.source:
            lines.append(f"\n_Source: {table.source}_")
        return "\n".join(lines)

class HTMLSectionRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        html: list[str] = []
        if table.title:
            html.append(f"<h2 class='mb-3'>{table.title}</h2>")
        html.append("<div class='table-responsive mb-4'>")
        html.append("<table class='table table-bordered table-striped'>")
        html.append("<thead class='table-dark'><tr>" + "".join(f"<th>{c}</th>" for c in table.columns) + "</tr></thead>")
        html.append("<tbody>")
        for i, row in enumerate(table.rows):
            cells = []
            for j, cell in enumerate(row):
                if j == 0 and table.focus_flags and table.focus_flags[i]:
                    cell = f"{cell} <span class='badge bg-warning text-dark ms-2'>FOCUS</span>"
                cells.append(f"<td>{cell}</td>")
            html.append("<tr>" + "".join(cells) + "</tr>")
        html.append("</tbody></table></div>")
        if table.footnotes:
            html.append("<div class='mb-4'><strong>Footnotes:</strong><ul>")
            for note in table.footnotes:
                html.append(f"<li>{note}</li>")
            html.append("</ul></div>")
        if table.source:
            html.append(f"<div class='mb-4'><em>Source: {table.source}</em></div>")
        return "\n".join(html)