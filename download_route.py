from flask import send_file

def download_route(messages):
   with open('messages.txt', 'w') as f:
       for message in messages:
           f.write(f"{message['role']}: {message['content']}\n")
           f.write("---\n")
   path = "messages.txt"
   return send_file(path, as_attachment=True)