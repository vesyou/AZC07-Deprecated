import openai

openai.api_key = "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"

conversation_history = ""
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": "Please tell a joke"}]
    )
response = completion.choices[0].message.content
print(response)
conversation_history += response
print(conversation_history)
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What was the last question?" + conversation_history}] 
    )
response = completion.choices[0].message.content
print(response)


"""
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Please say 'Hi, you are in a testing enviroment'."}])
response = completion.choices[0].message.content
print(response)
"""