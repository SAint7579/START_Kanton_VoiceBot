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
    translation = client.audio.translations.create(
        model="whisper-1", 
        file=audio_file
    )
    return translation.text
