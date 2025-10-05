#!/usr/bin/env python3
"""Tests for data processing functions.

These tests verify CSV parsing, amount conversion, and date handling,
NOT the report formatting/structure.
"""

import pytest
import pandas as pd
import sys
import os
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fidchar'))

from core.data_processing import parse_amount, read_donation_data


class TestParseAmount:
    """Test amount parsing function"""

    def test_parses_simple_dollar_amount(self):
        assert parse_amount("$100.00") == 100.0

    def test_parses_amount_with_commas(self):
        assert parse_amount("$1,000.00") == 1000.0

    def test_parses_large_amount(self):
        assert parse_amount("$10,000,000.50") == 10000000.50

    def test_handles_no_dollar_sign(self):
        assert parse_amount("500.75") == 500.75

    def test_handles_empty_string(self):
        assert parse_amount("") == 0.0

    def test_handles_none(self):
        assert parse_amount(None) == 0.0

    def test_handles_nan(self):
        assert parse_amount(pd.NA) == 0.0

    def test_handles_zero(self):
        assert parse_amount("$0.00") == 0.0

    def test_handles_no_cents(self):
        assert parse_amount("$1,500") == 1500.0


class TestReadDonationData:
    """Test CSV reading and data cleaning"""

    def test_raises_error_for_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_donation_data("nonexistent_file.csv")

    def test_converts_amounts_to_numeric(self):
        csv_data = """Submit Date,Amount,Tax ID
01/15/2024,"$1,000.00",11-1111111
02/20/2024,$500.50,22-2222222"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_path = f.name

        try:
            df = read_donation_data(temp_path)
            assert 'Amount_Numeric' in df.columns
            assert df['Amount_Numeric'].iloc[0] == 1000.0
            assert df['Amount_Numeric'].iloc[1] == 500.50
        finally:
            os.unlink(temp_path)

    def test_converts_dates_to_datetime(self):
        csv_data = """Submit Date,Amount,Tax ID
01/15/2024,$100.00,11-1111111"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_path = f.name

        try:
            df = read_donation_data(temp_path)
            assert pd.api.types.is_datetime64_any_dtype(df['Submit Date'])
        finally:
            os.unlink(temp_path)

    def test_extracts_year_from_date(self):
        csv_data = """Submit Date,Amount,Tax ID
01/15/2024,$100.00,11-1111111
03/20/2025,$200.00,22-2222222"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_path = f.name

        try:
            df = read_donation_data(temp_path)
            assert 'Year' in df.columns
            assert df['Year'].iloc[0] == 2024
            assert df['Year'].iloc[1] == 2025
        finally:
            os.unlink(temp_path)

    def test_strips_column_names(self):
        csv_data = """  Submit Date  ,  Amount  ,  Tax ID
01/15/2024,$100.00,11-1111111"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_path = f.name

        try:
            df = read_donation_data(temp_path)
            assert 'Submit Date' in df.columns
            assert 'Amount' in df.columns
            assert 'Tax ID' in df.columns
        finally:
            os.unlink(temp_path)

    def test_preserves_original_amount_column(self):
        csv_data = """Submit Date,Amount,Tax ID
01/15/2024,"$1,000.00",11-1111111"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_path = f.name

        try:
            df = read_donation_data(temp_path)
            assert 'Amount' in df.columns
            assert 'Amount_Numeric' in df.columns
            assert isinstance(df['Amount'].iloc[0], str)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
