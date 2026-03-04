from django.db import models
from accounts.models import User

class Conversation(models.Model):
    class ConversationType(models.TextChoices):
        PRIVATE='PRIVATE', 'private',
        GROUP ='GROUP', 'group'
        

    name=models.CharField(max_length=255, blank=True, null=True)
    conversation_type=models.CharField(
        max_length=10,
        choices=ConversationType.choices,
        default=ConversationType.PRIVATE
    )

    members=models.ManyToManyField(
        User,
        through='ConversationMember',
        related_name='conversations'
    )
    
    created_by=models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_conversations'
    )
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering=['-updated_at']

    def __str__(self):
        if(self.conversation_type==self.ConversationType.GROUP):
            return f"Group:{self.name}"
        return f"Private Conversation ({self.id})"
    
    

class ConversationMember(models.Model):
    conversation=models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='conversation_members'
    )
    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_memberships'
    )
    joined_at=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    
    class Meta:
        unique_together=['conversation','user']
        
    def __str__(self):
        return f"{self.user.username} in {self.conversation}"
    
    
    
class Message(models.Model):
    conversation=models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    sender=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    content=models.TextField()
    is_deleted=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering=['created_at']
        
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    
    
class MessageReadStatus(models.Model):
    message=models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_statuses'
    )
    
    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='read_messages'
    )
    
    read_at=models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together=['message','user']
        
    def __str__(self):
        return f"{self.user.username} read message {self.message.id}"
    