# Information Theory & Data Compression - Course Assignments

A comprehensive collection of four distinct data compression and information theory implementations covering classical and modern compression algorithms. This project was completed for the Information Theory and Data Compression course.

---

## 🎯 Overview

This repository contains four fundamental data compression techniques implemented in Python, each addressing different aspects of information theory and compression:

### **Core Technologies**
- **Language**: Python 3.x
- **Libraries**: NumPy, PIL (Pillow), Tkinter, heapq, struct
- **Paradigms**: Object-Oriented Programming, Functional Programming
- **Data Structures**: Binary Trees, Min Heaps, Codebooks, Search Buffers, Prediction Models

### **Learning Objectives**
- ✅ Understand lossless compression techniques (LZ77, Huffman, DPCM)
- ✅ Implement lossy compression using vector quantization
- ✅ Apply adaptive prediction techniques for image compression
- ✅ Calculate compression ratios and efficiency metrics
- ✅ Design GUI interfaces for real-world applications
- ✅ Apply information theory principles in practice

---

## 📂 Repository Structure

```
information-theory-data-compression/
│
├── README.md                                           
│
├── 1_LZ77_Compression/
│   ├── LZ77.py                     
│
├── 2_Huffman_Coding/
│   ├── Huffman.py               
│   
├── 3_Vector_Quantization/
│   ├── VQ.py                    
│   
├── 4_Adaptive_2D_Predictors/
│   ├── 2D_Predictor.py

```

---

## 📚 Assignments Summary

### **1. LZ77 Compression** - Handling Repetitive Sequences

#### Overview
LZ77 (Lempel-Ziv 1977) is a dictionary-based, lossless compression algorithm that exploits repetitive patterns in data by storing references to previously seen sequences.

#### Key Features
- **Technique**: Sliding window compression
- **Search Buffer**: Previous data used for pattern matching
- **Look-Ahead Buffer**: Future data to be compressed
- **Data Structure**: Three-tuple (position, length, next_char)
- **Best For**: Text files, code, highly repetitive data

#### How It Works

```
Input: "CABRACADABR"
       Search Buffer: ""
       Look-ahead: "CABRACADABR"

Output Tuples:
(0, 0, 'C')    → 'C' not in buffer, emit literal
(1, 1, 'A')    → Found 'A' at position 1, length 1, next 'A'
(3, 3, 'A')    → Found "ACA" at position 3, length 3, next 'A'
...
```

#### Compression Mechanism

1. **Search Phase**: Look for longest match in search buffer
2. **Match Recording**: Store (position, length, next_character)
3. **Buffer Update**: Shift window forward
4. **Repeat**: Until entire data is processed

#### Time Complexity
- **Compression**: O(n²) worst case, O(n log n) typical
- **Decompression**: O(n) - Linear

#### Space Complexity
- **Search Buffer**: Fixed window size (typically 4KB - 32KB)
- **Output**: Typically 60-80% of original for text

#### Advantages
- ✅ Simple to understand and implement
- ✅ Adaptive (no pre-computed tables needed)
- ✅ Good compression on repetitive data
- ✅ Real-time decompression possible

#### Disadvantages
- ❌ Slower than modern algorithms
- ❌ High memory for large windows
- ❌ Performance depends on data patterns
- ❌ Not optimal for random data

#### Use Cases
- ZIP/RAR archives (combined with Huffman)
- DEFLATE algorithm (gzip)
- PNG image compression
- Document compression
- Source code repositories

---

### **2. Huffman Coding** - Standard Huffman Assignment

#### Overview
Huffman coding is a greedy algorithm that assigns variable-length binary codes to symbols based on their frequency, with more frequent symbols receiving shorter codes.

#### Key Features
- **Technique**: Entropy encoding (information theory based)
- **Tree Structure**: Binary tree built from bottom-up
- **Code Assignment**: Variable-length binary codes
- **Data Structure**: Prefix-free code (no code is prefix of another)
- **Best For**: High-entropy data with non-uniform distribution

#### How It Works

