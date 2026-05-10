import json
import uuid
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import mongo_utils
from . import openai_utils

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['POST'])
def chat(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    message = (body.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    if len(message) > 2000:
        return JsonResponse({'error': 'Message too long (max 2000 characters)'}, status=400)

    session_id = body.get('session_id') or request.session.get('chatbot_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chatbot_session_id'] = session_id

    mongo_utils.create_session(session_id)
    mongo_utils.save_message(session_id, 'user', message)

    history = mongo_utils.get_history(session_id)
    reply = openai_utils.get_chat_response(history[:-1], message)
    mongo_utils.save_message(session_id, 'assistant', reply)

    return JsonResponse({
        'reply': reply,
        'session_id': session_id,
        'search_used': False,
    })


@require_http_methods(['GET'])
def history(request):
    session_id = request.GET.get('session_id') or request.session.get('chatbot_session_id')
    if not session_id:
        return JsonResponse({'messages': []})
    messages = mongo_utils.get_history(session_id)
    return JsonResponse({'messages': messages, 'session_id': session_id})


@csrf_exempt
@require_http_methods(['POST'])
def clear_history(request):
    session_id = request.GET.get('session_id') or request.session.get('chatbot_session_id')
    if session_id:
        mongo_utils.clear_history(session_id)
    if 'chatbot_session_id' in request.session:
        del request.session['chatbot_session_id']
    return JsonResponse({'status': 'cleared'})


@require_http_methods(['GET'])
def admin_sessions(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    sessions = mongo_utils.get_all_sessions()
    result = []
    for s in sessions:
        sid = s.get('session_id', '')
        result.append({
            'session_id': sid,
            'created_at': s.get('created_at', '').isoformat() if s.get('created_at') else '',
            'updated_at': s.get('updated_at', '').isoformat() if s.get('updated_at') else '',
            'message_count': mongo_utils.get_session_message_count(sid),
        })
    return JsonResponse({'sessions': result})


@csrf_exempt
@require_http_methods(['POST'])
def admin_delete_session(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    session_id = request.GET.get('session_id') or (json.loads(request.body).get('session_id') if request.body else None)
    if not session_id:
        return JsonResponse({'error': 'session_id required'}, status=400)
    mongo_utils.clear_history(session_id)
    return JsonResponse({'status': 'deleted'})
