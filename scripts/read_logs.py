import os
import gzip
import re
import pandas as pd

base_path = "./data/balance-sync-logs/a3fb6cdb-607b-469f-8f8a-ec4792e827cb"
output_csv = "./output/cleaned_transactions.csv"

# Regex pattern to extract transaction blocks
transaction_start = re.compile(r"^transaction:\s*\{")
brace_line = re.compile(r"[{}]")

def extract_transactions_from_lines(lines):
    """Extract multiline 'transaction: { ... }' blocks."""
    transactions = []
    capture = False
    buffer = ""
    open_braces = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if not capture and transaction_start.match(line):
            capture = True
            buffer = line[line.find("{"):]
            open_braces = buffer.count("{") - buffer.count("}")
            continue

        if capture:
            buffer += " " + line
            open_braces += line.count("{") - line.count("}")
            if open_braces == 0:
                transactions.append(buffer)
                capture = False
                buffer = ""

    return transactions

def convert_transaction_block_to_dict(block):
    """Convert JS-style object to Python dict."""
    try:
        block = block.replace("'", '"')
        block = re.sub(r'(\b[a-zA-Z_][a-zA-Z0-9_]*\b)\s*:', r'"\1":', block)
        return pd.json.loads(block)
    except Exception as e:
        return {"_error": str(e), "_raw": block}

# Step 1: Collect all .gz files recursively
gz_files = []
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".gz"):
            gz_files.append(os.path.join(root, file))

print(f"📦 Found {len(gz_files)} .gz files.")

# Step 2: Read and collect all lines
all_lines = []
for file_path in gz_files:
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            all_lines.extend(f.readlines())
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

# Step 3: Extract and convert transactions
transaction_blocks = extract_transactions_from_lines(all_lines)
print(f"🧾 Found {len(transaction_blocks)} transaction blocks.")

parsed_data = [convert_transaction_block_to_dict(block) for block in transaction_blocks]
df = pd.DataFrame(parsed_data)

# Step 4: Save to CSV only
df.to_csv(output_csv, index=False)
print(f"✅ Transactions written to CSV: {output_csv}")
