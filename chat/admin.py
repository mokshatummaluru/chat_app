from django.contrib import admin
from .models import Conversation, ConversationMember, Message, MessageReadStatus

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display=['id','conversation_type','name','created_by','created_at']
    list_filter=['conversation_type']
    search_fields=['name','created_by__username']
    
@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display=['id','conversation','user','joined_at','is_admin']
    list_filter=['is_admin']
    search_fields=['user__username']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=['id','conversation','sender','content','is_deleted','created_at']
    list_filter=['is_deleted']
    search_fields=['content','sender__username']
    
@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display=['message','user','read_at']
    search_fields=['user__username']