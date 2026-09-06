import re

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

# Method 1: Zero-Width Characters (Invisible)
def encode_text_zwsp(cover_text, secret_message):
    """
    Uses invisible directional marks to hide bits.
    Using LTR (\u200E) and RTL (\u200F) marks because mobile clipboards and 
    apps like WhatsApp NEVER strip them (they are required for bidirectional text).
    """
    binary_secret = text_to_binary(secret_message)
    zwsp_chars = {
        '0': '\u200E',  # Left-to-Right Mark
        '1': '\u200F'   # Right-to-Left Mark
    }
    
    if len(cover_text) < len(binary_secret):
        raise ValueError("Cover text too short! Need at least 1 character of cover text per bit of secret message.")
    
    # Hide binary in between characters of cover text
    stego_text = ''
    for i, char in enumerate(cover_text):
        stego_text += char
        if i < len(binary_secret):
            stego_text += zwsp_chars[binary_secret[i]]
    
    return stego_text

def decode_text_zwsp(stego_text):
    zwsp_chars = {
        '\u200E': '0',
        '\u200F': '1'
    }
    
    binary = ''
    for char in stego_text:
        if char in zwsp_chars:
            binary += zwsp_chars[char]
    
    return binary_to_text(binary)

# Method 2: Whitespace Steganography (Tabs vs Spaces)
def encode_text_whitespace(cover_text, secret_message):
    """
    Uses normal space vs non-breaking space to hide bits
    (More robust against copy/paste than tabs)
    """
    binary_secret = text_to_binary(secret_message)
    words = cover_text.split()
    
    if len(words) - 1 < len(binary_secret):
        raise ValueError("Cover text too short! Need more words.")
    
    stego_text = ''
    for i, word in enumerate(words):
        stego_text += word
        if i < len(words) - 1:
            if i < len(binary_secret):
                # \u00A0 is Non-Breaking Space
                stego_text += '\u00A0' if binary_secret[i] == '1' else ' '
            else:
                stego_text += ' '
    
    return stego_text

def decode_text_whitespace(stego_text):
    binary = ''
    # Find all spaces and non-breaking spaces between words
    # A regex to match spaces (\x20) and NBSP (\xA0)
    for char in stego_text:
        if char == '\u00A0':
            binary += '1'
        elif char == ' ':
            binary += '0'
            
    return binary_to_text(binary)

# Method 3: Text Formatting (Bold/Italic/Underline in HTML)
def encode_text_formatting(cover_text, secret_message):
    """
    For HTML/DOCX - uses bold/italic to encode bits
    """
    binary_secret = text_to_binary(secret_message)
    words = cover_text.split()
    
    if len(words) < len(binary_secret):
        raise ValueError("Cover text too short!")
    
    stego_words = []
    for i, word in enumerate(words):
        if i < len(binary_secret):
            if binary_secret[i] == '1':
                stego_words.append(f'<b>{word}</b>')
            else:
                stego_words.append(f'<i>{word}</i>')
        else:
            stego_words.append(word)
    
    return ' '.join(stego_words)

def decode_text_formatting(stego_text):
    binary = ''
    # Extract bold/italic tags
    bold_matches = re.findall(r'<b>(.*?)</b>', stego_text)
    italic_matches = re.findall(r'<i>(.*?)</i>', stego_text)
    
    # Check which came first in text order
    # Simplified: we need to parse order
    words = re.split(r'(<b>.*?</b>|<i>.*?</i>)', stego_text)
    
    for word in words:
        if word.startswith('<b>'):
            binary += '1'
        elif word.startswith('<i>'):
            binary += '0'
    
    return binary_to_text(binary)