import sys
sys.path.insert(0, "/Users/pitosalas/mydev/charapi")

import csv
from charapi import evaluate_charity

def extract_unique_eins(csv_path):
    eins = set()
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ein = row.get("Tax ID", "").strip()
            if ein:
                eins.add(ein)
    return sorted(eins)

def main():
    config_path = "/Users/pitosalas/mydev/charapi/charapi/config/config.yaml"
    input_csv_path = "data.csv"
    output_csv_path = "charity_metrics.csv"

    print(f"Reading EINs from {input_csv_path}...")
    eins = extract_unique_eins(input_csv_path)
    print(f"Found {len(eins)} unique EINs")

    successful = 0
    failed = 0

    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["EIN", "Charity Name", "Outstanding", "Acceptable", "Unacceptable"])

        for i, ein in enumerate(eins, 1):
            print(f"Evaluating {i}/{len(eins)}: {ein}", flush=True)
            try:
                result = evaluate_charity(ein, config_path)
                writer.writerow([
                    result.ein,
                    result.organization_name,
                    result.outstanding_count,
                    result.acceptable_count,
                    result.unacceptable_count
                ])
                successful += 1
            except Exception as e:
                print(f"  ERROR: {str(e)}", flush=True)
                failed += 1
                writer.writerow([ein, "ERROR", "", "", ""])

    print(f"\nCSV written to {output_csv_path}")
    print(f"Successful: {successful}, Failed: {failed}")

if __name__ == "__main__":
    main()
