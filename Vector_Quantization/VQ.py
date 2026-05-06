import numpy as np
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def load_user_image_gui(image_path):
    """Load image from provided path (GUI version)"""
    if not os.path.exists(image_path):
        return None, f"File '{image_path}' not found."
        
    try:
        pil_image = Image.open(image_path)
        original_image = np.array(pil_image)
        return original_image, f"Loaded: {image_path}\nImage size: {original_image.shape[1]} x {original_image.shape[0]} pixels"
        
    except Exception as e:
        return None, f"Error loading image: {e}"

def apply_padding_and_extract_blocks(image, block_height, block_width):
    """Pad image if needed and extract all blocks"""
    height, width = image.shape[:2]
    
    # Calculate padding needed to add on the image (15 % 4 = 3) -> you need 1 to padd perfectly with the 4 
    pad_width = block_width - (width % block_width) 
    pad_height = block_height - (height % block_height)
    
    # Apply padding
    if pad_height > 0 or pad_width > 0:
        if len(image.shape) == 3:
            padded_image = np.pad(image, ((0, pad_height), (0, pad_width), (0, 0)), mode='edge')
        else:
            padded_image = np.pad(image, ((0, pad_height), (0, pad_width)), mode='edge')
    else:
        padded_image = image
    
    # Calculate block arrangement
    final_height, final_width = padded_image.shape[:2]
    blocks_per_row = final_width // block_width
    blocks_per_col = final_height // block_height
    total_blocks = blocks_per_row * blocks_per_col
    
    # Extract blocks
    all_blocks = []
    block_positions = []
    
    for row in range(blocks_per_col):
        for col in range(blocks_per_row):
            start_y = row * block_height
            start_x = col * block_width

            block = padded_image[start_y:start_y + block_height, start_x:start_x + block_width]
            
            all_blocks.append(block)
            block_positions.append((row, col, start_y, start_x))
    
    return all_blocks, block_positions, padded_image, pad_height, pad_width

def lbg_splitting_algorithm(all_vectors, codebook_size, delta=0.01):
    """Exact LBG algorithm with splitting"""
    # Start with initial centroid (average of all vectors)
    average_vector = np.mean(all_vectors, axis=0)  # axis = 0 -> column
    codebook = [average_vector]
    
    current_iteration = 0
    while len(codebook) < codebook_size:
        current_iteration += 1
        
        # Split each centroid into two
        updated_codebook = []
        for current_centroid in codebook:
            left_split = current_centroid - delta   # Move left by delta
            right_split = current_centroid + delta  # Move right by delta
            updated_codebook.extend([left_split, right_split])
        
        codebook = np.array(updated_codebook)
        
        # Step 3: Refine - assign vectors to nearest centroids and recompute
        for refine_step in range(10):  # Max 10 refinement iterations
            # Create empty groups for each codevector
            vector_groups = [[] for _ in range(len(codebook))]
            total_error = 0
            
            # Assign each vector to closest codevector
            for current_vector in all_vectors:
                # Calculate distances to all codevectors
                distances = np.sum(np.abs(current_vector - codebook), axis=1)
                closest_index = np.argmin(distances)
                vector_groups[closest_index].append(current_vector)
                total_error += distances[closest_index]
            
            # Recompute centroids (average of each group)
            updated_codebook = []
            for group_index, vector_group in enumerate(vector_groups):
                if len(vector_group) > 0:
                    # Calculate average of vectors in this group
                    new_centroid = np.mean(vector_group, axis=0)
                    updated_codebook.append(new_centroid)
                else:
                    # Keep old centroid if group is empty
                    updated_codebook.append(codebook[group_index])
            
            updated_codebook = np.array(updated_codebook)
            
            # Update codebook for next refinement
            codebook = updated_codebook
    
    # Final assignment - determine which codevector represents each original vector
    final_assignments = []
    for current_vector in all_vectors:
        distances = np.sum(np.abs(current_vector - codebook), axis=1)
        best_match_index = np.argmin(distances)
        final_assignments.append(best_match_index)
    
    return codebook, np.array(final_assignments)

