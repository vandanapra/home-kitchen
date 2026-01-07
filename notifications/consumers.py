import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.seller_id = self.scope["url_route"]["kwargs"]["seller_id"]
        self.room_group_name = f"orders_{self.seller_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_order_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))
