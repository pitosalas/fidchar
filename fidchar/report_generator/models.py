from dataclasses import dataclass, field
import pandas as pd

@dataclass
class ReportTable:
    title: str | None
    columns: list[str]
    rows: list[list[str | int | float]]
    footnotes: list[str] = field(default_factory=list)
    source: str | None = None
    recurring_flags: list[bool] = field(default_factory=list)
    alignment_flags: list[str | None] = field(default_factory=list)  # 'aligned', 'not_aligned', or None

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        title: str | None = None,
        footnotes: list[str] | None = None,
        source: str | None = None,
        recurring_column: str | None = None,
        alignment_column: str | None = None,
    ):
        df = df.copy()

        # Extract recurring flags
        recurring_flags = df[recurring_column].tolist() if recurring_column and recurring_column in df.columns else [False] * len(df)
        if recurring_column and recurring_column in df.columns:
            df.drop(columns=[recurring_column], inplace=True)

        # Extract alignment flags
        alignment_flags = df[alignment_column].tolist() if alignment_column and alignment_column in df.columns else [None] * len(df)
        if alignment_column and alignment_column in df.columns:
            df.drop(columns=[alignment_column], inplace=True)

        return cls(
            title=title,
            columns=list(df.columns),
            rows=df.values.tolist(),
            footnotes=footnotes or [],
            source=source,
            recurring_flags=recurring_flags,
            alignment_flags=alignment_flags,
        )


@dataclass
class CardSection:
    """A section within a card - can be text, key-value pairs, list, table, etc."""
    section_type: str  # "text", "key_value", "list", "table"
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