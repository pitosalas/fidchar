from dataclasses import dataclass, field
import pandas as pd

@dataclass
class ReportTable:
    title: str | None
    columns: list[str]
    rows: list[list[str | int | float]]
    footnotes: list[str] = field(default_factory=list)
    source: str | None = None
    focus_flags: list[bool] = field(default_factory=list)

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        title: str | None = None,
        footnotes: list[str] | None = None,
        source: str | None = None,
        focus_column: str | None = None,
    ):
        df = df.copy()
        focus_flags = df[focus_column].tolist() if focus_column and focus_column in df.columns else [False] * len(df)
        if focus_column and focus_column in df.columns:
            df.drop(columns=[focus_column], inplace=True)
        return cls(
            title=title,
            columns=list(df.columns),
            rows=df.values.tolist(),
            footnotes=footnotes or [],
            source=source,
            focus_flags=focus_flags,
        )


@dataclass
class CardSection:
    """A section within a card - can be text, key-value pairs, list, table, etc."""
    section_type: str  # "text", "key_value", "list", "progress_bar", "table"
    content: dict | list | str
    title: str | None = None


@dataclass
class ReportCard:
    """Represents a Bootstrap card component - completely general and reusable"""
    title: str
    sections: list[CardSection] = field(default_factory=list)
    badge: str | None = None
    image_url: str | None = None
    image_position: str = "right"  # "right", "left", "top", "bottom"