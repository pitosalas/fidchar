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