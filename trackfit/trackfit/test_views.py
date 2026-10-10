"""Test-only views -- only imported when DEBUG=True."""
from django.contrib.auth import login as auth_login, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def e2e_test_login(request):
    User = get_user_model()
    username = request.POST.get("username") or request.GET.get("u", "")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "detail": "user not found"}, status=404)
    auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session["user"] = {"userinfo": {"name": user.username, "email": user.email or f"{user.username}@test.local"}}
    return JsonResponse({"ok": True, "username": user.username})
