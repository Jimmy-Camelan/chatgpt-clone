
import streamlit as st
from streamlit_chat import message
import openai
from google.cloud import texttospeech
from google.oauth2 import service_account
import json
import os
from config import open_api_key
import base64
import re


openai.api_key = open_api_key

def get_audio_str(file_name):
    """
    [Return] a string Base64 of a binary file
    [Arguments] file_name path to file 
    """
    aud_file= open(file_name,"rb")
    aud_data_binary = aud_file.read()
    aud_data = (base64.b64encode(aud_data_binary)).decode('ascii')
    return aud_data

def remove_emojis(data):
    """
    [Return] a string stripped from emojies
    [Arguments] data a string to be stripped
    """
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)
def google_auth(sa, sa_private_key):
    """
    [Return] a Google client with credentils based on the passed params based on supplied credentials
    [Arguments] sa is the JSON string of the service account
                sa_private_key is the private key to be added to the service account
    """
    SA_str = sa
    info = json.loads(SA_str)
    info['private_key'] = sa_private_key
    credentials = service_account.Credentials.from_service_account_info(info)
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    return client

def text_to_speech(text_to_convert, config={}):
    """
    [Return] a google TTS response object
    [Arguments] text_to_convert
                config TBD
    """
    text_to_convert = remove_emojis(text_to_convert)
    sa = os.environ.get('SERVICE_ACCOUNT')
    sa_private_key = os.environ.get('SA_PRIVATE_KEY')
    client = google_auth(sa, sa_private_key)


    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text_to_convert)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-F",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config)
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    
    return response


def send_notification(msg):
    url = st.secrets["SLACK_WEBHOOK"]
    payload = json.dumps({
        "text": msg
    })
    headers = {
     'Content-type': 'application/json'
     }
    response = requests.request("POST", url, headers=headers, data=payload)


def generate_response(prompt):
    completions = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = "Knowing that Camlist is the number one innovative marketplace for pets worldwide with a focus on safety and convenience, and Answering as a cheerful veterinarian scholar named \"Buddy\" who likes to provide long scientific answers in an extremely friendly way with some emojis , answer this question: \"" + prompt + "\"",
        max_tokens = st.secrets['OPENAPI_MAX_TOKENS'],
        stop=[" Human:", " AI:"],
        temperature=st.secrets['OPENAPI_TEMP'],
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = completions.choices[0].text
    return message


def chatgpt_clone(input, history):
    send_notification("Received Message: {}".format(input))
    history = history or []
    generated_response = generate_response(input)
    output = generatd_response
    
    history.append((input, output))
    return history, history

# Streamlit App
st.set_page_config(
    page_title="Camlist Pet Assistant",
    page_icon=":dog:"
)

st.header("Hi there! I am Buddy,")

history_input = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def get_text():
    input_text = st.text_input("I am the world's first pet assistant powered by artificial intelligence. Ask me anything related to pets, and I will answer:", key="input")
    return input_text 


user_input = get_text()


if user_input:
    send_notification("Received Message:" + user_input)
    output = generate_response(user_input)
    text_to_speech(output)
    TTS_file = get_audio_str("./output.mp3")
    send_notification("Response: "+output)
    history_input.append([user_input, output])
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    else:
        html_string = """
        <div>
        <style type="text/css" scoped>
        audio{
        width: 30%;
        }
        @media only screen and (min-width: 400px) {
        audio{
        width:10%
        }
    </style>
      <audio id='audio' controls autoplay style='position:fixed; top:160px; right:30px;'>
""" + "<source src=\"data:audio/mpeg;base64,{}\">".format(TTS_file) + """
        Your browser does not support the audio element.
      </audio>
"""
        sound = st.empty()
        sound.markdown(html_string, unsafe_allow_html=True)
