import os
import json

# Configuration 

INPUT_FILE  = "../data/generated_instruction_response_pairs.jsonl"
OUTPUT_FILE = "../data/final_sft_dataset.jsonl"

# Quality thresholds (tweak these if needed)
MIN_RESPONSE_LENGTH = 50    # Minimum characters in a response
MAX_RESPONSE_LENGTH = 5000  # Maximum characters (avoids bloated snippets)
MIN_INSTRUCTION_WORDS = 4   # Instruction must have at least 4 words

# Quality checks 

def is_valid(pair: dict) -> tuple[bool, str]:
    """
    Runs quality checks on a single instruction-response pair.
    Returns (True, "") if valid, or (False, reason) if it should be filtered out.
    """
    instruction = pair.get("instruction", "").strip()
    response    = pair.get("response", "").strip()

    if not instruction or not response:
        return False, "Missing instruction or response"

    if len(instruction.split()) < MIN_INSTRUCTION_WORDS:
        return False, f"Instruction too short: '{instruction}'"

    if len(response) < MIN_RESPONSE_LENGTH:
        return False, f"Response too short ({len(response)} chars)"

    if len(response) > MAX_RESPONSE_LENGTH:
        return False, f"Response too long ({len(response)} chars)"

    # Must contain at least one C++ indicator
    cpp_indicators = ["{", "}", "()", "return", "int ", "float ", "void ", "//", "#include"]
    if not any(indicator in response for indicator in cpp_indicators):
        return False, "Response does not look like C++ code"

    return True, ""

# ── I/O helpers────────────────────────────────────────────────────

def load_jsonl(filepath: str) -> list[dict]:
    """Loads all records from a JSONL file."""
    pairs = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    pairs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"  ⚠  Skipping malformed line: {e}")
    return pairs


def save_jsonl(data: list[dict], filepath: str) -> None:
    """Saves a list of dicts to a JSONL file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")

# Pipeline steps

def deduplicate(pairs: list[dict]) -> list[dict]:
    """Removes pairs with duplicate instructions (keeps first occurrence)."""
    seen        = set()
    unique      = []
    duplicates  = 0
    for pair in pairs:
        key = pair.get("instruction", "").strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(pair)
        else:
            duplicates += 1
    print(f"  Deduplication : removed {duplicates} duplicates → {len(unique)} remaining")
    return unique


def quality_filter(pairs: list[dict]) -> list[dict]:
    """Filters out pairs that fail quality checks."""
    passed  = []
    removed = 0
    for pair in pairs:
        valid, reason = is_valid(pair)
        if valid:
            passed.append(pair)
        else:
            removed += 1
            # Uncomment the line below to see exactly what was filtered and why:
            # print(f"    Filtered → {reason}")
    print(f"  Quality filter: removed {removed} pairs → {len(passed)} remaining")
    return passed

# Entry point

def main():
    # 1. Load
    if not os.path.exists(INPUT_FILE):
        print(f"Error: input file not found:\n  {INPUT_FILE}")
        print("Make sure Phase 3 ran successfully and the file exists.")
        return

    print(f"Loading pairs from:\n  {INPUT_FILE}")
    pairs = load_jsonl(INPUT_FILE)
    print(f"  Loaded {len(pairs)} total pairs\n")

    # 2. Deduplicate
    pairs = deduplicate(pairs)

    # 3. Quality filter
    pairs = quality_filter(pairs)

    # 4. Save
    save_jsonl(pairs, OUTPUT_FILE)
    print(f"\n✅ Done! Final dataset: {len(pairs)} high-quality pairs saved to:\n  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()