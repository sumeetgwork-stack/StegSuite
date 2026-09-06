# 🛡️ StegSuite — Multi-Format Steganography Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Deploy](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

**Hide your secrets in plain sight.**

StegSuite is a full-stack web application that lets you embed secret messages into images, audio files, video files, and text using various steganography techniques — all from a sleek, modern UI.

[🌐 Live Demo](https://stegsuite.onrender.com) · [🐛 Report Bug](https://github.com/sumeetgwork-stack/StegSuite/issues) · [✨ Request Feature](https://github.com/sumeetgwork-stack/StegSuite/issues)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Steganography Methods](#-steganography-methods)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [How It Works](#-how-it-works)
- [Limitations](#-limitations)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖼️ **Image Steganography** | Hide messages in PNG, JPG, BMP images using LSB encoding |
| 🎵 **Audio Steganography** | Conceal data within WAV audio waveforms |
| 🎬 **Video Steganography** | Embed secrets across video frames using lossless FFV1 codec |
| 📝 **Text Steganography** | 3 methods — Zero-Width Characters, Whitespace, HTML Formatting |
| 🔐 **User Authentication** | Email/Password signup + Google OAuth 2.0 |
| 📱 **Fully Responsive** | Optimized for desktop, tablet, and mobile screens |
| 🎨 **Modern Dark UI** | Amazon Prime-inspired hover card interface |
| ☁️ **Cloud Deployed** | Live on Render with PostgreSQL backend |

---

## 🔬 Steganography Methods

### Image — LSB (Least Significant Bit)
Replaces the least significant bit of each pixel's RGB value with a bit from the secret message. The visual change is imperceptible to the human eye.

```
Original pixel:  (148, 203, 97)  →  Binary: (10010100, 11001011, 01100001)
Secret bits:     1, 0, 1
Modified pixel:  (149, 202, 97)  →  Binary: (10010101, 11001010, 01100001)
```

### Audio — LSB on Raw Samples
Applies the same LSB technique to raw audio sample bytes in WAV files. The audio change is inaudible.

### Video — Frame-by-Frame LSB
Encodes the message across video frames pixel-by-pixel. Uses the **FFV1 lossless codec** to ensure no data is lost during compression.

### Text — Three Methods
| Method | Technique | Visibility |
|--------|-----------|------------|
| **ZWSP** | Zero-Width Space / Non-Joiner characters | Completely invisible |
| **Whitespace** | Spaces vs Tabs at end of lines | Invisible in most editors |
| **Formatting** | Bold/Italic HTML tags | Visible but unsuspicious |

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.10+
- Flask 2.3 (Web Framework)
- Flask-Login (Session Management)
- Flask-SQLAlchemy (ORM)
- Authlib (Google OAuth 2.0)
- Gunicorn (Production Server)

**Frontend:**
- HTML5 / CSS3 / Vanilla JavaScript
- Font Awesome 6 (Icons)
- Inter (Google Fonts)

**Image/Media Processing:**
- Pillow (PIL) — Image manipulation
- NumPy — Pixel array operations
- OpenCV — Video frame processing

**Database:**
- SQLite (Local Development)
- PostgreSQL (Production on Render)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sumeetgwork-stack/StegSuite.git
   cd StegSuite
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask session encryption key | ✅ Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID | ❌ Optional* |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret | ❌ Optional* |
| `DATABASE_URL` | PostgreSQL connection string (production) | ❌ Optional** |

> \* Google login button won't work without these, but email/password login still works.
>
> \*\* Falls back to SQLite if not provided.

---

## 📁 Project Structure

```
StegSuite/
├── app.py                  # Main Flask application & routes
├── models.py               # SQLAlchemy database models
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore
│
├── utils/
│   ├── image_stego.py      # Image encode/decode (LSB)
│   ├── audio_stego.py      # Audio encode/decode (LSB)
│   ├── video_stego.py      # Video encode/decode (Frame LSB)
│   └── text_stego.py       # Text encode/decode (ZWSP, Whitespace, Formatting)
│
├── templates/
│   ├── base.html           # Shared layout (navbar, footer, dropdown)
│   ├── index.html          # Homepage with hover cards
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   └── stego.html          # Encode/Decode interface
│
└── static/
    ├── style.css
    └── uploads/            # Temporary file storage
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/login` | Email/password login |
| GET/POST | `/signup` | Create new account |
| GET | `/logout` | Log out current user |
| GET | `/auth/google` | Initiate Google OAuth flow |
| GET | `/auth/google/callback` | Google OAuth callback |

### Steganography
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stego/<type>?mode=encode` | Encode page (image/audio/video/text) |
| GET | `/stego/<type>?mode=decode` | Decode page |
| POST | `/encode/image` | Encode message into image |
| POST | `/decode/image` | Extract message from image |
| POST | `/encode/audio` | Encode message into audio |
| POST | `/decode/audio` | Extract message from audio |
| POST | `/encode/video` | Encode message into video |
| POST | `/decode/video` | Extract message from video |
| POST | `/encode/text` | Encode message into text |
| POST | `/decode/text` | Extract message from text |
| GET | `/download/<filename>` | Download encoded file |

> ⚠️ All steganography endpoints require authentication (`@login_required`).

---

## ☁️ Deployment

StegSuite is deployed on **[Render](https://render.com)** with a free PostgreSQL database.

### Deploy Your Own

1. Fork this repository
2. Create a **PostgreSQL** database on Render
3. Create a **Web Service** on Render:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Add environment variables (`SECRET_KEY`, `DATABASE_URL`, Google OAuth keys)
5. Deploy!

---

## 🧠 How It Works

### Encoding Flow
```
User uploads file + secret message
        ↓
Message converted to binary (ASCII → 8-bit binary)
        ↓
Null terminator (00000000) appended to mark end
        ↓
LSB of each byte in the cover file is replaced
        ↓
Modified file saved and served for download
```

### Decoding Flow
```
User uploads stego file
        ↓
LSB of each byte is extracted
        ↓
Bits are grouped into 8-bit chunks
        ↓
Stops when null terminator (00000000) is found
        ↓
Binary converted back to text (ASCII)
```

---

## ⚠️ Limitations

- **Lossless formats only** — Image output is always PNG, video output is AVI (FFV1). Lossy compression (JPEG, MP4 H.264) destroys the hidden data.
- **No encryption** — Messages are hidden but not encrypted. Anyone who knows it's LSB steganography can extract the message. For sensitive data, encrypt your message before encoding.
- **Compatibility** — Can only decode files created with the same LSB method. Files from other steganography tools using different algorithms won't work.
- **File size** — Message length is limited by the cover file size. Roughly 1 character per 8 pixels/samples.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Sumeet](https://github.com/sumeetgwork-stack)**

</div>
