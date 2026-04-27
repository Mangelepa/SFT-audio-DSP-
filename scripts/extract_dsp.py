import os
import subprocess
import re

# GitHub repositories
repos = {
    "Surge": "https://github.com/surge-synthesizer/surge.git",
    "ChowDS": "https://github.com/Chowdhury-DSP/chowdsp_utils.git",
    "Airwindows": "https://github.com/airwindows/airwindows.git",
    "Vital": "https://github.com/mtytel/vital.git",
    "JUCE": "https://github.com/juce-framework/JUCE.git"
}

# Folders
repo_folder = "repos"
output_file = "extracted_dsp_functions.txt"

os.makedirs(repo_folder, exist_ok=True)

# Clone repositories
for name, url in repos.items():
    path = os.path.join(repo_folder, name)

    if not os.path.exists(path):
        print(f"Cloning {name}...")
        subprocess.run(["git", "clone", "--depth", "1", url, path])
    else:
        print(f"{name} already downloaded.")

#Extract DSP snippets
pattern = re.compile(
    r"(void|float|double|int|bool)\s+\w+\s*\([^)]*\)\s*\{",
    re.MULTILINE
)

results = []

for root, dirs, files in os.walk(repo_folder):
    for file in files:

        if file.endswith((".cpp", ".h", ".hpp")):

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

                    matches = pattern.finditer(text)

                    for match in matches:
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 400)

                        snippet = text[start:end]

                        results.append(
                            f"FILE: {file_path}\n"
                            f"{'-'*50}\n"
                            f"{snippet}\n\n"
                        )

            except:
                pass

# Save output
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(results)

print(f"Done. Extracted {len(results)} snippets.")
print(f"Saved to {output_file}")