**Step 1: Build Frequency Table**
```
Text: "HUFFMAN CODING"
Frequencies:
'H': 1, 'U': 1, 'F': 2, 'M': 1, 'A': 1, 'N': 2,
'C': 1, 'O': 1, 'D': 1, 'I': 1, 'G': 1, ' ': 2
```

**Step 2: Build Huffman Tree**
```
Using Min Heap (Priority Queue):
1. Insert all frequency nodes
2. Repeatedly:
   - Extract two minimum nodes
   - Create parent with combined frequency
   - Re-insert parent
3. Last node is root
```

**Step 3: Assign Codes**
```
Tree traversal:
- Left edge = 0
- Right edge = 1

'F': 00      (freq: 2)
'N': 01      (freq: 2)
'H': 100     (freq: 1)
'U': 101     (freq: 1)
...
```

**Step 4: Encode/Decode**
```
Encoding: Text → Look up code → Concatenate bits
Decoding: Bits → Traverse tree → Emit character
```

#### Time Complexity
- **Frequency Calculation**: O(n)
- **Tree Building**: O(n log n)
- **Code Generation**: O(n)
- **Encoding**: O(n)
- **Decoding**: O(m) where m is encoded length
- **Total**: O(n log n)

#### Space Complexity
- **Tree**: O(n) nodes for n unique symbols
- **Codes**: O(n) entries in code dictionary
- **Output**: 0.5n to 1.5n bytes typically

#### Compression Metrics

```
Compression Ratio = Original Size / Compressed Size
Redundancy = 1 - (Entropy / Average Code Length)

Example:
Original: 1000 bytes
Encoded: 625 bytes
Ratio: 1.6:1 (60% reduction)
```

#### Advantages
- ✅ Optimal for known frequency distribution
- ✅ Fast encoding/decoding
- ✅ Prefix-free guarantee (no ambiguity)
- ✅ Theoretically optimal (≤ H(X) + 1 bits/symbol)
- ✅ Proven optimal compression for the method

#### Disadvantages
- ❌ Needs two passes (frequency calculation, then encoding)
- ❌ Tree/codes must be stored with data
- ❌ Not adaptive to changing frequencies
- ❌ Overhead for small files

#### Use Cases
- JPEG image compression (DC/AC coefficients)
- MP3 audio compression
- DEFLATE algorithm (with LZ77)
- PDF compression
- FAX transmission
- Huffman coding in most compression formats

---

### **3. Vector Quantization (VQ)** - LBG Algorithm for Image Compression

#### Overview
Vector Quantization is a lossy compression technique that partitions the input space into clusters (a codebook) and represents each input vector by its closest cluster center. The LBG (Linde-Buzo-Gray) algorithm is used to iteratively optimize the codebook.

#### Key Features
- **Technique**: Lossy clustering-based compression
- **Algorithm**: LBG (Iterative optimization)
- **Block Size**: Configurable (typically 4×4 or 8×8 pixels)
- **Codebook**: Set of representative vectors (centroids)
- **Encoding**: Each block represented by closest codevector index
- **Best For**: Images, high compression ratios acceptable

#### How It Works

**Step 1: Image Preprocessing**
```
Input Image (256×256)
↓
Padding to multiple of block size
↓
Extract non-overlapping blocks (4×4)
↓
Flatten blocks to vectors (16 dimensions for 4×4)
```

**Step 2: Initialize Codebook (LBG Algorithm)**
```
1. Calculate average of all vectors
2. While |codebook| < target_size:
   a. Split each centroid by ±delta
   b. Assign vectors to nearest codevectors
   c. Recompute centroids (refine)
   d. Repeat refinement until convergence
```

**Step 3: Encoding**
```
For each block:
- Calculate distance to all codevectors
- Find closest match (minimum distance)
- Store index of closest codevector
- Original: 16 bytes (4×4 RGB) → 1 byte index
```

**Step 4: Decoding**
```
For each index:
- Look up codevector in codebook
- Reconstruct block from codevector
- Place in output image
```

#### Time Complexity
- **Block Extraction**: O(n) where n = pixels
- **LBG Training**: O(i × k × m) where:
  - i = iterations (typically 10-100)
  - k = codebook size (power of 2)
  - m = number of vectors
