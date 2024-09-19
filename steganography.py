from PIL import Image

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
    
    encrypted_message = xorEncryptDecrypt(secret, message)
    binary_message = stringToBinary(encrypted_message)
    message_length = len(binary_message)

    binary_length = format(message_length, '032b')
    binary_message = binary_length + binary_message

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
    new_image.save("new_"+image_path)
    print(f"Message encoded in new_"+image_path)

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

    encrypted_message_bits = binary_message[32:32 + message_length]

    encrypted_message = binToString(encrypted_message_bits)

    decrypted_message = xorEncryptDecrypt(secret, encrypted_message)

    print(decrypted_message)
    

if __name__ == '__main__':
    print('Welcome to Hide My Bits CLI.')
    my_image = "myimage.png"
    my_message = "what is your name?w"
    password = "sanish"
    # senthesis_message = xorEncryptDecrypt(password, my_message)
    # print(senthesis_message)

    encodeMessageToImage(my_image, my_message, password)

    decodeImageToMessage("new_"+my_image, password)