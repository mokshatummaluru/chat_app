from django.urls import path
from .views import (
    ConversationListView,
    GroupConversationCreateView,
    ConversationDetailView,
    MessageListView,
    MarkMessagesReadView,
    PrivateConversationCreateView,
)
urlpatterns = [
    path('conversations/',ConversationListView.as_view(),name='conversation-list'),
    path('conversations/private/',PrivateConversationCreateView.as_view(),name='private-conversation-create'),
    path('conversations/group/', GroupConversationCreateView.as_view(), name='group-conversation-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('conversations/<int:conversation_id>/read/', MarkMessagesReadView.as_view(), name='mark-read'),
]