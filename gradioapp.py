# Import required libraries
import gradio as gr
import openai
from gradio.outputs import HTML

# API key, obtained from your own OpenAI account
openai.api_key = "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"

# Initialised messages variable, which is a list of dictionaries. Each dictionary is a message, represented by two keys: 'role' and 'content'
# Role for the first message is 'system' as it is a prompt/instructions
messages = [{"role": "system", "content": "I want you to act as if you are a classic text adventure game and we are playing. I don’t want you to ever break out of your character, and you must not refer to yourself in any way. If I want to give you instructions outside the context of the game, I will use curly brackets {like this} but otherwise you are to stick to being the text adventure program. In this game, the setting is a dark forest. Each room should have at least 3 sentence descriptions. Once I say 'begin', start by displaying the first room at the beginning of the game, and wait for me to give you my first command."}]

# Function to interface with API 
# Reference: https://www.youtube.com/watch?v=pGOyw_M1mNE
def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

# Gradio interface: https://gradio.app/creating-a-chatbot/
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="A Dark Forest: An Interactive Adventure - Type 'begin' to start!")
    msg = gr.Textbox(label="Your response")
    clear = gr.Button("Clear")
    openai_button = gr.Button("Visit OpenAI")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        bot_message = CustomChatGPT(history[-1][0])
        history[-1][1] = bot_message
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

    # Add an OpenAI button that links to the OpenAI website
    openai_button.output = HTML(
        '<a href="https://openai.com" target="_blank"><button>Visit OpenAI</button></a>'
    )

demo.launch()



"""
import openai
import gradio as gr

openai.api_key = "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"

messages = [{"role": "system", "content": "I want you to act as if you are a classic text adventure game and we are playing. I don’t want you to ever break out of your character, and you must not refer to yourself in any way. If I want to give you instructions outside the context of the game, I will use curly brackets {like this} but otherwise you are to stick to being the text adventure program. In this game, the setting is a dark forest. Each room should have at least 3 sentence descriptions. Once I say 'begin', start by displaying the first room at the beginning of the game, and wait for me to give you my first command."}]

def CustomChatGPT(user_input):
    # if conditional for the various buttons

    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

demo = gr.Interface(
    fn=CustomChatGPT, 
    inputs = gr.inputs.Textbox(label="Your response"), 
    outputs = gr.inputs.Textbox(label="Messages"),
    title = "A Dark Forest: An Interactive Adventure",
    description="Welcome to 'A Dark Forest: An Interactive Adventure'! Please say 'begin' to start the game.",
    allow_flagging="never"
    )

demo.launch(share=False)


demo = gr.Interface(
    fn=CustomChatGPT, 
    inputs = gr.inputs.Text(label="Your response"), 
    outputs = gr.inputs.Text(label="Messages"),
    title = "A Dark Forest"
    )

"""