def compress_image_data(all_blocks, block_positions, codebook, indices, original_shape, padding, block_size, num_vectors):
    """Compress image data and calculate compression ratio"""
    # Calculate original image size in bits
    original_pixels = original_shape[0] * original_shape[1]
    if len(original_shape) == 3:
        bits_per_pixel = 8 * original_shape[2]  # 8 bits per channel
    else:
        bits_per_pixel = 8
    
    original_size_bits = original_pixels * bits_per_pixel
    
    # Calculate compressed size
    num_blocks = len(indices)
    bits_per_label = int(np.log2(len(codebook)))  # Binary labels
    
    labels_size_bits = num_blocks * bits_per_label
    
    # Codebook size: each vector has block_size pixels, each pixel uses bits_per_pixel
    block_pixels = block_size[0] * block_size[1]
    codebook_size_bits = len(codebook) * block_pixels * bits_per_pixel
    
    compressed_size_bits = labels_size_bits + codebook_size_bits
    compression_ratio = original_size_bits / compressed_size_bits
    
    compressed_data = {
        'codebook': codebook,
        'encoded_indices': indices,
        'original_shape': original_shape,
        'block_positions': block_positions,
        'padding': padding,
        'block_size': block_size,
        'num_vectors': num_vectors,
        'compression_ratio': compression_ratio,
        'is_color': len(all_blocks[0].shape) == 3 if all_blocks else False
    }
    
    return compressed_data, compression_ratio

def save_compressed_files(compressed_data, base_path):
    """Save compressed image and codebook as separate files"""
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(base_path) if os.path.dirname(base_path) else '.', exist_ok=True)
        
        # Save compressed image (only indices)
        image_path = base_path + '_compressed.npy'
        np.save(image_path, compressed_data['encoded_indices'])
        image_size = os.path.getsize(image_path)
        
        # Save codebook file (codebook + metadata)
        codebook_path = base_path + '_codebook.npz'
        codebook_data = {
            'codebook': compressed_data['codebook'],
            'original_shape': compressed_data['original_shape'],
            'block_size': compressed_data['block_size'],
            'num_vectors': compressed_data['num_vectors'],
            'is_color': compressed_data['is_color'],
            'compression_ratio': compressed_data['compression_ratio']
        }
        np.savez(codebook_path, **codebook_data)
        codebook_size = os.path.getsize(codebook_path)
        
        return True, f"Compressed image saved to: {image_path}\nCodebook saved to: {codebook_path}\nCompressed image size: {image_size / 1024:.2f} KB\nCodebook size: {codebook_size / 1024:.2f} KB\nTotal size: {(image_size + codebook_size) / 1024:.2f} KB"
    except Exception as e:
        return False, f"Error saving compressed files: {e}"

def load_compressed_files(image_path, codebook_path):
    """Load compressed image and codebook from separate files"""
    try:
        # Load compressed image (indices)
        encoded_indices = np.load(image_path)
        
        # Load codebook and metadata
        codebook_data = np.load(codebook_path, allow_pickle=True)
        codebook = codebook_data['codebook']
        original_shape = codebook_data['original_shape']
        block_size = codebook_data['block_size']
        num_vectors = codebook_data['num_vectors']
        is_color = codebook_data['is_color']
        compression_ratio = codebook_data['compression_ratio']
        
        # Reconstruct block positions (since we don't save them)
        block_height, block_width = block_size
        height, width = original_shape[:2]
        
        # Calculate padding
        pad_width = block_width - (width % block_width) 
        pad_height = block_height - (height % block_height)
        
        # Reconstruct block positions
        padded_height = height + pad_height
        padded_width = width + pad_width
        blocks_per_row = padded_width // block_width
        blocks_per_col = padded_height // block_height
        
        block_positions = []
        for row in range(blocks_per_col):
            for col in range(blocks_per_row):
                start_y = row * block_height
                start_x = col * block_width
                block_positions.append((row, col, start_y, start_x))
        
        compressed_data = {
            'codebook': codebook,
            'encoded_indices': encoded_indices,
            'original_shape': original_shape,
            'block_positions': block_positions,
            'padding': (pad_height, pad_width),
            'block_size': block_size,
            'num_vectors': num_vectors,
            'compression_ratio': compression_ratio,
            'is_color': is_color
        }
        
        return compressed_data, f"Loaded compressed image from: {image_path}\nLoaded codebook from: {codebook_path}"
        
    except Exception as e:
        return None, f"Error loading compressed files: {e}"

