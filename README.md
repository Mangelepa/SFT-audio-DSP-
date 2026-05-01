# SFT Dataset for Audio DSP Model 

## Project Overview

This project focuses on building a **Supervised Fine-Tuning (SFT) dataset** for an AI coding model specialized in **Audio Digital Signal Processing (DSP)** using **C++ source code** extracted from open-source audio frameworks and synthesizer repositories.

The objective is to create a high-quality dataset that can later be used to fine-tune open-source code models (e.g., Qwen Coder, Code Llama, DeepSeek Coder) to better understand and generate:

- Audio filters  
- Oscillators  
- Gain processors  
- Delay effects  
- Reverb algorithms  
- Compressors  
- Envelope generators  
- General real-time DSP logic in C++

This project simulates a real-world ML/Data Engineering workflow involving:

- Source code mining  
- Dataset generation  
- Data cleaning  
- Prompt engineering  
- Preparation for LLM fine-tuning

---

#  Problem Statement

Most general-purpose coding models have limited specialization in **real-time audio DSP development**, especially in C++.

Audio software developers often require help generating or understanding:

- Efficient DSP algorithms  
- Plugin processing chains  
- Synthesizer voice engines  
- Filters and modulation systems  
- JUCE-based plugin architecture

However, publicly available fine-tuning datasets focused on **Audio DSP code** are rare.

This project solves that gap by building a custom instruction-response dataset from real-world open-source DSP codebases.

---

# Business / Industry Relevance

This dataset can later support AI tools for:

- Audio plugin development assistants  
- DSP code autocomplete tools  
- Educational tutors for audio programming  
- Intelligent debugging of signal chains  
- Rapid prototyping of synth/filter modules

Industries impacted:

- Music technology  
- Game audio  
- Film sound design  
- Plugin development  
- Embedded audio systems

---

# Tech Stack

| Category | Tools |
|--------|------|
| Language | Python |
| Source Code | C++ |
| Data Format | JSONL |
| Environment | Windows / PowerShell |
| Version Control | Git + GitHub |
| IDE | VS Code |
| Future Training | Unsloth / QLoRA / Hugging Face |

---

## Project Structure

```text
sft_audio_dsp_project/
├── src/                        
├── data/
│   ├── extracted_dsp_functions.txt                  
│   ├── generated_instruction_response_pairs.jsonl   
│   ├── final_sft_dataset.jsonl                      
│   └── formatted_sft_dataset.jsonl                  
├── scripts/
│   ├── extract_dsp.py          
│   ├── generate_dataset.py     
│   ├── filter_dataset.py       
│   └── format_dataset.py       
├── notebooks/
│   └── qlora_finetuning.ipynb  
└── README.md
