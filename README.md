# SecBlur Studio (`sec-blur-studio`)
### Reversible Image Blurring, Steganographic Embedding, and High-Fidelity Restoration Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![C++17](https://img.shields.io/badge/C++-17-00599C.svg?logo=c%2B%2B)](https://isocpp.org/)
[![Repository URL](https://img.shields.io/badge/GitHub-Andranik28%2Fsec--blur--studio-green)](https://github.com/Andranik28/sec-blur-studio)

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Methodology](#-methodology)
- [Repository Structure](#-repository-structure)
- [Requirements & Installation](#-requirements--installation)
- [Dataset Information](#-dataset-information)
- [Usage Instructions (Python)](#-usage-instructions-python)
- [Usage Instructions (C++)](#-usage-instructions-c)
- [Experimental Results](#-experimental-results)
- [Citations](#-citations)
- [License & Contribution Guidelines](#-license--contribution-guidelines)

---

## 📖 Overview

**SecBlur Studio** (`sec-blur-studio`) is an open-source, dual-language (Python & C++) framework for secure, reversible image blurring and data-hiding. Designed for visual privacy protection (e.g., facial obfuscation) and secure image transmission, the framework blurs a sensitive region while embedding the original high-fidelity visual details directly into the stego-image using reversible steganographic algorithms. 

Authorized users can extract the payload and fully restore the original image; unauthorized viewers only see the obfuscated content.

---

## ⚙️ Methodology

1. **Embedding & Obfuscation**: Detects the sensitive Region of Interest (ROI), extracts its details, and applies a parameter-controlled Gaussian/Selective Blur. The original ROI details are encrypted and embedded into the image using Least Significant Bit (LSB) or Reversible Data Hiding (RDH).
2. **Extraction & Restoration**: Reads the authenticated stego-bits, decompresses the original ROI, and reconstructs the unblurred image.

---

## 📂 Repository Structure

The project is structured to support both Python (for rapid experimentation and deep learning integrations) and C++ (for high-performance signal processing).

```tree
sec-blur-studio/
├── configs/                  # Experiment hyperparameter settings (YAML)
├── datasets/                 # Datasets (LFW and USC-SIPI)
├── src/                      # Python core implementation
├── scripts/                  # Python command-line execution scripts
├── c_src/                    # C++ High-Performance Core
│   ├── CMakeLists.txt        # C++ build instructions
│   ├── include/              # Header files (secblur.hpp)
│   └── src/                  # Implementation files (secblur.cpp, main.cpp)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
