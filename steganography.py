from PIL import Image
from collections import Counter
import heapq, json, time


class HuffmanCoding:
    class Node:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

    def __init__(self):
        self.huffman_code = {}

    def build_tree(self, frequencies):
        heap = [self.Node(char, freq) for char, freq in frequencies.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = self.Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(heap, merged)

        return heap[0]

    def generate_codes(self, node, prefix=""):
        if node:
            if node.char is not None:
                self.huffman_code[node.char] = prefix
            self.generate_codes(node.left, prefix + "0")
            self.generate_codes(node.right, prefix + "1")

    def compress(self, text):
        frequency = Counter(text)
        root = self.build_tree(frequency)
        self.generate_codes(root)
        encoded_text = ''.join(self.huffman_code[char] for char in text)
        return encoded_text, self.huffman_code

    @staticmethod
    def decompress(encoded_text, huffman_code):
        reverse_huffman_code = {code: char for char, code in huffman_code.items()}
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in reverse_huffman_code:
                decoded_text += reverse_huffman_code[current_code]
                current_code = ""
        return decoded_text


class XOREncryption:    
    def __init__(self, key):
        self.key = key
    
    def encrypt(self, message):
        encrypted_message = ""
        key_length = len(self.key)

        for i, char in enumerate(message):
            key_char = self.key[i % key_length]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            encrypted_message += encrypted_char
        
        return encrypted_message
    
    def decrypt(self, encrypted_message):
        decrypted_message = ""
        key_length = len(self.key)

        for i, char in enumerate(encrypted_message):
            key_char = self.key[i % key_length]
            decrypted_char = chr(ord(char) ^ ord(key_char))
            decrypted_message += decrypted_char
        
        return decrypted_message



class Steganography:
    def __init__(self, secret_key):
        self.xor = XOREncryption(secret_key)
        self.huffman = HuffmanCoding()

    @staticmethod
    def string_to_binary(data):
        return ''.join(format(byte, '08b') for byte in bytearray(data, 'utf-8'))

    @staticmethod
    def binary_to_string(binary_data):
        byte_array = bytearray()
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i + 8]
            byte_array.append(int(byte, 2))
        return byte_array.decode('utf-8', errors='ignore')

    def serialize_huffman_code(self, huffman_code):
        huffman_string = json.dumps(huffman_code)
        return self.string_to_binary(huffman_string)

    def deserialize_huffman_code(self, binary_data):
        huffman_string = self.binary_to_string(binary_data)
        return json.loads(huffman_string)

    def encode_message_to_image(self, image_path, message):
        image = Image.open(image_path)
        pixels = list(image.getdata())

        compressed_message, huffman_code = self.huffman.compress(message)
        encrypted_message = self.xor.encrypt(compressed_message)
        binary_message = self.string_to_binary(encrypted_message)

        binary_huffman_code = self.serialize_huffman_code(huffman_code)
        combined_message = binary_huffman_code + "1111111101" + binary_message
        message_length = len(combined_message)

        binary_length = format(message_length, '032b')
        binary_message = binary_length + combined_message

        if len(binary_message) > len(pixels) * 3:
            raise ValueError("Message is too long to hide in the image")

        new_pixels = []
        message_index = 0

        for pixel in pixels:
            if message_index < len(binary_message):
                image_mode = image.mode
                if image_mode == 'RGB':
                    r, g, b = pixel
                elif image_mode == 'RGBA':
                    r, g, b, a = pixel
                else:
                    raise ValueError(f"Image has a different mode: {image_mode}")
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
        return new_image

    def decode_image_to_message(self, image_path):
        image = Image.open(image_path)
        pixels = list(image.getdata())

        binary_message = ""
        for pixel in pixels:
            image_mode = image.mode
            if image_mode == 'RGB':
                r, g, b = pixel
            elif image_mode == 'RGBA':
                r, g, b, a = pixel
            else:
                raise ValueError(f"Image has a different mode: {image_mode}")
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

        message_length_bits = binary_message[:32]
        message_length = int(message_length_bits, 2)
        combined_message = binary_message[32:32 + message_length]

        separator_index = combined_message.find('1111111101')
        binary_huffman_code = combined_message[:separator_index]
        encrypted_message_bits = combined_message[separator_index + 10:]

        huffman_code = self.deserialize_huffman_code(binary_huffman_code)
        encrypted_message = self.binary_to_string(encrypted_message_bits)
        decrypted_message = self.xor.decrypt(encrypted_message)

        return self.huffman.decompress(decrypted_message, huffman_code)


if __name__ == "__main__":
    print("Welcome to Hide My Bits CLI.")
    print("1. Encode a message\n2. Decode a message\nPress any other key to quit.")
    choice = input("Enter your choice: ")

    if choice == "1":
        image_name = input("Enter image file name: ")
        message = input("Enter message to encode: ")
        password = input("Enter password: ")
        stego = Steganography(password)
        stego.encode_message_to_image(image_name, message)

    elif choice == "2":
        image_name = input("Enter image file name: ")
        password = input("Enter password: ")
        stego = Steganography(password)
        decoded_message = stego.decode_image_to_message(image_name)
        print("Decoded message:", decoded_message)

    else:
        print("Goodbye!")
