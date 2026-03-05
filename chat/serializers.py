from rest_framework import serializers
from .models import Conversation, ConversationMember, Message, MessageReadStatus
from accounts.serializers import UserSerializer
from .models import User
from accounts.models import User

class ConversationMemberSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    
    class Meta:
        model=ConversationMember
        fields=['id','user','is_admin','joined_at']
        
class MessageSerializer(serializers.ModelSerializer):
    sender=UserSerializer(read_only=True)
    read_by=serializers.SerializerMethodField()
    
    class Meta:
        model=Message
        fields=['id','sender','content','is_deleted','created_at','read_by']
        
        
    def get_read_by(self,obj):
        return obj.read_statuses.values_list('user__username',flat=True)
    
    
class ConversationSerializer(serializers.ModelSerializer):
    members=ConversationMemberSerializer(
        source='convcersation_members',
        many=True,
        read_only=True 
    )
    last_message=serializers.SerializerMethodField()
    created_by=UserSerializer(read_only=True)
    
    class Meta:
        model=Conversation
        fields=[
            'id','name','conversation_type','members',
            'last_message','created_by','created_at','updated_at'
        ]
        
    def get_last_message(self,obj):
        last=obj.messages.last()
        if last:
            return {
                'id':last.id,
                'sender':last.sender.username,
                'content':last.content if not last.is_deleted else 'This message was deleted.',
                'created_at':last.created_at
            }
        return None 
    
class PrivateConversationCreateSerializer(serializers.Serializer):
    user_id=serializers.IntegerField()
    
    def validate_user_id(self,value):
        request=self.context['request']
        if(value==request.user.id):
            raise serializers.ValidationError('You cannot start a conversation with yourself.')
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError('User does not exist.')
        return value 
    
    
    
class GroupConversationCreateSerializer(serializers.ModelSerializer):
    member_ids=serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True 
    )
    
    class Meta:
        model=Conversation
        fields=['name','member_ids']
        
    def validate_name(self,value):
        if not value or not value.strip():
            raise serializers.ValidationError('Group name is required.')
        return value
    
    def validate_member_ids(self,value):
        request=self.context['request']
        if request.user.id in value:
            value.remove(request.user.id)
        if len(value)<1:
            raise serializers.ValidationError('Add at least one other member.')
        for user_id in value:
            if not User.objects.filter(id=user_id).exists():
                raise serializers.ValidationError(f'User with id {user_id} does not exist.')
        return value
    