# SecBlur Studio (`sec-blur-studio`)
### Reversible Image Blurring, Steganographic Embedding, and High-Fidelity Restoration Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![C++17](https://img.shields.io/badge/C++-17-00599C.svg?logo=c%2B%2B)](https://isocpp.org/)
[![Repository URL](https://img.shields.io/badge/GitHub-Andranik28%2Fsec--blur--studio-green)](https://github.com/Andranik28/sec-blur-studio)

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Methodology](#%EF%B8%8F-methodology)
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

### 📄 Document Redaction Module (RCO Framework)
In addition to visual image blurring, the repository includes the official implementation of **Reversible Colour Obfuscation (RCO)** specifically designed for digital document redaction (scanned forms, administrative records, healthcare/financial documents). RCO combines AES-256 encryption, background-aware solid-colour replacement (defeating contrast-enhancement forensic attacks with a 0% recovery rate), and Prediction-Error Histogram Shifting (PEHS) steganography for self-contained, bit-perfect restoration.

---

## ⚙️ Methodology

### 1. Facial / Image Blurring Pipeline
1. **Embedding & Obfuscation**: Detects the sensitive Region of Interest (ROI), extracts its details, and applies a parameter-controlled Gaussian/Selective Blur. The original ROI details are encrypted and embedded into the image using Least Significant Bit (LSB) or Reversible Data Hiding (RDH).
2. **Extraction & Restoration**: Reads the authenticated stego-bits, decompresses the original ROI, and reconstructs the unblurred image.

### 2. Document Redaction (RCO Pipeline)
1. **Background Estimation & Foreground Masking**: Estimates local paper colour $C_b$ from a 1-pixel boundary around selected region $R$. Computes a binary mask $F(p)$ using noise tolerance threshold $\tau = 10$.
2. **Payload Preparation & Encryption**: Compresses $F(p)$ via RLE, appends SHA-256 hash integrity check, and encrypts payload using **AES-256-CBC** with PBKDF2 key derivation (600,000 iterations).
3. **Solid-Colour Obfuscation**: Overwrites $R$ with $C_b$, physically destroying visible confidential information and rendering it immune to forensic contrast manipulation.
4. **PEHS Steganographic Embedding**: Embeds encrypted payload into non-obfuscated background pixels using Prediction-Error Histogram Shifting, yielding an imperceptible stego document ($\text{PSNR} > 50\text{ dB}$).
5. **Bit-Perfect Restoration**: Extracts payload, decrypts AES-256 ciphertext, verifies SHA-256 integrity, and restores original foreground pixels with 100% accuracy under lossless formats (PNG/TIFF).

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
```

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
## 📊 Dataset Information

1. **Labeled Faces in the Wild (LFW)**: Download from [Kaggle](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset) and place in `datasets/lfw/`.
2. **USC-SIPI Image Database**: Download from [USC-SIPI](https://sipi.usc.edu/database/) and place in `datasets/usc_sipi/`.
3. **Tobacco800 Document Image Database**: Download public scans from [Tobacco800 Repository](https://www.industrydocuments.ucsf.edu/) and place in `datasets/tobacco800/`. Pre-annotated ground-truth bounding boxes are provided in `datasets/tobacco800/annotations.json`.
4. **RVL-CDIP Corpus**: Download grayscale forms/letters from the [RVL-CDIP Dataset](https://www.cs.cmu.edu/~aharley/rvl-cdip/) and place in `datasets/rvl_cdip/`.

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

### 1. Facial Image Blurring Benchmarks

Evaluated on **100 images** from the LFW dataset and **5 images** from the USC-SIPI database across kernel sizes ranging from 10% to 90% of the region's smaller dimension.

| Metric | Published Value | Description / Statistics |
| :--- | :--- | :--- |
| **Restoration Quality** | **PSNR = ∞ dB**, **SSIM = 1.0** | Bit-perfect, mathematically lossless recovery using correct password. |
| **Embedding Capacity** | **3.0 bpp** | Total capacity of 67,500 bits for a 150 × 150 region (~63,724 bits payload utilized). |
| **Compression Ratio** | **8.1:1 – 8.9:1** | Lossless predictive coding (lowest single image: 7.2:1). $F(4, 396) = 87.42$, $p < 0.001$, $\eta^2 = 0.469$. |
| **Embedding Feasibility** | **100%** | Zero embedding failures across all tested images and kernel sizes. |
| **Embedding Time** | **4.2 ms** (SD = 0.31 ms) | Evaluated on Intel Core i7-10700 with 10-run averaging. |
| **Restoration Time** | **3.8 ms** (SD = 0.27 ms) | Significantly faster than embedding ($t(9) = 6.84$, $p < 0.001$, $d = 1.37$). |
| **Steganalysis Detection** | **0% Detection Rate** | 0% false positive rate across StegSpy, VSL, and StegSecret detectors. |

#### Obfuscation Thresholds
- **10% – 30% Kernel Sizes:** Facial features remain partially discernible or recognizable despite quantization.
- **50% – 90% Kernel Sizes:** Facial landmarks fall below spatial resolution limits, achieving effective anonymization and structural unrecognizability.

---

### 2. Document Redaction (RCO Paper Benchmarks)

Evaluated across **Tobacco800**, **RVL-CDIP**, **Synthetic**, and **Real Colour** document datasets ($n = 6,000$ trials):

| Metric / Evaluation | Published Result [95% CI] | Statistical / Method Details |
| :--- | :--- | :--- |
| **Forensic Recovery Rate** | **0%** (RCO) vs **>90%** (Overlay) | Contrast Enhancement (AHE + Contrast Stretch), $p < 0.001$, Cohen's $d = 4.82$. |
| **Global Quality (PSNR)** | **> 50.7 dB** [50.1, 51.3] | Imperceptible embedding distortion across all datasets. |
| **Non-Obfuscated PSNR** | **> 57.9 dB** [57.2, 58.6] | Isolated background embedding fidelity. |
| **Structural Similarity (SSIM)**| **> 0.997** [0.996, 0.998] | Global and non-obfuscated SSIM. |
| **RS Steganalysis** | **$p = 0.71$** (Mann-Whitney U) | No statistically significant difference between clean cover and RCO stego. |
| **SRNet Deep Steganalysis** | **EER = 0.488** [0.471, 0.505] | AUC = 0.51 (chance-level discrimination). |
| **Restoration Accuracy** | **100% Bit-Perfect** | Bit-identical reconstruction across all 6,000 lossless (PNG) trials. |
| **Processing Speed** | **< 1.5 seconds / page** | End-to-end timing on standard desktop hardware (Intel i7-10700K). |
| **Peak Memory Usage** | **< 85 MB** | Lightweight operational memory footprint. |

---

---

## 📝 Citations

If you use this code in your research, please cite:
```bibtex
@article{secblurstudio2026,
  title     = {Reversible Image Privacy Protection via Selective Blurring and Reversible Data Hiding},
  author    = {Andranik Karakhanyan},
  journal   = {GitHub Repository},
  year      = {2026},
  url       = {[https://github.com/Andranik28/sec-blur-studio](https://github.com/Andranik28/sec-blur-studio)}
}
```

---

## 📜 License & Contribution Guidelines
Released under the [MIT License](LICENSE). Contributions to both the Python wrapper and the C++ engine are welcome via Pull Requests.
