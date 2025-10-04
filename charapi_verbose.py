import sys
sys.path.insert(0, "/Users/pitosalas/mydev/charapi")

import csv
from charapi import evaluate_charity
from charapi.data.charity_evaluation_result import MetricCategory, MetricStatus

def status_symbol(status):
    if status == MetricStatus.OUTSTANDING:
        return "⭐"
    elif status == MetricStatus.ACCEPTABLE:
        return "✓"
    elif status == MetricStatus.UNACCEPTABLE:
        return "⚠"
    else:
        return "?"

def print_metrics_table(metrics, category_name, file):
    category_metrics = [m for m in metrics if m.category.value == category_name]
    if not category_metrics:
        return

    print(f"\n{category_name.upper().replace('_', ' ')}", file=file)
    print(f"  {'Metric':<30} {'Value':<20} {'Range':<20} {'Status':<15}", file=file)
    print(f"  {'-'*30} {'-'*15} {'-'*20} {'-'*15}", file=file)

    for metric in category_metrics:
        symbol = status_symbol(metric.status)
        status_text = f"{symbol} {metric.status.value.title()}"
        range_text = f"{metric.ranges.outstanding}/{metric.ranges.acceptable}" if metric.ranges else ""
        print(f"  {metric.name:<30} {metric.display_value:<15} {range_text:<20} {status_text:<15}", file=file)

def extract_unique_eins(csv_path):
    eins = set()
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ein = row.get("Tax ID", "").strip()
            if ein:
                eins.add(ein)
    return sorted(eins)

def write_charity_report(result, file):
    print(f"\nEvaluating charity with EIN: {result.ein}", file=file)
    print("=" * 80, file=file)

    print(f"\n{result.organization_name}", file=file)
    print(f"EIN: {result.ein}", file=file)

    print(f"\n{'SUMMARY'}", file=file)
    print(f"{result.summary}", file=file)

    print_metrics_table(result.metrics, "financial", file)
    print_metrics_table(result.metrics, "compliance", file)
    print_metrics_table(result.metrics, "organization_type", file)
    print_metrics_table(result.metrics, "validation", file)
    print_metrics_table(result.metrics, "preference", file)

    print(f"\nOVERALL ASSESSMENT", file=file)
    print(f"  ⭐ Outstanding:    {result.outstanding_count} metrics ({result.outstanding_count/result.total_metrics*100:.0f}%)", file=file)
    print(f"  ✓ Acceptable:     {result.acceptable_count} metrics ({result.acceptable_count/result.total_metrics*100:.0f}%)", file=file)
    print(f"  ⚠ Unacceptable:   {result.unacceptable_count} metrics ({result.unacceptable_count/result.total_metrics*100:.0f}%)", file=file)
    print("\n" + "=" * 80, file=file)

def main():
    config_path = "/Users/pitosalas/mydev/charapi/charapi/config/config.yaml"
    csv_path = "data.csv"
    output_path = "charity_evaluations.txt"

    print(f"Reading EINs from {csv_path}...")
    eins = extract_unique_eins(csv_path)
    print(f"Found {len(eins)} unique EINs")

    successful = 0
    failed = 0
    failed_eins = []

    with open(output_path, "w") as f:
        from datetime import datetime
        print(f"CHARITY EVALUATION REPORT", file=f)
        print(f"Generated: {datetime.now().isoformat()}", file=f)
        print(f"Total charities: {len(eins)}", file=f)
        print("=" * 80, file=f)

        for i, ein in enumerate(eins, 1):
            print(f"Evaluating {i}/{len(eins)}: {ein}", flush=True)
            try:
                result = evaluate_charity(ein, config_path)
                write_charity_report(result, f)
                successful += 1
            except Exception as e:
                print(f"  ERROR: {str(e)}", flush=True)
                failed += 1
                failed_eins.append(ein)
                print(f"\nERROR evaluating EIN: {ein}", file=f)
                print(f"Error: {str(e)}", file=f)
                print("=" * 80, file=f)

    print(f"\nReport written to {output_path}")
    print(f"Successful: {successful}, Failed: {failed}")
    if failed_eins:
        print(f"Failed EINs: {', '.join(failed_eins)}")

if __name__ == "__main__":
    main()
