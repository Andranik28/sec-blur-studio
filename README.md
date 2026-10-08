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

---

## 💻 Requirements & Installation

### Python Environment
- Python **3.8** or higher
```bash
git clone [https://github.com/Andranik28/sec-blur-studio.git](https://github.com/Andranik28/sec-blur-studio.git)
cd sec-blur-studio
pip install -r requirements.txt
```

### C++ Environment
- **CMake** (v3.10+)
- **OpenCV** (v4.x+)
- C++17 compatible compiler (GCC, Clang, or MSVC)

*Ubuntu/Debian:* `sudo apt install cmake libopencv-dev`  
*macOS:* `brew install cmake opencv`

---

## 📊 Dataset Information

1. **Labeled Faces in the Wild (LFW)**: Download from [Kaggle](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset) and place in `datasets/lfw/`.
2. **USC-SIPI Image Database**: Download from [USC-SIPI](https://sipi.usc.edu/database/) and place in `datasets/usc_sipi/`.

---

## 🚀 Usage Instructions (Python)

### 1. Embedding & Blurring
```bash
python scripts/run_embedding.py \
  --input_dir datasets/lfw/lfw-deepfunneled \
  --output_dir results/stego_blurred \
  --config configs/config.yaml
```

### 2. Extraction & Restoration
```bash
python scripts/run_restoration.py \
  --stego_dir results/stego_blurred \
  --output_dir results/restored \
  --secret_key "SecBlurSecretKey2026"
```

---

## ⚡ Usage Instructions (C++)

The C++ core is designed for high-performance execution.

### 1. Compile the C++ Engine
```bash
cd c_src
mkdir build && cd build
cmake ..
make
```

### 2. Run the C++ CLI
```bash
# Usage: ./secblur_cli <input_image> <output_image>
./secblur_cli ../../datasets/sample.jpg ../../results/output_stego.png
```

---

## 📈 Experimental Results

| Metric | Typical Range | Description |
| :--- | :--- | :--- |
| **PSNR (dB)** | $> 40 \text{ dB}$ | Peak Signal-to-Noise Ratio (restored vs original). |
| **SSIM** | $> 0.98$ | Structural Similarity Index Measure. |
| **Execution Time** | $< 20 \text{ ms}$ (C++) | Average per-image processing latency. |
| **Steganalysis** | $\approx 50\%$ | Detection rate by statistical steganalysis. |

To reproduce these metrics in Python:
```bash
python scripts/evaluate_all.py --config configs/config.yaml
```

---

## 📝 Citations

If you use this code in your research, please cite:
```bibtex
@article{secblurstudio2026,
  title     = {Reversible Image Privacy Protection via Selective Blurring and Reversible Data Hiding},
  author    = {Andranik and Contributors},
  journal   = {GitHub Repository},
  year      = {2026},
  url       = {[https://github.com/Andranik28/sec-blur-studio](https://github.com/Andranik28/sec-blur-studio)}
}
```

---

## 📜 License & Contribution Guidelines
Released under the [MIT License](LICENSE). Contributions to both the Python wrapper and the C++ engine are welcome via Pull Requests.
