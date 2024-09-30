import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import openai
from deepgram import Deepgram
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
CALLER_NUMBER = os.getenv("CALLER_NUMBER")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, CALLER_NUMBER)
deepgram = Deepgram(DEEPGRAM_API_KEY)
openai.api_key = (OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)
@app.route("/")
def start():
    return "Welcome to the New World of Artificial Intelligence "
@app.route("/voice", methods=["POST"])
def voice():
    """Handles incoming Twilio calls"""
    response = VoiceResponse()
    response.say("HELLO HOW CAN I HELP YOU ?? ")
    response.record(max_length=30, action="/process_recording")
    return str(response)

@app.route("/process_recording", methods=["POST"])
def process_recording():
    """Processes the recording with Deepgram and responds using OpenAI"""
    recording_url = request.form['RecordingUrl']

    transcription = transcribe_audio(recording_url)

    ai_response = generate_response(transcription)

    response = VoiceResponse()
    response.say(ai_response)
    return str(response)

def transcribe_audio(recording_url):
    """Transcribes audio using Deepgram"""
    try:
        source = {'url': recording_url}
        response = deepgram.transcription.prerecorded(source, {'punctuate': True})
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except Exception as e:
        return f"Error in transcription: {str(e)}"

def generate_response(transcription):
    """Generates a response using OpenAI's GPT"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"The user said: {transcription}. Generate a helpful response:",
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in AI response generation: {str(e)}"

if __name__== "__main__":
    app.run(debug=True)

