from fastapi import FastAPI, Request, UploadFile, File
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip
from gtts import gTTS
import os

from requests import request

app = FastAPI()

@app.get("/")
async def root():
    # text = "Hello, this is a test."
    # tts = gTTS(text=text, lang='en')
    # tts.save("output.mp3")
    # os.system("output.mp3")
    return {"message": "Hello World"}

def create_video(images_folder, text, output_path):
    # Get all image files from the folder
    image_files = sorted([f for f in os.listdir(images_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
    
    # Create ImageClips from images
    clips = [ImageClip(os.path.join(images_folder, img)).set_duration(3) for img in image_files]

    # Add text narration
    text_clip = TextClip(text, fontsize=30, color='white').set_duration(len(clips) * 3)
    text_clip = text_clip.set_pos(('center', 'bottom'))

    # Concatenate ImageClips and text clip
    final_clip = concatenate_videoclips(clips)
    final_clip = final_clip.set_audio(text_clip.audio)

    # Write the final video to output_path
    final_clip.write_videofile(output_path, codec='libx264', fps=24)

@app.post("/generate_video")
async def generate_video(request: Request) :
    try:
        data = await request.json()
        output_path = "output_video.mp4"
        
        text =  data.get("text", "Default text if not provided in the request")
        images_folder = data.get("images_folder", None)
        with open(images_folder, "wb") as buffer:
            buffer.write(images_folder.file.read())
        create_video(images_folder, text, output_path)
    except Exception as e:
        return str(e)