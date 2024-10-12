# AITranscribe
fast quick and dirty transcribe with python and whisper and bard

main issue with scriberr is that it doesnt work nicely with windows and i want something thats fast quick and dirty, something that it can output the text directly to my notes, hell even take my notes for me so this should be much easier. dont get me wrong his shit is nice too but theres so much front end fluff that idgaf about. its too big and heavy for me to justify running on a docker instance and it doesnt even convert my files from my shitty m4a or whatever to mp3 even though it has ffmpeg. and its alot easier to make it than to recode his stuff. 

workflow:
you put the audio file into thee folder, it picks it up and transcribes it and adds a summary. writes both the transcription and summary into a markdown file.