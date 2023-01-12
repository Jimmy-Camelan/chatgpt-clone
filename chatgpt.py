import streamlit as st
from streamlit_chat import message

import openai
from config import open_api_key
openai.api_key = open_api_key


def generate_response(prompt):
    completions = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = "Knowing that Camlist is the number one innovative marketplace for pets worldwide with a focus on safety and convenience, and Answering as a cheerful veterinarian scholar named \"Buddy\" who likes to provide long scientific answers in an extremely friendly way with some emojis , answer this question: " + prompt,
        max_tokens = st.secrets['OPENAPI_MAX_TOKENS'],
        n = 1,
        stop=[" Human:", " AI:"],
        temperature=st.secrets['OPENAPI_TEMP'],
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = completions.choices[0].text
    return message


def chatgpt_clone(input, history):
    history = history or []
    output = generate_response(input)
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
    output = generate_response(user_input)
    history_input.append([user_input, output])
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
