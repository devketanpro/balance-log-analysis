import os
import gzip
import re
import pandas as pd
import json

base_path = "./data/balance-sync-logs/a3fb6cdb-607b-469f-8f8a-ec4792e827cb"
output_csv = "./output/cleaned_transactions.csv"

# Regex patterns
transaction_start_pattern = re.compile(r"transaction:\s*\{")
timestamp_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")


# ===== FUNCTIONS =====
def parse_transaction_block(block):
    """
    Convert a JS-style transaction object to a Python dictionary.
    """
    try:
        # Ensure JS keys are quoted for JSON
        block = block.replace("'", '"')
        block = re.sub(r"(\b[a-zA-Z_][a-zA-Z0-9_]*\b)\s*:", r'"\1":', block)
        return json.loads(block)
    except Exception as e:
        return {"_error": str(e), "_raw": block}


def parse_raw_json(raw_str):
    """
    Parse nested JSON safely.
    """
    try:
        if isinstance(raw_str, str):
            raw_str = raw_str.strip().strip('"')
            raw_str = raw_str.replace('"{', "{").replace('}"', "}")
            raw_str = raw_str.replace('\\"', '"')
            return json.loads(raw_str)
        return raw_str if isinstance(raw_str, dict) else {}
    except Exception as e:
        return {"_error": str(e), "_raw": raw_str}


def extract_transaction_blocks(lines):
    """
    Extract transaction blocks and attach timestamps.
    """
    transactions = []
    capturing = False
    buffer = ""
    open_braces = 0
    current_timestamp = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Capture timestamp for this transaction
        ts_match = timestamp_pattern.match(line)
        if ts_match:
            current_timestamp = ts_match.group(1)

        # Detect start of transaction block
        if not capturing and transaction_start_pattern.search(line):
            capturing = True
            buffer = line[line.find("{") :]
            open_braces = buffer.count("{") - buffer.count("}")
            continue

        # Continue capturing block
        if capturing:
            buffer += " " + line
            open_braces += line.count("{") - line.count("}")

            if open_braces == 0:  # End of block
                parsed_block = parse_transaction_block(buffer)
                parsed_nested = parse_raw_json(parsed_block.get("_raw", parsed_block))
                merged = {
                    **parsed_block,
                    **parsed_nested,
                }  # Merge if nested JSON exists
                merged["timestamp"] = current_timestamp
                transactions.append(merged)
                capturing = False
                buffer = ""
                current_timestamp = None

    return transactions


def collect_gz_files(path):
    """
    Recursively collect all .gz files under the given path.
    """
    gz_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".gz"):
                gz_files.append(os.path.join(root, file))
    return gz_files


def read_lines_from_gz(files):
    """
    Read all lines from a list of .gz files.
    """
    lines = []
    for file_path in files:
        try:
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                lines.extend(f.readlines())
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return lines


# MAIN EXECUTION
if __name__ == "__main__":
    gz_files = collect_gz_files(base_path)
    all_lines = read_lines_from_gz(gz_files)
    transaction_blocks = extract_transaction_blocks(all_lines)

    df = pd.DataFrame(transaction_blocks)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Extracted {len(df)} transactions to {output_csv}")
