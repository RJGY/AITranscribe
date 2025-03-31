# AITranscribe

A lightweight, fast audio transcription service that automatically converts audio files to text, generates summaries, and saves them as markdown files. Built with Python, Whisper AI, and Gemini AI.

## Features

- 🎯 Automatic audio file detection and processing
- 🔄 Automatic file format conversion to MP3 using FFmpeg
- 📝 High-quality transcription using OpenAI's Whisper
- 📚 AI-powered summaries using Google's Gemini
- 📋 Clean markdown output format
- 🔄 Background processing service
- 🚀 FastAPI endpoint for direct uploads

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn whisper google-generativeai python-dotenv python-multipart
```

2. Install FFmpeg (required for audio conversion)

3. Create a `.env` file with:
```env
GENERATIVEAI_API_KEY=your_gemini_api_key
SCAN_DIR=path/to/input/folder
TRANSCRIPT_DIR=path/to/output/folder
```

## Usage

### Option 1: Automatic File Processing
1. Start the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
2. Drop audio files into your `SCAN_DIR` folder
3. Files will be automatically processed and transcripts will appear in `TRANSCRIPT_DIR`

### Option 2: API Endpoint
Send POST requests to `/transcribe/` with audio files:
```bash
curl -X POST -F "file=@your_audio.mp3" http://localhost:8000/transcribe/
```

## Output Format

Transcripts are saved as markdown files with:
- Timestamp of generation
- AI-generated summary
- Full transcription text

## Requirements

- Python 3.8+
- FFmpeg
- Google Gemini API key