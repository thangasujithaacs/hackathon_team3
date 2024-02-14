from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from moviepy.editor import *
from gtts import gTTS
import os
import json, openai, pandas
import numpy as np
import warnings
import moviepy.video.io.ImageSequenceClip
import pygame
warnings.filterwarnings('ignore')
import configparser
from fastapi.responses import JSONResponse
from requests import request
from dotenv import load_dotenv
from googleapiclient.discovery import build
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import cv2
from hugchat.login import Login
from hugchat import hugchat
from hugchat.message import Message

load_dotenv()

app = FastAPI()

# Setting API keys
yt_api_key = os.environ.get("yt_api_key")
huggingface_username = os.environ.get("huggingface_username")
huggingface_pwd = os.environ.get("huggingface_pwd")
openai_api_key = os.environ.get("openai_api_key")

# Set OpenAI API key
openai.api_key = openai_api_key

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
    
@app.get("/process_video")
async def process_video(video_url: str, num_frames: int = 5):
    try:
        # Extract video ID from the video link
        video_id = video_url.split('v=')[1]

        # Get the transcript for the video
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        captions = youtube.captions().list(part='snippet', videoId=video_id).execute()
        caption = captions['items'][0]['id']

        video_response = youtube.videos().list(part='snippet', id=video_id).execute()
        thumbnails = video_response['items'][0]['snippet']['thumbnails']

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_txt = ""

        for transcript in transcript_list:
            transcript_txt += transcript['text']

        summary = ""
        images = []

        if transcript_txt != "":
            # Log in to huggingface and grant authorization to huggingchat
            sign = Login(huggingface_username, huggingface_pwd)
            cookies = sign.login()

            # Save cookies to the local directory
            cookie_path_dir = "./cookies_snapshot"
            sign.saveCookiesToDir(cookie_path_dir)

            # Create a ChatBot
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

            # Extract the summary from the response
            message = chatbot.query(
                "Summarize in 10 lines if the given data is more than 10 lines: " + transcript_txt)
            print(message[0],'ytr')
            # Extract the text from the Message object
            summary = message.text if hasattr(
                message, 'text') else str(message)

        try:
            # Capture frames directly from the YouTube video stream
            output_frames_folder = "frames"
            images = capture_frames(
                video_url, output_frames_folder, num_frames)
        except Exception as e:
            print(f"Error capturing frames: {e}")

        return JSONResponse(content={ "success": True,"summary": summary, "images": images})

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing video: {str(e)}")


def capture_frames(video_url, output_folder='frames', num_frames=5):
    image_paths = []
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(file_extension='mp4', res='360p').first()

        cap = cv2.VideoCapture(stream.url)
        frame_count = 0
        success, image = cap.read()

        while success and frame_count < num_frames:
            frame_count += 1
            frame_path = f"{output_folder}/frame_{frame_count}.png"
            cv2.imwrite(frame_path, image)
            image_paths.append(os.path.abspath(frame_path))
            success, image = cap.read()

        cap.release()
        print(f"{num_frames} frames captured.")
    except Exception as e:
        print(f"Error capturing frames: {e}")

    return image_paths
