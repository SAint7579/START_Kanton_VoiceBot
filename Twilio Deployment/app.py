from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
app = Flask(__name__)

# @app.route("/answer", methods=['GET', 'POST'])
# def voice():
#     response = VoiceResponse()
#     response.say('Hello world, and thank you for your call from the Flask application.')
#     return str(response)



app = Flask(_name_)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    # response.say('Welcome to the Voice Transcription.')
    response.start().stream(url='wss://yourwebsocketserver.com')

    return Response(str(response), mimetype='text/xml')
if __name__ == "__main__":
    app.run(debug=True)