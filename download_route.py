from flask import send_file

def download_route(summariser_msg):
   with open('messages.txt', 'w') as f:
       for message in summariser_msg:
           f.write(f"{message['role']}: {message['content']}\n")
           f.write("---\n")
   path = "messages.txt"
   return send_file(path, as_attachment=True)