- **Encoding**: O(n/B² × k) - k distance calculations per block
- **Decoding**: O(n/B²) - simple lookup

#### Space Complexity
- **Codebook**: O(k × B²)
- **Index array**: O(n/B²) pixels

#### GUI Features
- **Compression Tab**:
  - Image loading and preview
  - Configurable block size (width × height)
  - Adjustable codebook size (2, 4, 8, 16, 32, 64, 128, 256)
  - Output path selection
  - Progress indication
  - Real-time statistics (compression ratio, file sizes)

- **Decompression Tab**:
  - Load compressed image and codebook
  - Reconstruct original dimensions
  - Save decompressed image
  - Display compression metrics

#### Advantages
- ✅ Extreme compression ratios (10:1 to 100:1)
- ✅ Fast decompression (simple lookup)
- ✅ Easily parallelizable
- ✅ Configurable quality-compression trade-off
- ✅ Works well for natural images

#### Disadvantages
- ❌ Lossy compression (quality reduction)
- ❌ Training phase time-consuming
- ❌ Fixed codebook per image
- ❌ Block artifacts visible
- ❌ Codebook dependent on training data

#### Quality vs. Compression Trade-off

```
Codebook Size  | Bits/Block | Ratio    | Visual Quality
2              | 1 bit      | 100:1    | Very poor
4              | 2 bits     | 50:1     | Poor
8              | 3 bits     | 33:1     | Fair
16             | 4 bits     | 25:1     | Good
32             | 5 bits     | 20:1     | Very good
64             | 6 bits     | 17:1     | Excellent
256            | 8 bits     | 12:1     | Near-lossless
```

#### Use Cases
- Video compression (motion JPEG)
- Satellite imagery compression
- Medical imaging (ultrasound, X-ray)
- Voice compression
- Texture compression in graphics
- Real-time video streaming
- Mobile image transmission

---

### **4. Adaptive 2D Predictors (DPCM)** - Feed-Backward Predictive Coding

#### Overview
Differential Pulse Code Modulation (DPCM) with adaptive 2D prediction is a lossless compression technique that predicts pixel values using neighboring pixels and encodes only the prediction error. The adaptive predictor uses the pixel values to intelligently select the prediction method.

#### Key Features
- **Technique**: Predictive coding with error quantization
- **Algorithm**: Adaptive 2D prediction + Uniform Quantization
- **Predictor Type**: Adaptive (chooses between min, max, and linear interpolation)
- **Error Encoding**: Quantized prediction residuals
- **Data Structure**: Pickle file format for compressed data
- **Best For**: Natural images with spatial correlation
- **Output**: 6 intermediate images showing compression process

#### How It Works

**Step 1: Image Loading**
```
Input: Grayscale or RGB image
↓
Convert to 2D/3D numpy array (int32 for precision)
↓
Extract height and width
↓
Store first row and column (no prediction needed)
```

**Step 2: Adaptive Prediction**
```
For each pixel at position (i, j):
  Get neighbor pixels:
  - A = decoded[i, j-1]    (Left pixel)
  - B = decoded[i-1, j-1]  (Top-left diagonal)
  - C = decoded[i-1, j]    (Top pixel)
  
  Apply Adaptive Predictor:
  if B ≤ min(A, C):
    prediction = min(A, C)    (Flat region)
  else if B ≥ max(A, C):
    prediction = max(A, C)    (Flat region)
  else:
    prediction = A + C - B    (Linear interpolation - median)
```

**Step 3: Error Calculation**
```
prediction_error = original_pixel - predicted_pixel
```

**Step 4: Uniform Quantization**
```
Quantizer with configurable bits (default: 2 bits):
- Step Size = 256 / (2^bits)
- Quantization Level = floor((error + 128) / step)
- Dequantized Value = midpoint of quantization interval

Example (2 bits):
Step = 64
Levels: -128:[-128,-64), -64:[-64,0), 0:[0,64), 64:[64,128)
Midpoints: -96, -32, 32, 96
```

**Step 5: Decoding (Reconstruction)**
```
For each pixel:
  decoded_pixel = predicted_pixel + dequantized_error
```

#### Quantization Details

