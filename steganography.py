from PIL import Image
from collections import defaultdict, Counter
import heapq, json, time

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def buildHuffmanTree(frequencies):
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = Node(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)
    
    return heap[0]

def generateHuffmanCodes(node, prefix='', huffman_code={}):
    if node:
        if node.char is not None:
            huffman_code[node.char] = prefix
        generateHuffmanCodes(node.left, prefix + '0', huffman_code)
        generateHuffmanCodes(node.right, prefix + '1', huffman_code)
    
    return huffman_code

def huffmanCompress(text):
    frequency = Counter(text)
    huffman_tree = buildHuffmanTree(frequency)
    huffman_code = generateHuffmanCodes(huffman_tree)

    encoded_text = ''.join(huffman_code[char] for char in text)
    
    return encoded_text, huffman_code

def huffmanDecompress(encoded_text, huffman_code):
    reverse_huffman_code = {code: char for char, code in huffman_code.items()}

    current_code = ""
    decoded_text = ""
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_huffman_code:
            decoded_text += reverse_huffman_code[current_code]
            current_code = ""
    
    return decoded_text

def serializeHuffmanCode(huffman_code):
    huffman_string = json.dumps(huffman_code)
    return stringToBinary(huffman_string)

def deserializeHuffmanCode(binary_data):
    huffman_string = binToString(binary_data)
    return json.loads(huffman_string)\

def stringToBinary(data):
    return ''.join(format(byte, '08b') for byte in bytearray(data, 'utf-8'))

def binToString(binary_data):
    byte_array = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array.decode('utf-8', errors='ignore')

def xorEncryptDecrypt(secret, message):
    senthesis_message = ""

    for i, c in enumerate(message):
        secret_char = secret[i % len(secret)]
        senthesis_char = chr(ord(c) ^ ord(secret_char))
        senthesis_message += senthesis_char

    return senthesis_message

def encodeMessageToImage(image_path, message, secret):
    image = Image.open(image_path)
    pixels = list(image.getdata())
    
    compressed_message, huffman_code = huffmanCompress(message)
    encrypted_message = xorEncryptDecrypt(secret, compressed_message)
    binary_message = stringToBinary(encrypted_message)

    # Serialize the Huffman code and appended it to binary message
    binary_huffman_code = serializeHuffmanCode(huffman_code)
    combined_message = binary_huffman_code + "1111111101" + binary_message # 11111111 to seperate huffmanc code and message
    message_length = len(combined_message)

    binary_length = format(message_length, '032b')
    binary_message = binary_length + combined_message

    if len(binary_message) > len(pixels) * 3:
        raise ValueError("Message is too long to hide in the image")

    new_pixels = []
    message_index = 0

    for pixel in pixels:
        if message_index < len(binary_message):
            r, g, b = pixel
            if message_index < len(binary_message):
                r = (r & ~1) | int(binary_message[message_index])
                message_index += 1
            if message_index < len(binary_message):
                g = (g & ~1) | int(binary_message[message_index])
                message_index += 1
            if message_index < len(binary_message):
                b = (b & ~1) | int(binary_message[message_index])
                message_index += 1
            new_pixels.append((r, g, b))
        else:
            new_pixels.append(pixel)

    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_pixels)
    new_image_name = "new_"+str(time.time())+"_"+image_path
    new_image.save(new_image_name)
    return new_image_name

def decodeImageToMessage(image_path, secret):
    image = Image.open(image_path)
    pixels = list(image.getdata())

    binary_message = ""

    for pixel in pixels:
        r, g, b = pixel
        binary_message += str(r & 1)
        binary_message += str(g & 1)
        binary_message += str(b & 1)

    message_length_bits = binary_message[:32]
    message_length = int(message_length_bits, 2)

    combined_message = binary_message[32:32 + message_length]

    separator_index = combined_message.find('1111111101')

    # Extract the binary Huffman code and the encrypted message
    binary_huffman_code = combined_message[:separator_index]
    encrypted_message_bits = combined_message[separator_index + 10:]

    huffman_code = deserializeHuffmanCode(binary_huffman_code)

    encrypted_message = binToString(encrypted_message_bits)

    decrypted_compressed_message = xorEncryptDecrypt(secret, encrypted_message)

    decompressed_message = huffmanDecompress(decrypted_compressed_message, huffman_code)
    
    return decompressed_message

if __name__ == '__main__':
    print('Welcome to Hide My Bits CLI.')
    print('1. To Encode \n2. To Decode\nPress any key to quit')
    chocie = input("Enter Here: ")
    
    if chocie == "1":
        image_name = input("Enter Image Name: ")
        my_message = input("Enter Message: ")
        password = input("Enter Password: ")

        new_image_name = encodeMessageToImage(image_name, my_message, password)
        print(f"Message encoded in "+new_image_name)
    elif chocie == "2":
        image_name = input("Enter Image Name: ")
        password = input("Enter Password: ")

        decoded_message = decodeImageToMessage(image_name, password)
        print(decoded_message)
    else:
        exit()