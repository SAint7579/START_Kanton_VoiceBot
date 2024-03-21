from openai import OpenAI
import os
import json
import time
import ast


key = "" #enter your api key here

client = OpenAI(api_key=key)
assistant = client.beta.assistants.retrieve(assistant_id='asst_HBm9X29io6tMuiphtvQeTuyh')
thread = client.beta.threads.create()
ASSISTANT_ID = assistant.id

def speech_to_text_german(api_key, audio_file_path):
    '''
    params: 
    api_key: str: openai api key
    audio_file_path: str: path to the audio file
    
    returns:
    str: text of the audio file
    '''
    # client = OpenAI(api_key=api_key)
    audio_file= open(audio_file_path, "rb")
    translation = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return translation.text

def text_to_speech_german(api_key, text, return_audio_file_path):
    '''
    params: 
    api_key: str: openai api key
    text: str: text to convert to speech
    return_audio_file_path: str: path to save the audio file
    
    returns:
    str: path to the audio file
    '''
    # client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
         model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(return_audio_file_path)


def submit_message(client,assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(client,thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def pretty_print(messages):
    result = ""
    for m in messages.data[-1:]:
        result += f"{m.content[0].text.value}\n"
    result += "\n"
    return result

# Waiting in a loop
def wait_on_run(client,run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def check_response(client,thread,run):
        # Extract single tool call
    tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    response = {'success': "Forwarding the call to the department. Ask user to hold"}

    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps(response),
            }
        ],
    )
    
    run = wait_on_run(client,run, thread)
    return get_response(client,thread)

# if __name__ == "__main__":
#     run = submit_message(client,ASSISTANT_ID, thread, "Can you connect me to the city department?")
#     run = wait_on_run(client,run, thread)
#     if run.status == 'requires_action':
#         response = pretty_print(check_response(client,thread,run))
#         print(response)
#     else:
#         response = pretty_print(get_response(client,thread))
#         print(response)
    