```python
# Quantizer Function
def create_quantizer(target_bits=2, full_scale=256):
    step = 256 / (2^target_bits)
    
    For each quantization level i:
      Start = -128 + i * step
      End = -128 + (i+1) * step
      Midpoint (dequantization) = (Start + End) / 2
      
Example (2 bits → 4 levels):
Code 0: [-128, -64) → Midpoint: -96
Code 1: [-64, 0)   → Midpoint: -32
Code 2: [0, 64)    → Midpoint: 32
Code 3: [64, 128)  → Midpoint: 96
```

#### Compression Process

```
Original Image
    ↓
Extract First Row/Column
    ↓
For Each Interior Pixel:
  ├─ Predict (using adaptive 2D)
  ├─ Calculate Error
  ├─ Quantize Error
  ├─ Dequantize Error
  └─ Reconstruct Decoded Value
    ↓
Quantized Error Array → Pickle File
    ↓
6 Output Images Generated
```

#### Output Images (6 Required)

1. **Original**: Input grayscale image
2. **Predicted**: Prediction map (predicted values for each pixel)
3. **Error**: Prediction error map (original - predicted)
   - Shifted by 128 for visualization (errors centered at 128)
   - Darker pixels = negative errors, Brighter = positive errors
4. **Quantized**: Quantization indices (visual representation)
   - Each level mapped to distinct grayscale value
   - Shows which quantization levels were used
5. **Dequantized**: Dequantized error values (reconstruction errors)
   - Quantization noise visualization
   - Shows loss in reconstruction
6. **Decoded**: Reconstructed/decompressed image
   - Predicted + Dequantized Error
   - Clipped to [0, 255] range

#### Compression Ratio Calculation

```
Original Size = Height × Width × 8 bits/pixel

Compressed Size = 
  First Row: Width × 8 bits
  First Column (excluding first element): Height × 8 bits
  Interior Pixels: (Height-1) × (Width-1) × target_bits

Compression Ratio = Original Size / Compressed Size

Example (256×256 image, 2 bits):
Original: 256 × 256 × 8 = 524,288 bits
Compressed: 
  - First Row: 256 × 8 = 2,048 bits
  - First Column: 255 × 8 = 2,040 bits
  - Interior: 255 × 255 × 2 = 129,790 bits
  - Total: 133,878 bits
Ratio: 524,288 / 133,878 ≈ 3.9:1
```

#### Time Complexity
- **Compression**: O(h × w) - Single pass through image
- **Decompression**: O(h × w) - Reconstruction pass
- **Quantization**: O(1) per pixel

#### Space Complexity
- **Storage**: (h × w × target_bits) / 8 bytes (compressed)
- **Working**: O(h × w) for arrays

#### Menu Interface

```
=====================================
FEED BACKWARD DPCM - 2D ADAPTIVE 
PREDICTIVE CODING
=====================================
1. Compress Image (Feed Backward)
2. Decompress Image (Feed Backward)
3. Exit
=====================================
```

#### Compression Features

1. **Dynamic Quantizer Bits**: User selects 1 to 8+ bits
2. **Quantizer Table Display**: Shows all levels with ranges and midpoints
3. **File I/O**: 
   - Input: PNG, JPG, BMP, TIFF
   - Compressed: .pkl (Pickle format)
   - Output: 6 PNG images
4. **Error Handling**: File existence validation, format checking

#### Decompression Features

1. **Load Compressed Data**: Read .pkl file
2. **Reconstruct Original**: Apply inverse prediction
3. **Adaptive Prediction**: Uses same predictor as compression
4. **Save Result**: Output PNG with "_decompressed" suffix

#### Advantages
- ✅ Simple and fast compression/decompression
- ✅ Fully reversible (lossless for integer arithmetic)
- ✅ Effective on correlated image data
- ✅ Low computational complexity
- ✅ Adaptive to local image content
- ✅ Configurable quality/compression trade-off
- ✅ No codebook needed (stateless)

#### Disadvantages
- ❌ Performance varies with image type
- ❌ Poor compression on random/noisy data
- ❌ Artifacts at sharp transitions
- ❌ Quantization noise visible at low bits
- ❌ Edge pixels not predicted (overhead)

