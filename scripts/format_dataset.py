import os
import json

# ── Configuration ──────────────────────────────────────────────────────────────

INPUT_FILE  = "../data/merged_sft_dataset.jsonl"
OUTPUT_FILE = "../data/formatted_sft_dataset.jsonl"

SYSTEM_PROMPT = (
    "You are an expert C++ Digital Signal Processing (DSP) programming assistant. "
    "Help users understand and implement audio DSP code in C++."
)

# ── ChatML Formatter ───────────────────────────────────────────────────────────

def to_chatml(instruction: str, response: str) -> str:
    """
    Wraps a pair in ChatML format — Qwen-Coder's native training format.
    """
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}\n<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n<|im_end|>\n"
        f"<|im_start|>assistant\n{response}\n<|im_end|>"
    )

# ── I/O Helpers ────────────────────────────────────────────────────────────────

def load_jsonl(filepath: str) -> list[dict]:
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
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")

# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    print("Phase 5 — ChatML Dataset Formatting\n")

    if not os.path.exists(INPUT_FILE):
        print(f"Error: input file not found:\n  {INPUT_FILE}")
        print("Make sure Phase 4 (filter_dataset.py) ran successfully.")
        return

    print(f"Loading from:\n  {INPUT_FILE}")
    pairs = load_jsonl(INPUT_FILE)
    print(f"  Loaded {len(pairs)} pairs\n")

    formatted = []
    skipped   = 0

    for pair in pairs:
        instruction = pair.get("instruction", "").strip()
        response    = pair.get("response", "").strip()

        if not instruction or not response:
            skipped += 1
            continue

        formatted.append({"text": to_chatml(instruction, response)})

    if skipped:
        print(f"  Skipped {skipped} incomplete pairs")

    save_jsonl(formatted, OUTPUT_FILE)

    print(f" Done! {len(formatted)} formatted examples saved to:\n  {OUTPUT_FILE}")
    print(f"\n── Sample record ──────────────────────────────")
    if formatted:
        print(formatted[0]["text"][:500] + "...")


if __name__ == "__main__":
    main()