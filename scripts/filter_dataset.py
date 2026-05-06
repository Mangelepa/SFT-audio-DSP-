import os
import json
import re

# ── Configuration ──────────────────────────────────────────────────────────────

INPUT_FILE  = "../data/generated_instruction_response_pairs.jsonl"
OUTPUT_FILE = "../data/final_sft_dataset.jsonl"

MIN_RESPONSE_CHARS    = 100
MAX_RESPONSE_CHARS    = 8000
MIN_INSTRUCTION_WORDS = 4
MIN_CODE_LINES        = 4

# ── DSP Validation ─────────────────────────────────────────────────────────────

DSP_KEYWORDS = [
    "filter", "oscillator", "reverb", "delay", "chorus", "flanger", "phaser",
    "distortion", "overdrive", "compressor", "limiter", "envelope", "adsr",
    "lfo", "fft", "ifft", "biquad", "lowpass", "highpass", "bandpass",
    "gain", "volume", "panning", "pan", "mixer", "pitch", "noise", "waveshap",
    "wavetable", "resample", "interpolat", "equalizer", "spectrum",
    "samplerate", "sample_rate", "inputsample", "outputsample", "feedback",
    "cutoff", "resonance", "frequency", "amplitude", "smoothed",
    "setramplength", "makelowpass", "makehighpass", "makebandpass",
    "decibels", "decibelstogain", "audiobuffer", "audioblock",
    "processsample", "processblock", "threshsmooth", "attacktime",
    "releasetime", "linearphase", "delaykernel", "freqdomain",
    "timedomain", "convolv", "dsp::", "juce::dsp", "wetdry",
    "drysignal", "wetsignal", "fir", "iir",
]

NON_DSP_FUNCTION_NAMES = {
    "isdivider", "autoscrollformouseevent", "getprogramname",
    "setprogramname", "geteffectname", "getvendorstring",
    "getproductstring", "pinparameter", "getchunk", "setchunk",
    "main", "setrule",
}

TRUNCATION_MARKERS = [
    "ng point", "atic void", "atic auto", "atic bool", "atic float",
    "atic int", "line bool", "line void", "unc>", "====",
    "hreshold", "}\n}\n", "} }\n", "}}\n",
]

# ── Quality Check ──────────────────────────────────────────────────────────────

def is_valid(pair: dict) -> tuple[bool, str]:
    instruction = pair.get("instruction", "").strip()
    response    = pair.get("response", "").strip()

    if not instruction or not response:
        return False, "Missing instruction or response"

    if len(instruction.split()) < MIN_INSTRUCTION_WORDS:
        return False, "Instruction too short"

    if len(response) < MIN_RESPONSE_CHARS:
        return False, f"Response too short ({len(response)} chars)"

    if len(response) > MAX_RESPONSE_CHARS:
        return False, f"Response too long ({len(response)} chars)"

    code_lines = [l for l in response.splitlines() if l.strip()]
    if len(code_lines) < MIN_CODE_LINES:
        return False, f"Too few lines ({len(code_lines)})"

    for marker in TRUNCATION_MARKERS:
        if response.startswith(marker):
            return False, "Truncated response"

    cpp_constructs = ["{", "}", "return ", "void ", "float ", "double ", "int "]
    if not any(c in response for c in cpp_constructs):
        return False, "Not C++ code"

    func_match = re.search(r'(void|float|double|int|bool|auto)\s+(\w+)\s*\(', response)
    if func_match:
        func_name = func_match.group(2).lower()
        if func_name in NON_DSP_FUNCTION_NAMES:
            return False, f"Non-DSP function: '{func_name}'"

    lowered = response.lower()
    if not any(keyword in lowered for keyword in DSP_KEYWORDS):
        return False, "No DSP content found"

    return True, ""

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

# ── Pipeline Steps ─────────────────────────────────────────────────────────────

def deduplicate(pairs: list[dict]) -> list[dict]:
    seen       = set()
    unique     = []
    duplicates = 0
    for pair in pairs:
        key = pair.get("instruction", "").strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(pair)
        else:
            duplicates += 1
    print(f"  Deduplication  : removed {duplicates} duplicates → {len(unique)} remaining")
    return unique


def quality_filter(pairs: list[dict]) -> list[dict]:
    passed  = []
    removed = 0
    reasons = {}
    for pair in pairs:
        valid, reason = is_valid(pair)
        if valid:
            passed.append(pair)
        else:
            removed += 1
            key = reason.split("(")[0].strip()
            reasons[key] = reasons.get(key, 0) + 1

    print(f"  Quality filter : removed {removed} pairs → {len(passed)} remaining")
    print(f"\n  Rejection breakdown:")
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"    {count:3}x  {reason}")
    return passed

# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    print("Phase 4 — Quality Filtering & Deduplication\n")

    if not os.path.exists(INPUT_FILE):
        print(f"Error: input file not found:\n  {INPUT_FILE}")
        return

    print(f"Loading pairs from:\n  {INPUT_FILE}\n")
    pairs = load_jsonl(INPUT_FILE)
    print(f"  Loaded {len(pairs)} total pairs\n")

    pairs = deduplicate(pairs)
    pairs = quality_filter(pairs)

    save_jsonl(pairs, OUTPUT_FILE)
    print(f"\n Done! {len(pairs)} clean pairs saved to:\n  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()