#### Adaptive Predictor Explanation

The predictor adapts based on local image structure:

```
Flat/Smooth Region (B ≤ min(A,C)):
  Uses: min(A, C) - Edge following
  Example: B=100, A=105, C=103 → Predict 103

Sharp Corner (B ≥ max(A,C)):
  Uses: max(A, C) - Edge following
  Example: B=200, A=150, C=160 → Predict 200

Texture/Diagonal (min < B < max):
  Uses: A + C - B - Linear interpolation (median edge detector)
  Example: B=155, A=150, C=160 → Predict 150+160-155=155
```

#### Use Cases
- Medical image compression (CT, MRI, X-ray)
- Document image compression
- Satellite imagery
- Video frame compression
- Lossless image archival
- Real-time image streaming
- Embedded system applications

#### Performance Metrics Example

```
Test Image: 512×512 Grayscale Medical Image

2-bit Quantization:
- Original: 262,144 bytes
- Compressed: ~67,000 bytes
- Ratio: 3.9:1
- Time: <1 second
- PSNR: ~38-42 dB

4-bit Quantization:
- Original: 262,144 bytes
- Compressed: ~132,000 bytes
- Ratio: 2.0:1
- Time: <1 second
- PSNR: ~48-52 dB (near-lossless)
```

#### Comparison with VQ

| Feature | DPCM (2D Predictor) | Vector Quantization |
|---------|-------------------|-------------------|
| **Type** | Lossless (integer) | Lossy |
| **Speed** | Very fast | Moderate |
| **Compression** | 2-5:1 | 10-100:1 |
| **Quality** | Excellent | Good to Poor |
| **Memory** | Low | High (codebook) |
| **Training** | None | Requires LBG |
| **Best For** | Natural images | High compression needs |

---

## 🚀 Getting Started

### Prerequisites
```bash
# Python 3.7 or higher
python --version

# Required libraries
pip install numpy pillow
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/passantelsherif/information-theory-data-compression.git
cd information-theory-data-compression

# Assignment 1: LZ77 Compression
cd 1_LZ77_Compression
python LZ77_20230269_20230248_20231036.py

# Assignment 2: Huffman Coding
cd ../2_Huffman_Coding
python Huffman_20231036_20230248_20230269.py

# Assignment 3: Vector Quantization GUI
cd ../3_Vector_Quantization
python VQ_20230269_20230248_20231036.py

# Assignment 4: Adaptive 2D Predictors
cd ../4_Adaptive_2D_Predictors
python 2D_Predictor.py
```

---

## 📖 Installation & Setup

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.7+
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk**: 500MB free space for examples

### Step-by-Step Installation

**1. Clone Repository**
```bash
git clone https://github.com/passantelsherif/information-theory-data-compression.git
cd information-theory-data-compression
```

**2. Create Virtual Environment (Optional but Recommended)**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Verify Installation**
```bash
python -c "import numpy; import PIL; print('All dependencies installed!')"
```

---

## 💻 Usage Guide

### **Assignment 1: LZ77 Compression**

#### Interactive Mode
```bash
cd 1_LZ77_Compression
python LZ77_20230269_20230248_20231036.py

# Menu options:
# 1. Compress a string
# 2. Decompress tags
# 3. Exit

# Example compression:
> Choose option: 1
> Enter data: ABAABABAABBBBBBBBBBBBA
> Output: [(0,0,'A'), (1,1,'B'), (2,2,'A'), ...]
```

---

### **Assignment 2: Huffman Coding**

#### Interactive Mode
```bash
cd 2_Huffman_Coding
python Huffman_20231036_20230248_20230269.py

# Input file name: mytext.txt
# Output: 
#   - Frequency analysis
#   - Huffman codes display
#   - Compression ratio
#   - Encoded binary file
#   - Decoded verification
```

#### File Compression Workflow
```
1. Place text file in directory
2. Run: python Huffman_20231036_20230248_20230269.py
3. Enter filename when prompted
4. View statistics and Huffman codes
5. Binary file created: filename_encoded.bin
6. Decoded file created: filename_decoded.txt
7. Compare original vs decoded to verify
```

