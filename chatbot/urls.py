from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chatbot-chat'),
    path('history/', views.history, name='chatbot-history'),
    path('clear/', views.clear_history, name='chatbot-clear'),
    path('admin/sessions/', views.admin_sessions, name='chatbot-admin-sessions'),
    path('admin/delete-session/', views.admin_delete_session, name='chatbot-admin-delete'),
]
