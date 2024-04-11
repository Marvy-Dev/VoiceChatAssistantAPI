from flask import Flask, request, send_file
from flask import jsonify
import os
from openai import OpenAI
from pathlib import Path
from flask_cors import CORS
# get api key from environment variable OPENAI_API_KEY into .env file
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

def audio(prompt):
    speech_file_path="speech2.wav"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1-hd",
        voice="nova",
        input=prompt,
    ) as response:
        response.stream_to_file(speech_file_path)
def speechToText(audio_file):
    response = client.audio.speech.to_text.create(audio=audio_file)
    return response["text"]

@app.route("/getAudio")
def getAudio():
    # get the prompt from the request query parameter
    prompt = request.args.get('prompt')
    print(prompt)
    audio(prompt)
    return send_file(
        "speech2.wav",
         mimetype="audio/wav",
         as_attachment=True,
         download_name="speech2.wav"
           )
@app.route("/speechToText", methods=["POST"])
def translation():
    # get the audio file and send it to openai to convert it to text, the file comes in blob format into a formdata
    print("request",request) 
    if "audio" not in request.files:
        return jsonify({"error": "No audio file in request"}), 404
    

    audio_file = request.files["audio"]
    text = speechToText(audio_file)
    return jsonify({"text": text})



@app.route("/")
def home():
    return "Application Ready"

if __name__ == "__main__":
    app.run(port=8000)
