import heapq
import struct

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

# Return every symbol as key and its frequency as value in a dict
def get_freq_text(file_name):
    # Read the file to encode
    with open(file_name, 'r') as input_file:
        data = input_file.read()

    freq_dict = {char: data.count(char) for char in data}
    return freq_dict, data

# Building tree using min heap from heapq module
def build_tree(freq_dict):
    heap = [Node(char, freq) for char, freq in freq_dict.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(heap, merged)
    
    return heap[0] # Return last node or the root

# Using recursion to give each node code in the heap
def get_codes(root):
    def traverse(node, code, codes):
        if node:
            if node.char: # Only add the node that contain symbol in the dict not the merged nodes
                codes[node.char] = code
            traverse(node.left, code + '0', codes)
            traverse(node.right, code + '1', codes)
    
    codes = {}
    traverse(root, "", codes)
    return codes

# Encoding the string itself
def encode_text(text, codes):
    encoded_string = ""
    for character in text:
        encoded_string += codes[character]
    return encoded_string

# Uses the same tree for decoding
def decode_text(encoded_string, root):
    decoded_text = ""
    current_node = root
    
    for bit in encoded_string:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
            
        if current_node.char is not None: # Found a leaf node or symbol node
            decoded_text += current_node.char
            current_node = root  # always return to root for next symbol
    
    return decoded_text

# Main execution
def main():
    file_name = input('Enter file name: ')

    # Get frequency dictionary and original text
    freq_dict, original_text = get_freq_text(file_name)

    # Generate Huffman tree and codes
    huffman_tree = build_tree(freq_dict)
    huffman_codes = get_codes(huffman_tree)
    
    # Encode the text
    encoded_string = encode_text(original_text, huffman_codes)
    
    # Convert binary string to actual bytes using struct.pack()
    # Pad the string to make length multiple of 8
    padding = (8 - len(encoded_string) % 8) % 8
    padded_string = encoded_string + '0' * padding
    
    # Convert to bytes using struct.pack()
    encoded_bytes = b''
    for i in range(0, len(padded_string), 8):
        byte_chunk = padded_string[i:i+8]
        # Convert binary string to integer and pack as unsigned char
        encoded_bytes += struct.pack('B', int(byte_chunk, 2))
    
    # Create output filename
    output_filename = file_name.split('.')[0] + '_encoded.bin'
    
    # Save encoded binary data
    with open(output_filename, 'wb') as f:
        # Write metadata (original length and padding)
        f.write(struct.pack('II', len(encoded_string), padding))
        # Write the actual encoded data
        f.write(encoded_bytes)
    
    print(f"\nEncoding completed!")
    print(f"Original text length: {len(original_text)} characters")
    print(f"Encoded string length: {len(encoded_string)} bits")
    print(f"Compressed size: {len(encoded_bytes) + 8} bytes")  # +8 for metadata
    print(f"Output saved to: {output_filename}")
    
    # Display Huffman codes
    print("\nHuffman Codes:")
    for char, code in sorted(huffman_codes.items()):
        print(f"'{char}': {code}")
    
    with open(output_filename, 'rb') as f:
        # Read metadata
        original_length, padding = struct.unpack('II', f.read(8))
        # Read encoded data
        encoded_bytes = f.read()
    
    # Convert bytes back to binary string
    binary_string = ""
    for byte in encoded_bytes:
        # Unpack each byte and format as 8-bit binary string
        binary_string += format(struct.unpack('B', bytes([byte]))[0], '08b')
    
    # Remove padding
    binary_string = binary_string[:original_length]
    
    # Decode using the same tree
    decompressed_text = decode_text(binary_string, huffman_tree)
    
    # Save the decoded text
    decoded_filename = file_name.split('.')[0] + '_decoded.txt'
    with open(decoded_filename, 'w') as f:
        f.write(decompressed_text)
    
    print(f"\nDecoding completed!")
    print(f"Decoded text saved to: {decoded_filename}")

# Run the program
if __name__ == "__main__":
    main()
