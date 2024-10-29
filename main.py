import whisper
import os
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
import time

def main():
    genai.configure(api_key=os.getenv("GENERATIVEAI_API_KEY"))
    model = whisper.load_model("base")
    ai = genai.GenerativeModel("gemini-1.5-flash")
    folders = [os.getenv("FOLDER_TO_SCAN"), os.getenv("FOLDER_TO_SCAN_2")]
    print(folders)
    while True:
        for folder in folders:
            files = scan_folder(folder)
            for file in files:
                old_file = file
                if ".mp3" not in file:
                    output_file = os.path.splitext(file)[0] + ".mp3"
                    subprocess.run(['ffmpeg', '-i', file, output_file])
                    file = output_file
                result = model.transcribe(file)
                summary = ai.generate_content("Summarise the following text between the three hashtags ### " + result["text"] + " ### ")
                # save to scanned files as a .md file
                filename = f"voice_memo_{time.strftime('%Y-%m-%d-%H-%M-%S')}.md"
                with open(os.path.join(os.getenv("TEXT_OUTPUT"), filename), "w") as f:
                    f.write("# " + os.path.splitext(filename)[0] + "\n\n## Summary\n\n" + summary.text + "\n\n## Transcription\n\n" + result["text"] + "\n")
                if not old_file.endswith(".mp3"):
                    os.remove(old_file)
            # clean up files
            files = scan_folder(folder)
            for file in files:
                os.rename(file, os.path.join(os.getenv("SCANNED_FILES"), os.path.basename(file)))
            
        # sleep for 60 seconds
        time.sleep(60)
    
    
def scan_folder(folder_to_scan: str) -> list[str]:
    print("scanning folder " + folder_to_scan)
    files = [os.path.join(folder_to_scan, f) for f in os.listdir(folder_to_scan)]
    return files


if __name__ == "__main__":
    main()
    
    