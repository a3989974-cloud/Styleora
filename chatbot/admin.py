from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from .models import ChatSession
from . import mongo_utils


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'updated_at']
    search_fields = ['session_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


# Inject dashboard URL into admin site
original_get_urls = admin.site.get_urls


def patched_get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('chatbot-dashboard/', admin.site.admin_view(dashboard_view), name='chatbot-dashboard'),
    ]
    return custom_urls + urls


def dashboard_view(request):
    sessions = mongo_utils.get_all_sessions(100)
    total_sessions = len(sessions)
    total_messages = sum(
        mongo_utils.get_session_message_count(s.get('session_id', ''))
        for s in sessions
    )
    mongo_status = mongo_utils.is_connected()

    context = {
        'title': 'AI Chatbot Dashboard',
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'mongo_status': mongo_status,
        'sessions': sessions,
        'has_permission': request.user.is_staff,
        'site_title': 'STYLEORA Admin',
        'site_header': 'STYLEORA Administration',
    }
    return TemplateResponse(request, 'admin/chatbot_dashboard.html', context)


admin.site.get_urls = patched_get_urls
