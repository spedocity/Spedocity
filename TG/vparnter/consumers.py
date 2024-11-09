# vpartner/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DriverNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def driver_status_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'message': event['message']
        }))
