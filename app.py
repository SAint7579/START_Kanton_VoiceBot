from streamlit_mic_recorder import mic_recorder
import streamlit as st
import re
from utils import *

key = "" #enter your api key here, works even if not given
audio = mic_recorder(
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=False,
    use_container_width=False,
    format="webm",
    callback=None,
    args=(),
    kwargs={},
    key=None
)
with open("audio/output.wav", "wb") as out_file:  # open for [w]riting as [b]inary
    out_file.write(audio['bytes'])

# do translation
translated_text = speech_to_text_german(api_key=key, audio_file_path="audio/output.wav")
st.write("Translated text is :" + translated_text)

run = submit_message(client,ASSISTANT_ID, thread, translated_text)
run = wait_on_run(client,run, thread)
if run.status == 'requires_action':
    response = pretty_print(check_response(client,thread,run))
    # print(response)
else:
    response = pretty_print(get_response(client,thread))
    # print(response)
# do rag
answer = response
answer = re.sub(r'【.*?】', '', answer)
st.write("Answer: "+ answer)
#convert rag text output to audio file
text_to_speech_german(api_key=key, text= answer, return_audio_file_path= "audio/final.mp3")
st.audio("audio/final.mp3")