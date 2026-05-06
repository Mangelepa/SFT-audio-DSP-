import os
import json

# ── Configuration ──────────────────────────────────────────────────────────────

HANDCRAFTED_FILE = "../data/handcrafted_pairs.jsonl"
EXTRACTED_FILE   = "../data/final_sft_dataset.jsonl"
OUTPUT_FILE      = "../data/merged_sft_dataset.jsonl"

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_jsonl(filepath: str) -> list[dict]:
    pairs = []
    if not os.path.exists(filepath):
        print(f"  ⚠  File not found, skipping: {filepath}")
        return pairs
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    pairs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return pairs


def save_jsonl(data: list[dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")

# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    print("Merging handcrafted and extracted pairs...\n")

    handcrafted = load_jsonl(HANDCRAFTED_FILE)
    extracted   = load_jsonl(EXTRACTED_FILE)

    print(f"  Handcrafted pairs : {len(handcrafted)}")
    print(f"  Extracted pairs   : {len(extracted)}")

    # Deduplicate by instruction — handcrafted takes priority
    seen   = set()
    merged = []

    for pair in handcrafted + extracted:
        key = pair.get("instruction", "").strip().lower()
        if key not in seen:
            seen.add(key)
            merged.append(pair)

    save_jsonl(merged, OUTPUT_FILE)

    print(f"\n Merged dataset: {len(merged)} total pairs")
    print(f"   Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()