async def process_text(websocket, path):
    user_input_text = ''
    
    while True:
        message = await websocket.recv()  # Receive audio stream from Twilio
        data = json.loads(message).get('Media')  # Extract audio payload
        audio_data = base64.b64decode(data)  # Base64 decode

        # write audio file 
        with open("input.wav", 'wb') as f:
            f.write(audio_data)

        # Convert voice to text
        text = speech_to_text_german("input.wav")
        
        # Append transcribed text to user_input_text variable
        user_input_text += text

        # Check for silence, indicating end of user's speech
        if detect_silence(audio_data):
            # Process the transcription text here 

            # Get the bot response
            run = submit_message(client, ASSISTANT_ID, thread, user_input_text)
            if run.status == 'requires_action':
                response = pretty_print(check_response(client, thread, run))
            else:
                response = pretty_print(get_response(client, thread))

            # Remove response text characters if needed
            answer_to_question = response
            response_text = re.sub(r'【.*?】', '', answer_to_question)

            # Convert back text to speech
            text_to_speech_german(response_text, "output.wav")

            # read the output file and convert it to base64
            with open('output.wav', "rb") as f:
                output_data = f.read()

            output_base64 = base64.b64encode(output_data).decode('utf-8')

            # Send the message back to Twilio
            await websocket.send(json.dumps({
                "event": "media",
                "stream_sid": "your-stream-sid",  # Replace it with your actual stream_sid
                "media": {
                    "payload": output_base64
                }
            }))

            user_input_text = ''  # Reset user_input_text for the new conversation after silence
    
# Run the WebSocket server in an event loop
start_server = websockets.serve(process_text, 'localhost', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()