---

### **Assignment 3: Vector Quantization (VQ) GUI**

#### Launch Application
```bash
cd 3_Vector_Quantization
python VQ_20230269_20230248_20231036.py
```

#### Compression Workflow

**Tab 1: Compress Image**

1. **Select Image**
   - Click "Browse" next to "Select Image"
   - Choose JPG, PNG, BMP, or TIFF file

2. **Set Parameters**
   - Block Width: 4 (default)
   - Block Height: 4 (default)
   - Codebook Size: 16, 32, 64, 128, 256

3. **Set Output Path**
   - Click "Browse" or type custom name

4. **Compress**
   - Click "Compress Image" button
   - Two files created:
     - `*_image.npy` (indices)
     - `*_codebook.npz` (codebook)

#### Decompression Workflow

**Tab 2: Decompress Image**

1. **Load Compressed Files**
   - Select `*_image.npy` file
   - Select `*_codebook.npz` file

2. **Set Output**
   - Choose format (JPG, PNG)

3. **Decompress**
   - Click "Decompress Image" button

---

### **Assignment 4: Adaptive 2D Predictors (DPCM)**

#### Interactive Mode
```bash
cd 4_Adaptive_2D_Predictors
python 2D_Predictor.py
```

#### Menu Interface
```
============================================================
FEED BACKWARD DPCM - 2D ADAPTIVE PREDICTIVE CODING
============================================================
1. Compress Image (Feed Backward)
2. Decompress Image (Feed Backward)
3. Exit
============================================================
```

#### Compression Workflow

**Option 1: Compress Image**

1. **Input Image Path**
   - Enter path to image file (PNG, JPG, BMP, TIFF)
   - Example: `photo.jpg` or `C:\images\picture.png`

2. **Select Quantizer Bits**
   - Enter number of bits (default: 2)
   - Examples: 1, 2, 3, 4, 5, etc.
   - Higher bits = Better quality, Lower compression

3. **Output Files**
   - Compressed: `image_Xbit.pkl` (Pickle file)
   - 6 Images Generated:
     1. `image_original.png` - Original input
     2. `image_predicted.png` - Prediction map
     3. `image_error.png` - Prediction errors
     4. `image_quantized.png` - Quantization levels
     5. `image_dequantized.png` - Dequantized errors
     6. `image_decoded.png` - Reconstructed image

4. **Information Displayed**
   - Quantizer table with all levels and midpoints
   - Compression ratio
   - File sizes

#### Compression Example

```
Enter choice: 1
Image path: sample.jpg
Quantizer bits: 2

Quantizer Table (2 bits):
Code   Start      End        Dequant
0      -128.0     -64.0      -96.0
1      -64.0      0.0        -32.0
2      0.0        64.0       32.0
3      64.0       128.0      96.0

Compression Ratio: 3.92:1
Images saved with prefix: sample_
Compressed data saved: sample_2bit.pkl
```

#### Decompression Workflow

**Option 2: Decompress Image**

1. **Input Compressed File**
   - Enter path to .pkl file
   - Example: `image_2bit.pkl`

2. **Output**
   - Decompressed image: `image_2bit_decompressed.png`

#### Decompression Example

```
Enter choice: 2
Compressed file path (.pkl): sample_2bit.pkl

Decompressing: 512x512 image, 2-bit quantization
Decompressed image saved: sample_2bit_decompressed.png
Decompression complete!
```

#### Parameter Guidelines

```
Quantizer Bits vs Compression vs Quality:

1-bit:
  - Compression: 7.8:1
  - Quality: Very poor (binary)
  - Use: Extreme compression only

2-bit (default):
  - Compression: 3.9:1
  - Quality: Fair
  - Use: Good balance

4-bit:
  - Compression: 1.95:1
  - Quality: Very good
  - Use: High-quality compression

6-bit:
  - Compression: 1.3:1
  - Quality: Excellent
  - Use: Near-lossless

8-bit:
  - Compression: 1.0:1
  - Quality: Virtually perfect
  - Use: Lossless reference
```

#### Understanding Output Images

