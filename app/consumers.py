# Yenda/consumers.py
import json
import datetime  

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        try:
            # Parse JSON data
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # Get current timestamp
            timestamp = datetime.datetime.now().isoformat()

            # Send message back to client with timestamp
            self.send(text_data=json.dumps({
                "message": message,
                "timestamp": timestamp
            }))
        except (KeyError, json.JSONDecodeError) as e:
            # Handle errors (e.g., log the error)
            print(f"Error parsing received data: {e}")