def decompress_image(compressed_data):
    """Reconstruct image from compressed data"""
    if compressed_data['is_color']:
        block_shape = (compressed_data['block_size'][0], compressed_data['block_size'][1], 3)
    else:
        block_shape = (compressed_data['block_size'][0], compressed_data['block_size'][1])
    
    # Decode blocks using codebook (substitute labels with vectors)
    decoded_blocks = []
    for idx in compressed_data['encoded_indices']:
        codeword = compressed_data['codebook'][idx]
        block = codeword.reshape(block_shape)
        decoded_blocks.append(block)
    
    # Reconstruct image
    block_height, block_width = compressed_data['block_size']
    pad_height, pad_width = compressed_data['padding']
    original_shape = compressed_data['original_shape']
    
    padded_height = original_shape[0] + pad_height
    padded_width = original_shape[1] + pad_width
    
    if compressed_data['is_color']:
        reconstructed = np.zeros((padded_height, padded_width, 3), dtype=np.float32)
    else:
        reconstructed = np.zeros((padded_height, padded_width), dtype=np.float32)
    
    # Place blocks back into image
    for (row, col, start_y, start_x), block in zip(compressed_data['block_positions'], decoded_blocks):
        if compressed_data['is_color']:
            reconstructed[start_y:start_y+block_height, start_x:start_x+block_width, :] = block
        else:
            reconstructed[start_y:start_y+block_height, start_x:start_x+block_width] = block
    
    # Remove padding
    if pad_height > 0 or pad_width > 0:
        final_image = reconstructed[:original_shape[0], :original_shape[1]]
    else:
        final_image = reconstructed
    
    final_image = np.clip(final_image, 0, 255).astype(np.uint8)
    return final_image

def save_decompressed_image(image, output_path):
    """Save decompressed image"""
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        pil_image = Image.fromarray(image)
        pil_image.save(output_path)
        return True, f"Decompressed image saved to: {output_path}"
    except Exception as e:
        return False, f"Error saving decompressed image: {e}"

# =============================================================================
# GUI IMPLEMENTATION
# =============================================================================

class VectorQuantizationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vector Quantization System (LBG Algorithm)")
        self.root.geometry("800x600")
        
        # Variables
        self.original_image = None
        self.image_path = None
        self.compressed_data = None
        
        self.setup_gui()
    
    def setup_gui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Compression Tab
        compression_frame = ttk.Frame(notebook)
        notebook.add(compression_frame, text="Compress Image")
        
        # Decompression Tab
        decompression_frame = ttk.Frame(notebook)
        notebook.add(decompression_frame, text="Decompress Image")
        
        # Setup both tabs
        self.setup_compression_tab(compression_frame)
        self.setup_decompression_tab(decompression_frame)
    
    def setup_compression_tab(self, parent):
        # Image selection
        ttk.Label(parent, text="Select Image:").grid(row=0, column=0, sticky='w', pady=5)
        
        image_frame = ttk.Frame(parent)
        image_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.image_entry = ttk.Entry(image_frame, width=50)
        self.image_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(image_frame, text="Browse", command=self.browse_image).pack(side='right')
        
        # Parameters frame
        params_frame = ttk.LabelFrame(parent, text="Compression Parameters")
        params_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Block dimensions
        ttk.Label(params_frame, text="Block Width:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.block_width = ttk.Entry(params_frame, width=10)
        self.block_width.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.block_width.insert(0, "4")
        
        ttk.Label(params_frame, text="Block Height:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.block_height = ttk.Entry(params_frame, width=10)
        self.block_height.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        self.block_height.insert(0, "4")
        
        # Codebook size
        ttk.Label(params_frame, text="Codebook Size:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.codebook_size = ttk.Entry(params_frame, width=10)
        self.codebook_size.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.codebook_size.insert(0, "16")
        
        # Output path
        ttk.Label(parent, text="Output Base Path:").grid(row=3, column=0, sticky='w', pady=5)
        
        output_frame = ttk.Frame(parent)
        output_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.output_entry = ttk.Entry(output_frame, width=50)
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.output_entry.insert(0, "compressed_image")
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side='right')
        
        # Compress button
        self.compress_btn = ttk.Button(parent, text="Compress Image", command=self.compress_image)
        self.compress_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky='ew', pady=5)
        
        # Status text
        self.status_text = tk.Text(parent, height=10, width=80)
        self.status_text.grid(row=7, column=0, columnspan=2, sticky='ew', pady=5)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(parent, command=self.status_text.yview)
        scrollbar.grid(row=7, column=2, sticky='ns')
        self.status_text.config(yscrollcommand=scrollbar.set)
    
    def setup_decompression_tab(self, parent):
        # Compressed image selection
        ttk.Label(parent, text="Compressed Image File:").grid(row=0, column=0, sticky='w', pady=5)
        
        comp_image_frame = ttk.Frame(parent)
        comp_image_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.comp_image_entry = ttk.Entry(comp_image_frame, width=50)
        self.comp_image_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(comp_image_frame, text="Browse", command=lambda: self.browse_file(self.comp_image_entry)).pack(side='right')
        
        # Codebook file selection
        ttk.Label(parent, text="Codebook File:").grid(row=2, column=0, sticky='w', pady=5)
        
        codebook_frame = ttk.Frame(parent)
        codebook_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.codebook_entry = ttk.Entry(codebook_frame, width=50)
        self.codebook_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(codebook_frame, text="Browse", command=lambda: self.browse_file(self.codebook_entry)).pack(side='right')
        
        # Output path for decompressed image
        ttk.Label(parent, text="Decompressed Image Path:").grid(row=4, column=0, sticky='w', pady=5)
        
        decomp_output_frame = ttk.Frame(parent)
        decomp_output_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.decomp_output_entry = ttk.Entry(decomp_output_frame, width=50)
        self.decomp_output_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.decomp_output_entry.insert(0, "decompressed_image.jpg")
        
        ttk.Button(decomp_output_frame, text="Browse", command=lambda: self.browse_save_file(self.decomp_output_entry)).pack(side='right')
        
        # Decompress button
        self.decompress_btn = ttk.Button(parent, text="Decompress Image", command=self.decompress_image)
        self.decompress_btn.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.decomp_progress = ttk.Progressbar(parent, mode='indeterminate')
        self.decomp_progress.grid(row=7, column=0, columnspan=2, sticky='ew', pady=5)
        
        # Status text
        self.decomp_status_text = tk.Text(parent, height=10, width=80)
        self.decomp_status_text.grid(row=8, column=0, columnspan=2, sticky='ew', pady=5)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(parent, command=self.decomp_status_text.yview)
        scrollbar.grid(row=8, column=2, sticky='ns')
        self.decomp_status_text.config(yscrollcommand=scrollbar.set)
    
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        if filename:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save Compressed Files As",
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            # Remove extension for base path
            base_path = os.path.splitext(filename)[0]
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, base_path)
    
    def browse_file(self, entry_widget):
        filename = filedialog.askopenfilename(title="Select File")
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def browse_save_file(self, entry_widget):
        filename = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def log_status(self, text, is_compression=True):
        if is_compression:
            self.status_text.insert(tk.END, text + "\n")
            self.status_text.see(tk.END)
        else:
            self.decomp_status_text.insert(tk.END, text + "\n")
            self.decomp_status_text.see(tk.END)
    
    def clear_status(self, is_compression=True):
        if is_compression:
            self.status_text.delete(1.0, tk.END)
        else:
            self.decomp_status_text.delete(1.0, tk.END)
    
    def compress_image(self):
        def compression_thread():
            self.compress_btn.config(state='disabled')
            self.progress.start()
            self.clear_status(True)
            
            try:
                # Load image
                image_path = self.image_entry.get()
                if not image_path:
                    messagebox.showerror("Error", "Please select an image file")
                    return
                
                self.log_status("Loading image...")
                self.original_image, status_msg = load_user_image_gui(image_path)
                if self.original_image is None:
                    self.log_status(status_msg)
                    return
                self.log_status(status_msg)
                
                # Get parameters
                try:
                    block_width = int(self.block_width.get())
                    block_height = int(self.block_height.get())
                    num_vectors = int(self.codebook_size.get())
                except ValueError:
                    self.log_status("Error: Please enter valid numbers for parameters")
                    return
                
                # Validate parameters
                height, width = self.original_image.shape[:2]
                if block_width <= 0 or block_height <= 0:
                    self.log_status("Error: Block dimensions must be positive numbers")
                    return
                if block_width > width or block_height > height:
                    self.log_status(f"Error: Block size cannot be larger than image size ({width}x{height})")
                    return
                
                # Check if codebook size is power of 2
                if not (num_vectors & (num_vectors - 1) == 0) and num_vectors != 0:
                    self.log_status("Warning: Number of vectors should be power of 2 for efficient binary labeling")
                
                # Apply padding and extract blocks
                self.log_status("Extracting blocks...")
                all_blocks, block_positions, final_image, pad_h, pad_w = apply_padding_and_extract_blocks(
                    self.original_image, block_height, block_width
                )
                self.log_status(f"Extracted {len(all_blocks)} blocks")
                
                # Convert blocks to vectors
                self.log_status("Converting blocks to vectors...")
                vectors = []
                for block in all_blocks:
                    vectors.append(block.flatten())
                vectors = np.array(vectors, dtype=np.float32)
                
                # Apply LBG algorithm
                self.log_status("Running LBG algorithm...")
                codebook, indices = lbg_splitting_algorithm(vectors, num_vectors)
                self.log_status(f"LBG completed: {len(codebook)} codevectors")
                
                # Compress data
                self.log_status("Compressing image data...")
                compressed_data, compression_ratio = compress_image_data(
                    all_blocks, block_positions, codebook, indices,
                    self.original_image.shape, (pad_h, pad_w),
                    (block_height, block_width), num_vectors
                )
                self.log_status(f"Compression ratio: {compression_ratio:.2f}:1")
                
                # Save compressed files
                output_base_path = self.output_entry.get()
                if not output_base_path:
                    output_base_path = "compressed_image"
                
                success, save_msg = save_compressed_files(compressed_data, output_base_path)
                if success:
                    self.log_status("Compression completed successfully!")
                    self.log_status(save_msg)
                else:
                    self.log_status(save_msg)
                
            except Exception as e:
                self.log_status(f"Error during compression: {e}")
            finally:
                self.progress.stop()
                self.compress_btn.config(state='normal')
        
        threading.Thread(target=compression_thread, daemon=True).start()
    
    def decompress_image(self):
        def decompression_thread():
            self.decompress_btn.config(state='disabled')
            self.decomp_progress.start()
            self.clear_status(False)
            
            try:
                # Get file paths
                image_path = self.comp_image_entry.get()
                codebook_path = self.codebook_entry.get()
                output_path = self.decomp_output_entry.get()
                
                if not image_path or not codebook_path:
                    messagebox.showerror("Error", "Please select both compressed image and codebook files")
                    return
                
                if not output_path:
                    output_path = "decompressed_image.jpg"
                
                # Load compressed files
                self.log_status("Loading compressed files...", False)
                compressed_data, load_msg = load_compressed_files(image_path, codebook_path)
                if compressed_data is None:
                    self.log_status(load_msg, False)
                    return
                self.log_status(load_msg, False)
                
                # Decompress image
                self.log_status("Decompressing image...", False)
                reconstructed_image = decompress_image(compressed_data)
                self.log_status("Image reconstructed successfully", False)
                
                # Save decompressed image
                self.log_status("Saving decompressed image...", False)
                success, save_msg = save_decompressed_image(reconstructed_image, output_path)
                if success:
                    self.log_status("Decompression completed successfully!", False)
                    self.log_status(save_msg, False)
                    self.log_status(f"Original compression ratio: {compressed_data['compression_ratio']:.2f}:1", False)
                else:
                    self.log_status(save_msg, False)
                
            except Exception as e:
                self.log_status(f"Error during decompression: {e}", False)
            finally:
                self.decomp_progress.stop()
                self.decompress_btn.config(state='normal')
        
        threading.Thread(target=decompression_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = VectorQuantizationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
