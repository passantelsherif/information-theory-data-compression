'''
CS - S3,S4
Omar Hany Tohami: 20230269
Omar Bassam Mahmoud: 20230248
Passant Shaaban Abdelazim: 20231036
'''


# Examples for tracing:
# CABRACADABR
# ABAABABAABBBBBBBBBBBBA

def match(search_buff, look_ahead_buff, start_in_search):
    """Finds the longest match of look_ahead_buff in search_buff starting at start_in_search."""
    length = 0
    max_len = len(look_ahead_buff)
    while length < max_len:
        if start_in_search + length < len(search_buff):
            src = search_buff[start_in_search + length] # Still inside search buffer
        else:
            offset_into_matched = length - (len(search_buff) - start_in_search)
            src = look_ahead_buff[offset_into_matched] # Past the end (overlap), copy from the already matched characters from the look-ahead buffer
        if src == look_ahead_buff[length]:
            length += 1
        else:
            break
    return length


def compress(data):
    """Compress a string using a simple LZ77 approach."""
    search_buff = ''
    tags = []
    i = 0
    while i < len(data):
        if data[i] not in search_buff:
            # No match found in search buffer
            tags.append((0, 0, data[i]))
            search_buff += data[i]
            i += 1
        else:
            best_length = 0
            best_j = -1

            # Try all possible matches in search buffer
            for k in range(len(search_buff)):
                if search_buff[k] == data[i]:
                    length = match(search_buff, data[i:], k)
                    # Choose the longer match, or if equal, the closer one (higher k)
                    if length > best_length or (length == best_length and k > best_j):
                        best_length = length
                        best_j = k

            if best_j == -1:
                tags.append((0, 0, data[i]))
                search_buff += data[i]
                i += 1
            else:
                pos = len(search_buff) - best_j
                next_char = data[i + best_length] if i + best_length < len(data) else ''
                tags.append((pos, best_length, next_char))
                search_buff += data[i:i + best_length + 1]
                i += best_length + 1

    return tags


def decompress(tags):
    """Decompress a list of LZ77 tags into the original string."""
    out = []
    for pos, length, next_char in tags:
        if pos == 0 and length == 0:
            # Literal character
            out.append(next_char)
        else:
            start = len(out) - pos
            if start < 0:
                raise ValueError(f"Invalid tag: start={start} before beginning of output")
            for i in range(length):
                out.append(out[start + i])
            if next_char:
                out.append(next_char)
    return ''.join(out)


# --- MAIN PROGRAM INTERFACE ---

while True:
    print("\nLZ77 Compression & Decompression")
    print("1. Compress a string")
    print("2. Decompress tags")
    print("3. Exit")

    choice = input("Choose an option (1/2/3): ").strip()

    if choice == '1':
        data = input("Enter the data to compress: ").strip()
        tags = compress(data)
        print("\nCompressed tags:")
        print(tags)
    elif choice == '2':
        print("Enter tags in the format [(pos, length, 'char'), ...]")
        raw_tags = input("Tags: ")
        try:
            tags = eval(raw_tags)
            result = decompress(tags)
            print("\nDecompressed string:")
            print(result)
        except Exception as e:
            print(f"Error parsing tags: {e}")
    elif choice == '3':
        print("Exiting...")
        break
    else:
        print("Invalid choice! Please select 1, 2, or 3.")
