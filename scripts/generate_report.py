import pandas as pd
import json
import os
from pandas import json_normalize

input_csv = "./output/cleaned_transactions.csv"
output_excel = "./output/wallet_report.xlsx"


def parse_raw_json(raw_str):
    """
    Safely parse a JSON string, fixing common escape issues.
    """
    try:
        if isinstance(raw_str, str):
            raw_str = raw_str.strip().strip('"')
            raw_str = raw_str.replace('"{', "{").replace('}"', "}")
            raw_str = raw_str.replace('\\"', '"')
            return json.loads(raw_str)
        elif isinstance(raw_str, dict):
            return raw_str
    except Exception:
        pass
    return {}


def main():
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df = pd.read_csv(input_csv)
    all_records = []

    for _, row in df.iterrows():
        record = dict(row)

        # Parse `_raw` if present
        if "_raw" in record and isinstance(record["_raw"], str):
            parsed_raw = parse_raw_json(record["_raw"])
            if parsed_raw:
                record.update(parsed_raw)

        # Parse `metadata` if it's JSON
        if "metadata" in record and isinstance(record["metadata"], str):
            parsed_meta = parse_raw_json(record["metadata"])
            record["metadata"] = parsed_meta

        # Flatten record
        flat_record = json_normalize(record, sep=".")
        all_records.append(flat_record)

    if not all_records:
        print("⚠ No records found to process.")
        return

    final_df = pd.concat(all_records, ignore_index=True)
    final_df.dropna(how="all", inplace=True)

    os.makedirs(os.path.dirname(output_excel), exist_ok=True)
    final_df.to_excel(output_excel, index=False)

    print(f"Report generated: {output_excel}")


if __name__ == "__main__":
    main()
