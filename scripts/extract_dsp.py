import os
import subprocess
import re

#Configuration 

REPOS = {
    "Surge":      "https://github.com/surge-synthesizer/surge.git",
    "ChowDSP":    "https://github.com/Chowdhury-DSP/chowdsp_utils.git",
    "Airwindows": "https://github.com/airwindows/airwindows.git",
    "Vital":      "https://github.com/mtytel/vital.git",
    "JUCE":       "https://github.com/juce-framework/JUCE.git",
    "Maximilian":  "https://github.com/micknoise/Maximilian.git",       
    "Q":           "https://github.com/cycfi/q.git",                     # Audio DSP library
    "AudioFFT":    "https://github.com/HiFi-LoFi/AudioFFT.git",          # FFT processing
    "KFR":         "https://github.com/kfrlib/kfr.git",                  # DSP framework
    "RTAudio":     "https://github.com/thestk/rtaudio.git",              # Real-time audio
    "STK":         "https://github.com/thestk/stk.git",                  # Synthesis toolkit
    "Bela":        "https://github.com/BelaPlatform/Bela.git",           # Real-time audio DSP
    "FaustLibs":   "https://github.com/grame-cncm/faustlibraries.git",  # DSP algorithms
    "OwlProgram":  "https://github.com/pingdynasty/OwlProgram.git",      # DSP patches
    "AudioTK":     "https://github.com/mbrucher/AudioTK.git",            # Audio toolkit
}

REPO_FOLDER  = "../src/repos"
OUTPUT_FILE  = "../data/extracted_dsp_functions.txt"
MAX_SNIPPETS = 20000

# DSP Relevance

# Snippet must contain at least one of these to be kept
DSP_KEYWORDS = [
    "filter", "oscillator", "reverb", "delay", "chorus", "flanger", "phaser",
    "distortion", "overdrive", "compressor", "limiter", "envelope", "adsr",
    "lfo", "fft", "ifft", "biquad", "lowpass", "highpass", "bandpass",
    "gain", "volume", "panning", "pitch", "noise", "waveshap", "wavetable",
    "resample", "interpolat", "equalizer", "spectrum", "samplerate",
    "sample_rate", "inputsample", "outputsample", "feedback", "cutoff",
    "resonance", "frequency", "amplitude", "smoothed", "setramplength",
    "decibels", "audiobuffer", "audioblock", "processsample", "processblock",
    "attacktime", "releasetime", "freqdomain", "timedomain", "convolv",
    "dsp::", "juce::dsp", "wetdry", "drysignal", "wetsignal",
]

# Functions with these names are pure boilerplate — skip entirely
SKIP_FUNCTION_NAMES = {
    "main", "pinparameter", "getchunk", "setchunk",
    "getparameter", "setparameter", "getprogramname",
    "setprogramname", "geteffectname", "getvendorstring",
    "getproductstring", "canparameterbeautomated",
    "getparameterproperties", "isdivider",
    "autoscrollformouseevent", "setrule",
}

# Skip these folders — they contain no real DSP code
SKIP_DIRS = {
    "test", "tests", "build", "cmake", "docs", "examples",
    "thirdparty", "third_party", "extern", "external",
}

# Extraction Pattern 

FUNC_PATTERN = re.compile(
    r"(void|float|double|int|bool|auto)\s+"   # return type
    r"(\w+)"                                   # function name
    r"\s*\([^)]{0,200}\)"                      # parameters
    r"\s*\{",                                  # opening brace
    re.MULTILINE
)

# Helpers 

def extract_function_body(text: str, match_start: int) -> str | None:
    """
    Extracts a complete function by tracking brace depth.
    Returns the full function text or None if incomplete.
    """
    brace_pos = text.find("{", match_start)
    if brace_pos == -1:
        return None

    depth = 0
    end   = brace_pos

    for i in range(brace_pos, min(len(text), brace_pos + 6000)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    else:
        return None  # Function body never closed

    # Walk back to include the full function signature
    sig_start = text.rfind("\n", 0, match_start)
    sig_start = max(0, sig_start)
    body = text[sig_start:end].strip()

    # Reject if too short or too long
    if len(body) < 100 or len(body) > 8000:
        return None

    return body


def is_dsp_relevant(snippet: str) -> bool:
    """Returns True only if the snippet contains DSP-related content."""
    lowered = snippet.lower()
    return any(keyword in lowered for keyword in DSP_KEYWORDS)


def clone_repos():
    """Clones all repositories if not already present."""
    os.makedirs(REPO_FOLDER, exist_ok=True)
    for name, url in REPOS.items():
        path = os.path.join(REPO_FOLDER, name)
        if not os.path.exists(path):
            print(f"  Cloning {name}...")
            subprocess.run(["git", "clone", "--depth", "1", url, path], check=False)
        else:
            print(f"  {name} already downloaded.")


def extract_snippets() -> list[str]:
    """Walks all repos and extracts clean, complete, DSP-relevant functions."""
    snippets = []
    seen     = set()

    for root, dirs, files in os.walk(REPO_FOLDER):
        # Skip irrelevant folders in-place
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS]

        for filename in files:
            if not filename.endswith((".cpp", ".h", ".hpp")):
                continue

            filepath = os.path.join(root, filename)

            try:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue

            for match in FUNC_PATTERN.finditer(text):
                if len(snippets) >= MAX_SNIPPETS:
                    return snippets

                func_name = match.group(2).lower()

                # Skip known boilerplate functions
                if func_name in SKIP_FUNCTION_NAMES:
                    continue

                # Extract complete function body using brace tracking
                body = extract_function_body(text, match.start())
                if body is None:
                    continue

                # Skip if not DSP-related
                if not is_dsp_relevant(body):
                    continue

                # Deduplicate
                key = func_name + body[:80]
                if key in seen:
                    continue
                seen.add(key)

                snippets.append(body)

    return snippets


def save_snippets(snippets: list[str], filepath: str):
    """Saves snippets separated by --- delimiter."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for snippet in snippets:
            f.write(snippet + "\n---\n")

# Entry Point 

def main():
    print("Phase 2 — DSP Function Extraction\n")

    print("Step 1: Cloning repositories...")
    clone_repos()

    print("\nStep 2: Extracting DSP functions...")
    snippets = extract_snippets()

    print("\nStep 3: Saving snippets...")
    save_snippets(snippets, OUTPUT_FILE)

    print(f"\n Done!")
    print(f"   Extracted : {len(snippets)} clean DSP snippets")
    print(f"   Saved to  : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()