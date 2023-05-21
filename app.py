# OpenAI API integration code https://www.youtube.com/watch?v=pGOyw_M1mNE
# Flask code from CS50 project and DigitalOcean
import openai
from flask import Flask, flash, redirect, render_template, request, send_file
import os

# API key 
openai.api_key = "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"

# Configure application
app = Flask(__name__)
app.secret_key = 'very_secret_key'

# Ensure templates are auto-reloaded when modified
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Initialised messages variable, which is a list of dictionaries. Each dictionary is a message with two key value pairs - 'role' and 'content'.
messages = [{"role": "system", "content": "I want you to act as if you are a classic text adventure game and we are playing. I don’t want you to ever break out of your character, and you must not refer to yourself in any way. If I want to give you instructions outside the context of the game, I will use curly brackets {like this} but otherwise you are to stick to being the text adventure program. In this game, the setting is a dark forest. Each room should have at least 3 sentence descriptions. Once I say 'begin', start by displaying the first room at the beginning of the game, and wait for me to give you my first command."}]

# Obtain user input, interact with API and return result.
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        message = request.form['input']
        messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        return render_template('index.html', reply=reply)
    else:
        return render_template('index.html')

# Route to write the conversation into messages.txt and provide to user as download
@app.route('/download')
def download():
    with open('messages.txt', 'w') as f:
        for message in messages:
            f.write(f"{message['role']}: {message['content']}\n")
            f.write("---\n")
    path = "messages.txt"
    return send_file(path, as_attachment=True)

# Route to clear history and reset to default
@app.route('/clear')
def clear():
    # Keyword 'global' to indicate that I want to use the global variable rather than create a new local variable with the same name
    global messages

    # Reset to default
    messages = [{"role": "system", "content": "I want you to act as if you are a classic text adventure game and we are playing. I don’t want you to ever break out of your character, and you must not refer to yourself in any way. If I want to give you instructions outside the context of the game, I will use curly brackets {like this} but otherwise you are to stick to being the text adventure program. In this game, the setting is a dark forest. Each room should have at least 3 sentence descriptions. Once I say 'begin', start by displaying the first room at the beginning of the game, and wait for me to give you my first command."}]

    # Delete messages.txt, flash confirmation then return
    if os.path.exists('messages.txt'):
        os.remove('messages.txt')   
        flash('History cleared', 'success')
    else:
        flash('History already cleared', 'error')
    return redirect('/')

