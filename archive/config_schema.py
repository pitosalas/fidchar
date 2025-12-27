#!/usr/bin/env python3
"""Structured configuration schema for Hydra.

Defines dataclasses that provide type safety and validation for config.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CharityNavigatorConfig:
    """Charity Navigator API configuration"""
    app_id: str = "3069"
    app_key: Optional[str] = None


@dataclass
class SectionOptions:
    """Options for specific report sections"""
    min_years: int = 5
    min_amount: int = 500
    max_shown: int = 20
    sort_by: str = "total"


@dataclass
class ReportSection:
    """Configuration for a single report section"""
    name: str = ""
    options: SectionOptions = field(default_factory=SectionOptions)


@dataclass
class AppConfig:
    """Main application configuration"""
    input_file: str = "../data.csv"
    output_dir: str = "../output"
    generate_html: bool = True
    generate_markdown: bool = True
    generate_textfile: bool = False
    charapi_config_path: Optional[str] = None
    charity_navigator: CharityNavigatorConfig = field(default_factory=CharityNavigatorConfig)
    sections: List[Any] = field(default_factory=list)
