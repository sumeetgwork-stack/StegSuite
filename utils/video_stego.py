import cv2
import numpy as np
import os
import tempfile

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

def encode_video(video_path, secret_message, output_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    binary_secret = text_to_binary(secret_message)
    frames_processed = 0
    bits_encoded = 0
    
    # Use 0 for uncompressed AVI (guaranteed to work everywhere losslessly)
    fourcc = 0
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flatten frame
        flat = frame.flatten()
        
        # Encode bits into this frame
        for i in range(min(len(flat), len(binary_secret) - bits_encoded)):
            if bits_encoded >= len(binary_secret):
                break
            flat[i] = (flat[i] & 254) | int(binary_secret[bits_encoded])
            bits_encoded += 1
        
        # Reshape back
        frame_encoded = flat.reshape(frame.shape)
        out.write(frame_encoded.astype('uint8'))
        frames_processed += 1
        
        if bits_encoded >= len(binary_secret):
            # If message fully encoded, just copy remaining frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    if bits_encoded < len(binary_secret):
        raise ValueError("Video too short for this message!")
    
    return output_path

def decode_video(video_path):
    cap = cv2.VideoCapture(video_path)
    binary = ''
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        flat = frame.flatten()
        for pixel in flat:
            binary += str(pixel & 1)
            # Check if we have enough bits to decode
            if len(binary) >= 8 and len(binary) % 8 == 0:
                if binary[-8:] == '00000000':
                    cap.release()
                    return binary_to_text(binary)
            if len(binary) > 1000000:
                cap.release()
                raise ValueError("No hidden message found in this video.")
    
    cap.release()
    return binary_to_text(binary)