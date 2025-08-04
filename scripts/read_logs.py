import os
import gzip
import re
import pandas as pd
import json

# Paths
base_path = "./data/balance-sync-logs/a3fb6cdb-607b-469f-8f8a-ec4792e827cb"
output_csv = "./output/cleaned_transactions.csv"

# Regex patterns
transaction_start_pattern = re.compile(r"^transaction:\s*\{")


def extract_transaction_blocks(lines):
    """
    Extract 'transaction: { ... }' blocks from log lines.
    """
    transactions = []
    capturing = False
    buffer = ""
    open_braces = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if not capturing and transaction_start_pattern.match(line):
            capturing = True
            buffer = line[line.find("{") :]
            open_braces = buffer.count("{") - buffer.count("}")
            continue

        if capturing:
            buffer += " " + line
            open_braces += line.count("{") - line.count("}")
            if open_braces == 0:
                transactions.append(buffer)
                capturing = False
                buffer = ""

    return transactions


def parse_transaction_block(block):
    """
    Convert a JS-style object block to a Python dictionary.
    """
    try:
        block = block.replace("'", '"')
        block = re.sub(r"(\b[a-zA-Z_][a-zA-Z0-9_]*\b)\s*:", r'"\1":', block)
        return json.loads(block)
    except Exception as e:
        return {"_error": str(e), "_raw": block}


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


# Main execution
gz_files = collect_gz_files(base_path)
all_lines = read_lines_from_gz(gz_files)
transaction_blocks = extract_transaction_blocks(all_lines)
parsed_transactions = [parse_transaction_block(block) for block in transaction_blocks]

df = pd.DataFrame(parsed_transactions)
df.to_csv(output_csv, index=False)
