import os
import json

#  Configuration

INPUT_FILE  = "../data/final_sft_dataset.jsonl"
OUTPUT_FILE = "../data/formatted_sft_dataset.jsonl"

SYSTEM_PROMPT = "You are an expert C++ Digital Signal Processing (DSP) programming assistant. Help users understand and implement audio DSP code in C++."

#  Formatter 
def to_chatml(instruction: str, response: str, system: str = SYSTEM_PROMPT) -> str:
    """
    Wraps an instruction-response pair in ChatML format.
    This is the native format Qwen-Coder was trained on.

    Structure:
        <|im_start|>system
        {system prompt}
        <|im_end|>
        <|im_start|>user
        {instruction}
        <|im_end|>
        <|im_start|>assistant
        {response}
        <|im_end|>
    """
    return (
        f"<|im_start|>system\n{system}\n<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n<|im_end|>\n"
        f"<|im_start|>assistant\n{response}\n<|im_end|>"
    )

#  I/O helpers 

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

#  Entry point 
def main():
    # 1. Load filtered dataset
    if not os.path.exists(INPUT_FILE):
        print(f"Error: input file not found:\n  {INPUT_FILE}")
        print("Make sure Phase 4 (filter_dataset.py) ran successfully.")
        return

    print(f"Loading dataset from:\n  {INPUT_FILE}")
    pairs = load_jsonl(INPUT_FILE)
    print(f"  Loaded {len(pairs)} pairs\n")

    # 2. Format each pair into ChatML
    formatted = []
    skipped   = 0

    for pair in pairs:
        instruction = pair.get("instruction", "").strip()
        response    = pair.get("response", "").strip()

        if not instruction or not response:
            skipped += 1
            continue

        formatted.append({
            "text": to_chatml(instruction, response)  # Single "text" field — what Unsloth expects
        })

    if skipped:
        print(f"  Skipped {skipped} incomplete pairs")

    # 3. Save
    save_jsonl(formatted, OUTPUT_FILE)
    print(f"✅ Done! {len(formatted)} formatted examples saved to:\n  {OUTPUT_FILE}")
    print(f"\nSample output (first record):\n")
    print(formatted[0]["text"] if formatted else "No records to show.")


if __name__ == "__main__":
    main()