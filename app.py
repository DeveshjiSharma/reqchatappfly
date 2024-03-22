from twilio.rest import Client
from nudenet import NudeClassifier
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from PIL import Image
from io import BytesIO
import base64
import os

account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)



@app.route("/")
def index():
    return render_template('index.html')

@socketio.on("message")
def handle_message(message):
    if message is None:
        return  
    else:
        print("Received message: " + message)
        send(message, broadcast=True)

@socketio.on('image')
def handle_image(image_data):
    imgin=image_data[image_data.index(',')+1:]
    decoded_image_data = base64.b64decode(imgin)
    img=Image.open(BytesIO(decoded_image_data))
    output_jpg=img.convert('RGB')
    output_jpg.save('desc.jpg')
    current_directory = os.getcwd()
    image_path = os.path.join(current_directory, 'desc.jpg')
    try:
        classifier = NudeClassifier()
        pred = classifier.classify(image_path)
        print("Predictions:", pred)
        for file_path, inner_dict in pred.items():
            unsafe_value = inner_dict.get('unsafe', 0.0)  
            safe_value = inner_dict.get('safe', 0.0)  
            print(f"Unsafe value: {unsafe_value}")
            print(f"Safe value: {safe_value}")
            if unsafe_value > 0.5:
                message = client.messages.create(
                      from_='+15642343837',
                      body='Your son chintu was sending some inappropriate content',
                      to='+917738874661'  
                    )
                print(message.sid)
                emit('unsafe')
            else:
                emit('image', image_data, broadcast=True)
    except Exception as e:
        print(f"Error: {str(e)}")
        
    finally:
        os.remove(image_path)


if __name__ == "__main__":
    app.debug = True
    socketio.run(app)











