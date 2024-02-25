# consumers.py
from channels.exceptions import StopConsumer

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.consumer import AsyncConsumer
from .models import Thread, ChatMessage
from accountApp.models import User

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#         # Extract thread ID from the URL
#         self.thread_id = self.scope['url_route']['kwargs']['thread_id']

#         # Verify and authenticate the user and thread
#         if await self.validate_user_and_thread():
#             # Join room group
#             self.thread_group_name = f"thread_{self.thread_id}"
#             await self.channel_layer.group_add(
#                 self.thread_group_name,
#                 self.channel_name
#             )
#         else:
#             # Disconnect the user if validation fails
#             await self.close()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.thread_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         sender_id = data['sender_id']

#         # Save message to the database (you need to implement this)
#         # ...
#         @database_sync_to_async
#         def save_chat_message(self, thread_id, sender_id, message):
#             thread = Thread.objects.get(id=thread_id)
#             sender_user = User.objects.get(id=sender_id)
#             chat_message = ChatMessage.objects.create(thread=thread, sender=sender_user, message=message)
#             return chat_message.id


#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.thread_group_name,
#             {
#                 'type': 'chat.message',
#                 'message': message,
#                 'sender_id': sender_id,
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         sender_id = event['sender_id']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender_id': sender_id,
#         }))

#     @database_sync_to_async
#     def validate_user_and_thread(self):
#         # Validate and authenticate the user and thread
#         user_id = self.scope['user'].id
#         return Thread.objects.filter(id=self.thread_id, customer_id=user_id).exists() or \
#                Thread.objects.filter(id=self.thread_id, corporate_id=user_id).exists()

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        print("********************************")
        print(chat_room)
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_disconnect(self, event):
        print('disconnect', event)
        await self.channel_layer.group_discard(
        self.chat_room,
        self.channel_name
        )
        raise StopConsumer()
    
    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')

        if not msg:
            print('Error:: empty message')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')

        # is_valid = await self.check_thread_user(thread_obj,sent_by_user,send_to_user)
                
        await self.create_chat_message(thread_obj, sent_by_user, msg)

        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']
        response = {
            'message': msg,
            'sent_by': self_user.id,
            'thread_id': thread_id
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )





    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        ChatMessage.objects.create(thread=thread, sender=user, message=msg)
        
    


    
