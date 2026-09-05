from PIL import Image
import numpy as np
import os

def text_to_binary(text):
    binary = ''.join(format(ord(char), '08b') for char in text)
    return binary + '00000000'

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    text = ''
    for char in chars:
        if char == '00000000':
            break
        text += chr(int(char, 2))
    return text

def encode_image(image_path, secret_message, output_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()
    binary_secret = text_to_binary(secret_message)
    
    if len(binary_secret) > len(pixels):
        raise ValueError("Image too small for this message!")
    
    for i in range(len(binary_secret)):
        pixels[i] = (pixels[i] & 254) | int(binary_secret[i])
    
    encoded = Image.fromarray(pixels.reshape(img.size[1], img.size[0], 3).astype('uint8'), 'RGB')
    encoded.save(output_path)
    return output_path

def decode_image(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()
    binary = ''.join(str(pixel & 1) for pixel in pixels)
    return binary_to_text(binary)