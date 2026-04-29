import os
import json
import re

# ── Configuration ──────────────────────────────────────────────────────────────

INPUT_FILE   = "../data/extracted_dsp_functions.txt"
OUTPUT_FILE  = "../data/generated_instruction_response_pairs.jsonl"
MAX_SNIPPETS = 200

# ── Keyword → Instruction mapping ─────────────────────────────────────────────
# Each entry is (keyword, instruction).
# The FIRST matching keyword wins, so put more specific ones first.

KEYWORD_INSTRUCTIONS = [
    # Filters
    ("lowpass",       "How do I implement a low-pass filter in C++?"),
    ("low_pass",      "How do I implement a low-pass filter in C++?"),
    ("highpass",      "How do I implement a high-pass filter in C++?"),
    ("high_pass",     "How do I implement a high-pass filter in C++?"),
    ("bandpass",      "How do I implement a band-pass filter in C++?"),
    ("band_pass",     "How do I implement a band-pass filter in C++?"),
    ("biquad",        "How do I implement a biquad filter in C++?"),
    ("filter",        "How do I implement a DSP filter in C++?"),

    # Dynamics
    ("compressor",    "How do I implement a compressor in C++ for audio?"),
    ("limiter",       "How do I implement a limiter in C++ for audio?"),
    ("expander",      "How do I implement an expander/gate in C++ for audio?"),
    ("envelope",      "How do I implement an envelope follower in C++?"),

    # Effects
    ("reverb",        "How do I create a reverb effect in C++?"),
    ("chorus",        "How do I implement a chorus effect in C++?"),
    ("flanger",       "How do I implement a flanger effect in C++?"),
    ("phaser",        "How do I implement a phaser effect in C++?"),
    ("distortion",    "How do I implement a distortion effect in C++?"),
    ("overdrive",     "How do I implement an overdrive effect in C++?"),
    ("bitcrush",      "How do I implement a bitcrusher in C++?"),
    ("delay",         "How do I implement a delay effect in C++ for audio?"),

    # Synthesis
    ("oscillator",    "How do I build an oscillator in C++ for audio synthesis?"),
    ("wavetable",     "How do I implement wavetable synthesis in C++?"),
    ("lfo",           "How do I implement an LFO (Low Frequency Oscillator) in C++?"),
    ("adsr",          "How do I implement an ADSR envelope in C++?"),
    ("synth",         "How do I build a synthesizer component in C++?"),

    # Frequency domain
    ("fft",           "How do I perform an FFT in C++ for audio processing?"),
    ("ifft",          "How do I perform an inverse FFT in C++?"),
    ("spectrum",      "How do I analyze the frequency spectrum of audio in C++?"),
    ("windowing",     "How do I apply a windowing function to audio data in C++?"),

    # Utilities
    ("equalizer",     "How do I implement an equalizer (EQ) in C++?"),
    ("eq",            "How do I implement an equalizer (EQ) in C++?"),
    ("gain",          "How do I apply gain to an audio signal in C++?"),
    ("volume",        "How do I control the volume of an audio signal in C++?"),
    ("panning",       "How do I implement stereo panning in C++?"),
    ("pan",           "How do I implement stereo panning in C++?"),
    ("mixer",         "How do I implement an audio mixer in C++?"),
    ("resample",      "How do I implement audio resampling in C++?"),
    ("interpolat",    "How do I implement audio interpolation in C++?"),
    ("pitch",         "How do I implement pitch shifting in C++?"),
    ("tuner",         "How do I implement a tuner/pitch detector in C++?"),
    ("noise",         "How do I generate or reduce noise in C++ audio processing?"),
    ("buffer",        "How do I manage audio buffers in C++?"),
    ("sample",        "How do I process audio samples in C++?"),
    ("waveform",      "How do I work with audio waveforms in C++?"),
    ("clip",          "How do I implement audio clipping in C++?"),
    ("smooth",        "How do I apply smoothing to an audio signal in C++?"),
]

FALLBACK_INSTRUCTION = "Explain this C++ DSP function and how it works."

# ── Instruction builder ────────────────────────────────────────────────────────

def get_instruction(code: str) -> str:
    """
    Scans the code for known DSP keywords and returns a matching instruction.
    Also checks function names extracted from the code for better accuracy.
    Falls back to a generic instruction if nothing matches.
    """
    lowered = code.lower()

    # First try to extract and match the function name specifically
    func_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    func_name_str = " ".join(func_names).lower()

    # Check function names first (more specific), then full code
    for keyword, instruction in KEYWORD_INSTRUCTIONS:
        if keyword in func_name_str:
            return instruction

    for keyword, instruction in KEYWORD_INSTRUCTIONS:
        if keyword in lowered:
            return instruction

    return FALLBACK_INSTRUCTION


def get_response(code: str) -> str:
    """
    Builds the response: the cleaned code snippet plus a short auto-generated description.
    """
    code = code.strip()

    # Try to extract the first function signature for the description
    match = re.search(r'([\w\s\*&<>:]+)\s+(\w+)\s*\(([^)]*)\)', code)
    if match:
        func_name = match.group(2)
        # Convert camelCase / snake_case to readable words
        readable = re.sub(r'([A-Z])', r' \1', func_name)          # camelCase
        readable = readable.replace("_", " ").strip().lower()      # snake_case
        description = f"This function implements `{func_name}` — a C++ DSP routine for {readable}."
    else:
        description = "This C++ snippet implements a DSP routine for audio processing."

    return f"{code}\n\n// {description}"

# ── I/O helpers ────────────────────────────────────────────────────────────────

def load_snippets(filepath: str) -> list[str]:
    """Reads the input file and splits it into individual code snippets."""
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    return [s.strip() for s in raw.split("---") if s.strip()]


def save_jsonl(data: list[dict], filepath: str) -> None:
    """Saves a list of dicts to a JSONL file (one JSON object per line)."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")

# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    # 1. Validate input
    if not os.path.exists(INPUT_FILE):
        print(f"Error: input file not found:\n  {INPUT_FILE}")
        print("Make sure Phase 2 (extract_dsp.py) ran successfully.")
        return

    # 2. Load snippets
    snippets = load_snippets(INPUT_FILE)
    to_process = snippets[:MAX_SNIPPETS]
    print(f"Loaded {len(snippets)} snippets. Processing {len(to_process)}.\n")

    # 3. Generate pairs
    dataset   = []
    fallbacks = 0

    for i, snippet in enumerate(to_process, start=1):
        instruction = get_instruction(snippet)
        response    = get_response(snippet)

        if instruction == FALLBACK_INSTRUCTION:
            fallbacks += 1

        dataset.append({"instruction": instruction, "response": response})

        if i % 50 == 0:
            print(f"  Processed {i}/{len(to_process)}...")

    # 4. Save
    save_jsonl(dataset, OUTPUT_FILE)

    print(f"\n Done!")
    print(f"   Total pairs generated : {len(dataset)}")
    print(f"   Keyword matched        : {len(dataset) - fallbacks}")
    print(f"   Fallback (generic)     : {fallbacks}")
    print(f"   Saved to               : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()