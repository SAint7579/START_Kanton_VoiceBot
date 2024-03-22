from flask import Flask, request, make_response
from twilio.twiml.voice_response import VoiceResponse
import openai
from openai import OpenAI
import json
# Fill in your OpenAI API key
client = OpenAI(api_key='')
assistant = client.beta.assistants.retrieve(assistant_id='asst_HBm9X29io6tMuiphtvQeTuyh')


app = Flask(__name__)

@app.route("/transcribe", methods=['GET', 'POST'])
def transcribe():
    twiml = VoiceResponse()

    # Creating a thread
    thread = client.beta.threads.create()
    print(thread.id)  # You can store this ID or log it as needed

    if not request.cookies.get('convo'):
        twiml.say("Hallo! Ich bin Polly, ein Chatbot, der mit Twilio und ChatGPT erstellt wurde. Worüber möchten Sie heute sprechen?", voice='Polly.Joanna-Neural')

    gather = twiml.gather(
        speech_timeout='auto',
        speech_model='experimental_conversations',
        input='speech',
        action=f'/respond?threadId={thread.id}',
        language = 'de-DE'
    )

    response = make_response(str(twiml))
    response.headers['Content-Type'] = 'application/xml'
    
    if not request.cookies.get('convo'):
        response.set_cookie('convo', '', path='/')

    return response

@app.route("/respond", methods=['POST'])
def respond():
    # Retrieve the thread ID from the request query parameters
    thread_id = request.args.get("threadId")
    print("Retrieved", thread_id)

    # Set up the Twilio VoiceResponse object to generate the TwiML
    twiml = VoiceResponse()

    # Parse the cookie value if it exists
    cookie_value = request.cookies.get('convo')
    # cookie_data = json.loads(cookie_value) if cookie_value else None
    cookie_data = None

    # Get the user's voice input from the event
    voice_input = request.form.get("SpeechResult")
    print("User message", voice_input)

    # Create a conversation variable to store the dialog and the user's input to the conversation history
    conversation = cookie_data.get('conversation') if cookie_data else []
    conversation.append(f"user: {voice_input}")

    # Get the AI's response
    ai_response = create_chat_completion(thread_id, voice_input)

    # Clean the AI's response
    cleaned_ai_response = ai_response.replace(r'^\w+:\s*', '').strip()

    # Add the AI's response to the conversation history
    conversation.append(f"assistant: {cleaned_ai_response}")

    # Generate some <Say> TwiML using the cleaned-up AI response
    twiml.say(cleaned_ai_response, voice="Polly.Joanna-Neural")

    # Redirect to the Function where the <Gather> is capturing the caller's speech
    twiml.redirect(url="/transcribe", method="POST")

    # Prepare the Flask response
    response = make_response(str(twiml))
    response.headers["Content-Type"] = "application/xml"

    # Update the conversation history cookie
    new_cookie_value = json.dumps({'conversation': conversation})
    # response.set_cookie("convo", new_cookie_value, path="./")

    return response

# Function to handle the creation and retrieval of conversation runs
def create_chat_completion(thread_id, voice_input):
    try:
        # Send user message to the thread
        my_thread_message = client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=voice_input
        )

        # Run the thread to get the AI's response
        my_run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id='asst_HBm9X29io6tMuiphtvQeTuyh',
        )

        # Keep retrieving run info until it is completed
        while True:
            retrieved_run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=my_run.id,
            )

            if retrieved_run.status == "completed":
                break

        # Retrieve all messages in the thread
        all_messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")

        # Return the latest AI message
        return all_messages.data[0].content[0].text.value

    except openai.error.OpenAIError as e:
        print(f"Error during OpenAI API request: {str(e)}")
        return "Something went wrong. Please try again."

    
if __name__ == "__main__":
    app.run(debug=True)