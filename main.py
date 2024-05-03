from flask import Flask, request, send_file, jsonify
from flask_uploads import UploadSet, IMAGES, configure_uploads
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
import os
import json
import hashlib
from openai import OpenAI
import base64
from flask_cors import CORS

# get api key from environment variable OPENAI_API_KEY into .env file
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

uploads = UploadSet("images", IMAGES)
app.config["UPLOADED_IMAGES_DEST"] = "uploads"
app.config["SECRET_KEY"] = os.urandom(24)
configure_uploads(app, uploads)
myFolder = os.getenv("UPLOAD_FOLDER")


def gen_audio(prompt):
    speech_file_path = "speech2.wav"
    with client.audio.speech.with_streaming_response.create(
            model="tts-1-hd",
            voice="onyx",
            input=prompt,
    ) as response:
        response.stream_to_file(speech_file_path)

@app.route("/getAudio")
def getAudio():
    # get the prompt from the request query parameter
    prompt = request.args.get('prompt')
    print(prompt)
    gen_audio(prompt)
    return send_file(
        "speech2.wav",
        mimetype="audio/wav",
        as_attachment=True,
        download_name="speech2.wav"
    )


@app.route("/")
def home():

    return "Application Ready"


# Get blob file from post an just reproduce it in the browser
@app.route("/myfile", methods=["POST"])
def myfile():
    try:

        data = request.data
        decoded_data = json.loads(data.decode('utf-8'))
        audio_base64 = decoded_data['audio']
        audio_bytes = base64.b64decode(audio_base64)
        final_json_response = upload_file(audio_bytes)
        return final_json_response
    except Exception as e:
        return jsonify({"error": str(e)}), 404


def upload_file(fileAudio):
    try:

        filename = "MyAudioFile.webm"
        file_path = os.path.join(myFolder, filename)
        print("File path:", file_path)
        if not os.path.exists(myFolder):
            return jsonify({"error": "Folder not found"}), 404
        # Save the file in the folder myFolder


        with open(file_path, "wb") as file:
            file.write(fileAudio)
            print("File saved successfully")

        print("Archivo guardado con éxito:", file_path)

        audio_file = open(file_path, "rb")
        text_from_audio = speechToText(audio_file)

        return jsonify({"message": "File uploaded successfully", "text":text_from_audio}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


def calculate_sha256(data):
    hash_object = hashlib.sha256(data)
    hash_hex = hash_object.hexdigest()
    return hash_hex


# Return dthe audio file from the base64 string


def speechToText(audio_file):
    try:
        transcript = client.audio.transcriptions.create(
          model="whisper-1",
          file=audio_file,
          response_format="text"
        )
        print("Transcript:", transcript)
        return transcript
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run()
