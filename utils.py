from openai import OpenAI

def speech_to_text_german(api_key, audio_file_path):
    '''
    params: 
    api_key: str: openai api key
    audio_file_path: str: path to the audio file
    
    returns:
    str: text of the audio file
    '''
    client = OpenAI(api_key=api_key)
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
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
         model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(return_audio_file_path)
    
