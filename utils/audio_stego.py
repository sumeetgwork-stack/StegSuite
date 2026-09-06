import wave
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

def encode_audio(audio_path, secret_message, output_path):
    # Read WAV file
    wav = wave.open(audio_path, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()
    
    # Convert to numpy array as uint8 for format-agnostic byte manipulation
    audio_array = np.frombuffer(frames, dtype=np.uint8).copy()
    binary_secret = text_to_binary(secret_message)
    
    if len(binary_secret) > len(audio_array):
        raise ValueError("Audio file too short for this message!")
    
    # Encode LSB
    for i in range(len(binary_secret)):
        audio_array[i] = (audio_array[i] & 254) | int(binary_secret[i])
    
    # Save new WAV
    new_wav = wave.open(output_path, 'wb')
    new_wav.setnchannels(wav.getnchannels())
    new_wav.setsampwidth(wav.getsampwidth())
    new_wav.setframerate(wav.getframerate())
    new_wav.writeframes(audio_array.tobytes())
    new_wav.close()
    return output_path

def decode_audio(audio_path):
    wav = wave.open(audio_path, 'rb')
    frames = wav.readframes(wav.getnframes())
    wav.close()
    
    audio_array = np.frombuffer(frames, dtype=np.uint8)
    binary = ''
    for sample in audio_array:
        binary += str(sample & 1)
        if len(binary) >= 8 and len(binary) % 8 == 0:
            if binary[-8:] == '00000000':
                break
        if len(binary) > 1000000:
            raise ValueError("No hidden message found in this file.")
    return binary_to_text(binary)