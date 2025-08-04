import pandas as pd
import json
from pandas import json_normalize


def parse_raw_json(raw_str):
    try:
        # Fix improperly escaped inner double quotes (common with nested JSON in "metadata")
        if isinstance(raw_str, str):
            # Remove extra outer quotes if accidentally present
            raw_str = raw_str.strip().strip('"')
            # Handle escaped double quotes in nested JSON
            raw_str = raw_str.replace('"{', "{").replace('}"', "}")
            raw_str = raw_str.replace('\\"', '"')
            return json.loads(raw_str)
        return {}
    except Exception as e:
        print(f"Error parsing JSON: {e}\nRaw: {raw_str}")
        return {}


def main():
    # Load the CSV
    input_csv_path = "./output/cleaned_transactions.csv"
    df = pd.read_csv(input_csv_path)

    # Parse the `_raw` column
    all_records = []
    for raw in df["_raw"]:
        parsed = parse_raw_json(raw)

        # Try to parse metadata field if it's a stringified JSON
        if "metadata" in parsed and isinstance(parsed["metadata"], str):
            try:
                parsed["metadata"] = json.loads(parsed["metadata"])
            except Exception:
                pass

        # Flatten nested JSON (e.g. metadata)
        flat = json_normalize(parsed, sep=".")
        all_records.append(flat)

    # Concatenate all parsed dataframes
    final_df = pd.concat(all_records, ignore_index=True)

    # Export to Excel
    final_df = final_df.dropna(how="all").reset_index(drop=True)
    final_df.to_excel("./output/wallet_report.xlsx", index=False)
    print("Done. Report saved as wallet_report.xlsx")


if __name__ == "__main__":
    main()
