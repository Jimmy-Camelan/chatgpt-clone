import streamlit as st
from streamlit_chat import message
import requests
import json

import openai
from config import open_api_key
openai.api_key = open_api_key

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
    send_notification("Response: "+output)
    history_input.append([user_input, output])
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
