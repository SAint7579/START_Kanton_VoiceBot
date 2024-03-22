import streamlit as st
from streamlit_mic_recorder import mic_recorder
import re
from utils import *  # speech_to_text_german, submit_message, etc.


JSON_DATA = {}
# Function to process audio data and get text
def process_audio_data(audio_data, key):
    with open("audio/output.wav", "wb") as out_file:
        out_file.write(audio_data['bytes'])

    translated_text = speech_to_text_german(api_key=key, audio_file_path="audio/output.wav")
    return translated_text

# Function to get the bot's response
def get_bot_response(translated_text):
    run = submit_message(client, ASSISTANT_ID, thread, translated_text)
    run = wait_on_run(client, run, thread)
    if run.status == 'requires_action':
        response = pretty_print(check_response(client,thread,run))
        json_data = run.required_action.submit_tool_outputs.tool_calls[0].function.arguments
        st.json(json_data)
        
    else:
        response = pretty_print(get_response(client, thread))

    answer = re.sub(r'\【.*?\】', '', response)

    if answer:
        text_to_speech_german(api_key=key, text=answer, return_audio_file_path=f"audio/final.mp3")
        st.audio("audio/final.mp3")
        
        # autoplay_audio(f"audio/final.mp3")
        
    return answer

# Function to update conversation history
def update_conversation_history(translated_text, answer):
    st.session_state['conversation_history'].append(f"**You:** {translated_text}")
    st.session_state['conversation_history'].append(f"**asKanton:** {answer}")


# Set page configuration
st.set_page_config(page_title='askCanton Bot', layout='wide')

# Define language code and API key
LANG_CODE = "de-DE"  # German Language code
key = ""  # Your API key here (if needed)

# Initialize Session State for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

# Main container for chat
main_container = st.container()

# Left sidebar for conversation history
with st.sidebar:
    st.markdown("## Conversation History:")
    for index, item in enumerate((st.session_state['conversation_history'])):
        if index % 2 == 1:
            st.markdown(f"{item}")
        else:
            st.markdown(f"{item}")

# Title and User Input
with main_container:
    st.title('asKanton')
    st.markdown("#### Current Conversation:")

    # Audio recording
    audio_data = mic_recorder(
        key="audio_recorder",
        start_prompt="Press to Record",
        stop_prompt="Recording... Press again to stop",
        format="wav",
    )

    # Check if audio data exists
    if audio_data:
        # Process and display user's question
        st.success("Recording complete! Processing your question...")
        translated_text = process_audio_data(audio_data, key)
        st.text_input("Your question:", value=translated_text, disabled=True)

        # Process and display bot's response
        answer = get_bot_response(translated_text)
        st.text_area("asKanton:", value=answer, disabled=False)
        

        # Update conversation history (left sidebar will automatically update)
        update_conversation_history(translated_text, answer)
        
    # Record button if no audio data
    else:
        st.info("Press the button to record your question!")
