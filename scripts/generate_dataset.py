import os
import json
import re

# Configuration

INPUT_FILE   = "../data/extracted_dsp_functions.txt"
OUTPUT_FILE  = "../data/generated_instruction_response_pairs.jsonl"
MAX_SNIPPETS = 2000

# Keyword → Instruction Mapping 
# More specific keywords come first — first match wins.

KEYWORD_INSTRUCTIONS = [
    # Filters
    ("lowpass",       "How do I implement a low-pass filter in C++?"),
    ("low_pass",      "How do I implement a low-pass filter in C++?"),
    ("highpass",      "How do I implement a high-pass filter in C++?"),
    ("high_pass",     "How do I implement a high-pass filter in C++?"),
    ("bandpass",      "How do I implement a band-pass filter in C++?"),
    ("band_pass",     "How do I implement a band-pass filter in C++?"),
    ("biquad",        "How do I implement a biquad filter in C++?"),
    ("makelowpass",   "How do I implement a low-pass filter in C++?"),
    ("makehighpass",  "How do I implement a high-pass filter in C++?"),
    ("makebandpass",  "How do I implement a band-pass filter in C++?"),
    ("fir",           "How do I implement a FIR filter in C++?"),
    ("iir",           "How do I implement an IIR filter in C++?"),
    ("filter",        "How do I implement a DSP filter in C++?"),
    # Dynamics
    ("compressor",    "How do I implement a compressor in C++ for audio?"),
    ("limiter",       "How do I implement a limiter in C++ for audio?"),
    ("expander",      "How do I implement an expander/gate in C++ for audio?"),
    ("envelope",      "How do I implement an envelope follower in C++?"),
    ("attacktime",    "How do I implement attack/release smoothing in C++?"),
    ("releasetime",   "How do I implement attack/release smoothing in C++?"),
    ("threshsmooth",  "How do I implement a compressor with smoothing in C++?"),
    # Effects
    ("reverb",        "How do I create a reverb effect in C++?"),
    ("chorus",        "How do I implement a chorus effect in C++?"),
    ("flanger",       "How do I implement a flanger effect in C++?"),
    ("phaser",        "How do I implement a phaser effect in C++?"),
    ("distortion",    "How do I implement a distortion effect in C++?"),
    ("overdrive",     "How do I implement an overdrive effect in C++?"),
    ("bitcrush",      "How do I implement a bitcrusher in C++?"),
    ("convolv",       "How do I implement convolution reverb in C++?"),
    ("delay",         "How do I implement a delay effect in C++ for audio?"),
    # Synthesis
    ("oscillator",    "How do I build an oscillator in C++ for audio synthesis?"),
    ("wavetable",     "How do I implement wavetable synthesis in C++?"),
    ("lfo",           "How do I implement an LFO in C++?"),
    ("adsr",          "How do I implement an ADSR envelope in C++?"),
    ("synth",         "How do I build a synthesizer component in C++?"),
    # Frequency domain
    ("fft",           "How do I perform an FFT in C++ for audio processing?"),
    ("ifft",          "How do I perform an inverse FFT in C++?"),
    ("freqdomain",    "How do I work with frequency domain audio data in C++?"),
    ("timedomain",    "How do I work with time domain audio data in C++?"),
    ("spectrum",      "How do I analyze the frequency spectrum of audio in C++?"),
    # Utilities
    ("equalizer",     "How do I implement an equalizer in C++?"),
    ("decibels",      "How do I convert between decibels and gain in C++?"),
    ("decibelstogain","How do I convert decibels to gain in C++?"),
    ("gain",          "How do I apply gain to an audio signal in C++?"),
    ("volume",        "How do I control the volume of an audio signal in C++?"),
    ("panning",       "How do I implement stereo panning in C++?"),
    ("pan",           "How do I implement stereo panning in C++?"),
    ("mixer",         "How do I implement an audio mixer in C++?"),
    ("resample",      "How do I implement audio resampling in C++?"),
    ("interpolat",    "How do I implement audio interpolation in C++?"),
    ("pitch",         "How do I implement pitch shifting in C++?"),
    ("noise",         "How do I implement noise shaping in C++?"),
    ("smoothed",      "How do I apply parameter smoothing in C++?"),
    ("setramplength", "How do I apply parameter smoothing in C++?"),
    ("audiobuffer",   "How do I work with audio buffers in C++?"),
    ("audioblock",    "How do I work with audio blocks in C++?"),
    ("processblock",  "How do I implement a processBlock function in C++?"),
    ("processsample", "How do I process individual audio samples in C++?"),
]

FALLBACK_INSTRUCTION = "Explain this C++ DSP function and how it works."

# Helpers 

def get_instruction(code: str) -> str:
    """Matches keywords against function names first, then full code."""
    lowered = code.lower()

    # Extract all function names for precise matching
    func_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    func_name_str = " ".join(func_names).lower()

    # Match function names first (most precise)
    for keyword, instruction in KEYWORD_INSTRUCTIONS:
        if keyword in func_name_str:
            return instruction

    # Then match full code body
    for keyword, instruction in KEYWORD_INSTRUCTIONS:
        if keyword in lowered:
            return instruction

    return FALLBACK_INSTRUCTION


def get_response(code: str) -> str:
    """Returns cleaned code with an auto-generated description comment."""
    code = code.strip()

    # Find the most meaningful function name
    boilerplate = {
        "pinParameter", "getChunk", "setChunk",
        "getParameter", "setParameter", "prepare",
    }
    matches = re.findall(r'(void|float|double|int|bool|auto)\s+(\w+)\s*\(', code)
    func_name = None
    for _, name in matches:
        if name not in boilerplate:
            func_name = name
            break

    if func_name:
        readable = re.sub(r'([A-Z])', r' \1', func_name).replace("_", " ").strip().lower()
        description = f"// This implements `{func_name}` — a C++ DSP routine for {readable}."
    else:
        description = "// This C++ snippet implements a DSP routine for audio processing."

    return f"{code}\n\n{description}"


def load_snippets(filepath: str) -> list[str]:
    """Reads and splits the extracted snippets file."""
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    return [s.strip() for s in raw.split("---") if s.strip()]


def save_jsonl(data: list[dict], filepath: str) -> None:
    """Saves pairs to a JSONL file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")

# Entry Point

def main():
    print("Phase 3 — Instruction-Response Pair Generation\n")

    if not os.path.exists(INPUT_FILE):
        print(f"Error: input file not found:\n  {INPUT_FILE}")
        print("Make sure Phase 2 (extract_dsp.py) ran successfully.")
        return

    snippets   = load_snippets(INPUT_FILE)
    to_process = snippets[:MAX_SNIPPETS]
    print(f"Loaded {len(snippets)} snippets. Processing {len(to_process)}.\n")

    dataset   = []
    fallbacks = 0

    for i, snippet in enumerate(to_process, start=1):
        instruction = get_instruction(snippet)
        response    = get_response(snippet)

        if instruction == FALLBACK_INSTRUCTION:
            fallbacks += 1

        dataset.append({"instruction": instruction, "response": response})

        if i % 200 == 0:
            print(f"  Processed {i}/{len(to_process)}...")

    save_jsonl(dataset, OUTPUT_FILE)

    print(f"\n Done!")
    print(f"   Total pairs generated  : {len(dataset)}")
    print(f"   Keyword matched        : {len(dataset) - fallbacks}")
    print(f"   Fallback (generic)     : {fallbacks}")
    print(f"   Saved to               : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()