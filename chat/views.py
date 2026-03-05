from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from accounts.models import User
from .models import Conversation, ConversationMember, Message, MessageReadStatus

from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    PrivateConversationCreateSerializer,
    GroupConversationCreateSerializer
)

class ConversationListView(generics.ListAPIView):
    serializer_class=ConversationSerializer
    permission_classes=[IsAuthenticated]
    
    @method_decorator(cache_page(60*5))
    def list(self,request,*args,**kwargs):
        return super().list(request,*args,**kwargs)
    
    
    def get_queryset(self):
        return Conversation.objects.filter(
            members=self.request.user
        ).prefetch_related('conversation_members__user','messages')
        
        
class PrivateConversationCreateView(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self,request):
        serializer=PrivateConversationCreateSerializer(
            data=request.data,
            context={'request':request}
        )
        if serializer.is_valid():
            other_user_id=serializer.validated_data['user_id']
            other_user=User.objects.get(id=other_user_id)
            
            existing=Conversation.objects.filter(
                conversation_type=Conversation.ConversationType.PRIVATE,
                members=request.user
            ).filter(members=other_user)
            
            if(existing.exists()):
                return Response(
                    ConversationSerializer(existing.first()).data,
                    status=status.HTTP_200_OK 
                )
            
            
            conversation=Conversation.objects.create(
                conversation_type=Conversation.ConversationType.PRIVATE,
                created_by=request.user
            )
            
            ConversationMember.objects.create(conversation=conversation,user=request.user)
            ConversationMember.objects.create(conversation=conversation,user=other_user)
            
            return Response (
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class GroupConversationCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializer=GroupConversationCreateSerializer(
            data=request.data,
            context={'request':request}
        )
        
        if serializer.is_valid():
            member_ids=serializer.validated_data['member_ids']
            
            conversation=Conversation.objects.create(
                name=serializer.validated_data['name'],
                conversation_type=Conversation.ConversationType.GROUP,
                created_by=request.user,
            )
            
            ConversationMember.objects.create(
                conversation=conversation,
                user=request.user,
                is_admin=True
            )
            
            for user_id in member_ids:
                user=User.objects.get(id=user_id)
                ConversationMember.objects.create(
                    conversation=conversation,
                    user=user 
                )
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class=ConversationSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(members=self.request.user)
    
class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_id"]

        serializer.save(
            sender=self.request.user,
            conversation_id=conversation_id
        )
        
        
class MarkMessagesReadView(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self,request,conversation_id):
        if not Conversation.objects.filter(
            id=conversation_id,
            members=request.user
        ).exists():
            return Response(
                {'error': 'Conversation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        messages=Message.objects.filter(
            conversation_id=conversation_id
        ).exclude(sender=request.user)
        
        read_count=0
        for message in messages:
            _, created=MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )
            if created:
                read_count+=1
                
        return Response({
            'message':f'{read_count} messages marked as read.'
        },status=status.HTTP_200_OK)
                