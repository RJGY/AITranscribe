# Standard library imports
import asyncio
import os
import shutil
import subprocess 
from datetime import datetime

# Third-party imports
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
import google.generativeai as genai
import whisper

load_dotenv()

# Modify the FastAPI app initialization
app = FastAPI()

# Load Whisper model (choose "base", "small", "medium", or "large" for accuracy)
model = whisper.load_model("base")

# Set up Google Gemini API
genai.configure(api_key=os.environ['GENERATIVEAI_API_KEY'])

# Tasks
async def background_task():
    scan_dir = os.environ['SCAN_DIR']  # Get from env or default to 'input'
    # Create directory if it doesn't exist
    os.makedirs(scan_dir, exist_ok=True)

    while True:
        try:
            # List all files in directory
            files = os.listdir(scan_dir)
            if files:
                print(f"Found {len(files)} files: {files}")
                # Process each file concurrently
                tasks = []
                for filename in files:
                    file_path = os.path.join(scan_dir, filename)
                    # Instead of using UploadFile, pass the file path directly
                    task = asyncio.create_task(asyncio.to_thread(process_file, file_path))
                    tasks.append(task)
                
                # Wait for all transcriptions to complete
                if tasks:
                    await asyncio.gather(*tasks)
                    # Remove processed files
                    for filename in files:
                        try:
                            os.remove(os.path.join(scan_dir, filename))
                        except FileNotFoundError:
                            pass
            else:
                print(f"No files found in {scan_dir}")
                
        except Exception as e:
            print(f"Error processing files: {e}")
            
        await asyncio.sleep(60)  # Run every 60 seconds

def process_file(file_path: str) -> str:
    """Process a file from disk instead of an UploadFile"""
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        # Create a new UploadFile for each file
        upload_file = UploadFile(filename=filename, file=f)
        return transcribe(upload_file)


@app.on_event("startup")
async def startup_event():
    """Start background tasks when app starts"""
    asyncio.create_task(background_task())

# Service
def summarize_text(text) -> str:
    """Summarizes the given text using Google's Gemini AI."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Summarize the following text:\n\n{text}")
    return response.text if response.text else "Summary unavailable."


def transcribe(file: UploadFile = File(...)) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    temp_path = f"temp_{timestamp}_{file.filename}"
    output_md = f"{os.path.splitext(file.filename)[0]}_{timestamp}_transcript.md"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create audio directory if it doesn't exist
    audio_dir = os.environ.get("AUDIO_DIR", "processed_audio")
    os.makedirs(audio_dir, exist_ok=True)

    if not temp_path.endswith('.mp3'):
        output_file = os.path.join(audio_dir, f"{os.path.splitext(file.filename)[0]}_{timestamp}.mp3")
        subprocess.run(['ffmpeg', '-i', temp_path, output_file],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.PIPE,
                    check=True)
        # Remove only the temporary file
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass
    else:
        # If it's already an MP3, just move it to the audio directory
        output_file = os.path.join(audio_dir, f"{file.filename}_{timestamp}.mp3")
        shutil.move(temp_path, output_file)

    # Transcribe audio
    result = model.transcribe(output_file)
    transcription = result["text"]

    # Generate summary
    summary = summarize_text(transcription)

    # Create output directory if it doesn't exist
    output_dir = os.environ.get("TRANSCRIPT_DIR", "transcripts")  # Default to 'transcripts' if not set
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to markdown file in the specified directory
    output_path = os.path.join(output_dir, output_md)
    aest_time = datetime.now().strftime("%d %B %Y at %I:%M %p AEST")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Audio Transcription Results\n\n")
        f.write(f"Generated on {aest_time}\n\n")
        f.write("## Summary\n")
        f.write(f"{summary}\n\n")
        f.write("## Full Transcription\n")
        f.write(f"{transcription}\n")

    return output_path


# Endpoint
@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribes audio and returns text + summary."""
    output_path = transcribe(file)

    return {"status": "success", "file": output_path}

# Run server with: uvicorn main:app --host 0.0.0.0 --port 8000