from fastapi import FastAPI, Request, UploadFile, File
from moviepy.editor import *
from gtts import gTTS
import os
import json, openai, pandas
import numpy as np
import warnings
import os
import moviepy.video.io.ImageSequenceClip
import pygame
warnings.filterwarnings('ignore')
import configparser

from requests import request

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome"}

@app.post("/generate_video")
async def generate_video(request: Request) :
    try:
       return images_to_video('C:\\Users\\Admin\\projects\\hackathon_team3\\hackathon_team3\\images_new', 54, '.jpeg', 'Spectra_video', '.mp4')
    except Exception as e:
        return str(e)
    
def images_to_video(image_folder_path: str, fps, extension:str, video_name:str, output_format:str):
    images = []
    print(image_folder_path)
    for img in os.listdir(image_folder_path):
        images.append(img)
    images = ['0.jpg', '11.jpg']
    movie_clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(images, fps)
    movie_clip.write_videofile(video_name+output_format)
    video_clip = VideoFileClip("Spectra_video.mp4")
    audio_clip = AudioFileClip("output.mp3")
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile("youtube_v" + ".mp4")	