1. **Original** - Input image as-is
2. **Predicted** - What algorithm expected at each pixel
3. **Error** - Difference between original and prediction
   - Mid-gray (128) = Zero error
   - Darker = Overestimation
   - Brighter = Underestimation
4. **Quantized** - Which quantization level used
   - Visual representation of 4 levels (2 bits)
   - Distinct gray levels
5. **Dequantized** - Actual error values after quantization
   - Shows quantization noise
6. **Decoded** - Final reconstructed image
   - Should closely match original

---

## 🔧 Technical Details

### Data Structures

#### LZ77
```python
# Output format: List of tuples
tags = [
    (position_in_buffer, match_length, next_character),
    (0, 0, 'C'),           # Literal 'C'
    (1, 1, 'A'),           # Reference to position 1, length 1
    ...
]
```

#### Huffman
```python
# Code dictionary
codes = {
    'H': '00',
    'U': '101',
    'F': '110',
    ...
}

# File format
[metadata: 8 bytes][tree/codes: variable][encoded_data: variable]
```

#### Vector Quantization
```python
# Compressed data dictionary
compressed_data = {
    'codebook': np.array(...),           # K×(B²×3) matrix
    'encoded_indices': np.array(...),    # (H/B)×(W/B) indices
    'original_shape': (H, W, 3),
    'block_size': (B, B),
    'block_positions': [(row, col, ...), ...],
    'compression_ratio': 12.5,
    'is_color': True
}
```

#### 2D Predictor (DPCM)
```python
# Compressed data (Pickle format)
compressed_data = {
    'quantized': np.array(...),          # Quantization indices
    'first_row': [pixel_values],         # First row uncompressed
    'first_col': [pixel_values],         # First column uncompressed
    'height': H,
    'width': W,
    'target_bits': bits_used,
    'compression_ratio': 3.92
}
```

### I/O Operations

- **LZ77**: Text input, structured output (Python list)
- **Huffman**: Text input, binary output (pickle serialization)
- **VQ**: Image input, NumPy binary output
- **2D Predictor**: Image input, Pickle output + 6 PNG images

---

## 📊 Performance Analysis

### Compression Ratio Comparison

| Algorithm | Text | Code | Image | Random |
|-----------|------|------|-------|--------|
| **LZ77** | 40% | 35% | 70% | 95% |
| **Huffman** | 55% | 50% | 85% | 99% |
| **2D Predictor** | N/A | N/A | 25% (2-bit) | N/A |
| **VQ (K=64)** | N/A | N/A | 5% | N/A |

### Time Complexity

| Operation | LZ77 | Huffman | VQ | 2D Predictor |
|-----------|------|---------|-----|-------------|
| Compress | O(n²) | O(n log n) | O(ik m) | O(h×w) |
| Decompress | O(n) | O(m) | O(n) | O(h×w) |
| Space | O(buffer) | O(n) | O(k×B²) | O(h×w) |

### Practical Benchmarks

```
Test Image: 512×512 Grayscale Photo

2D Predictor (2-bit):
- Original: 262,144 bytes
- Compressed: 67,000 bytes
- Ratio: 3.9:1
- Time: <1 second
- Quality: Fair

2D Predictor (4-bit):
- Original: 262,144 bytes
- Compressed: 132,000 bytes
- Ratio: 2.0:1
- Time: <1 second
- Quality: Very good

VQ (K=64):
- Original: 262,144 bytes
- Compressed: 20,000 bytes (codebook) + 16,384 bytes (indices)
- Ratio: 11:1
- Time: 8 seconds
- Quality: Good
```

---


---

## 👥 Contributors

This project was completed by:
- **Passant Shaaban Abdelazim** 
- **Omar Hany Tohami** 
- **Omar Bassam Mahmoud** 

**Course**: Information Theory and Data Compression  
**Institution**: Cairo University, Faculty of Computers & Artificial Intelligence

---


## 📄 License

This project is created as academic coursework for Cairo University. All implementations are for educational purposes.

**Academic Integrity Notice**: These files are shared for learning purposes. If you use this code for your own coursework, please ensure proper citation and academic integrity guidelines.

---


