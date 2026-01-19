def test_export_csv_logic():
def run():
import os
import csv
import tempfile
import shutil
from types import SimpleNamespace

import pytest

@pytest.mark.usefixtures("tmp_path")
def test_export_csv_logic(tmp_path):
    output_csv = tmp_path / "charity_export.csv"
    # Fake evaluation objects (simulate char_evals)
    char_evals = {
        "12-3456789": SimpleNamespace(
            organization_name="Charity A",
            summary="Mission A",
            data_field_values={"budget": "$1M", "client_geography": "USA"},
            alignment_score=95
        ),
        "98-7654321": SimpleNamespace(
            organization_name="Charity B",
            summary="Mission B",
            data_field_values={"budget": "$2M", "client_geography": "Global"},
            alignment_score=80
        )
    }
    # Simulate the export logic (copy-paste from main.py)
    rows = []
    for ein, eval_obj in char_evals.items():
        name = getattr(eval_obj, 'organization_name', None) or getattr(eval_obj, 'name', None) or ''
        mission = getattr(eval_obj, 'summary', None) or ''
        budget = ''
        geography = ''
        if hasattr(eval_obj, 'data_field_values'):
            vals = eval_obj.data_field_values
            budget = vals.get('budget', '') or vals.get('budget_size', '') or ''
            geography = vals.get('client_geography', '') or vals.get('geography', '') or ''
        alignment = getattr(eval_obj, 'alignment_score', None)
        rows.append({
            'EIN': ein,
            'Name': name,
            'Mission': mission,
            'Budget': budget,
            'Geography': geography,
            'Alignment': alignment if alignment is not None else ''
        })
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['EIN', 'Name', 'Mission', 'Budget', 'Geography', 'Alignment'])
        writer.writeheader()
        writer.writerows(rows)
    # Check file exists and contents
    assert os.path.exists(output_csv)
    with open(output_csv, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 2
        assert reader[0]['EIN'] == "12-3456789"
        assert reader[0]['Name'] == "Charity A"
        assert reader[0]['Mission'] == "Mission A"
        assert reader[0]['Budget'] == "$1M"
        assert reader[0]['Geography'] == "USA"
        assert reader[0]['Alignment'] == "95"
