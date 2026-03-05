import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone 
from .models import Conversation, Message, MessageReadStatus
from accounts.models import User
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id=self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name=f'chat_{self.conversation_id}'
        self.user=self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return 
        
        is_member=await self.check_membership()
        if not is_member:
            await self.close()
            return 
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.set_online_status(True)
        await self.accept()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'user_status',
                'user_id': self.user.id,
                'username':self.user.username,
                'is_online': True
            }
        )
        
    async def disconnect(self,close_code):
        if hasattr(self,'room_group_name'):
            await self.set_online_status(False)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_online': False,
                }
            )
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    async def receive(self, text_data):
        data=json.loads(text_data)
        event_type=data.get('type')
        
        if event_type =='message.send':
            await self.handle_send_message(data)
            
        elif event_type=='message.read':
            await self.handle_read_receipt(data)
            
    async def handle_send_message(self,data):
        content=data.get('content','').strip()
        
        if not content:
            return 
        
        message=await self.save_message(content)
        
        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                'type': 'chat_message',
                'message_id': message.id,
                'content': message.content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'created_at': str(message.created_at),

            }
        )
        
        
    async def handle_read_receipt(self,data):
        message_id=data.get('message_id')
        
        if not message_id:
            return 
        
        already_read=await self.mark_message_read(message_id)
        
        if not already_read:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'username': self.user.username,

                }
            )
            
    async def chat_message(self,event):
        await self.send(text_data=json.dumps(
            {
            'type': 'message.receive',
            'message_id': event['message_id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'created_at': event['created_at'],

            }
        ))
        
    async def read_receipt(self,event):
        await self.send(text_data=json.dumps(
            {
            'type': 'read.receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username']
            }
        ))
        
    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user.status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online'],
        }))

    @database_sync_to_async
    def check_membership(self):
        return Conversation.objects.filter(
            id=self.conversation_id,
            members=self.user 
        ).exists()
        
    @database_sync_to_async
    def save_message(self,content):
        conversation=Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        
    @database_sync_to_async
    def mark_message_read(self,message_id):
        try:
            message = Message.objects.get(id=message_id)
            _, created = MessageReadStatus.objects.get_or_create(
                message=message,
                user=self.user
            )
            return not created  # returns True if already read
        except Message.DoesNotExist:
            return True
        
    @database_sync_to_async
    def set_online_status(self,is_online):
        User.objects.filter(id=self.user.id).update(
            is_online=is_online,
            last_seen=timezone.now()
        )