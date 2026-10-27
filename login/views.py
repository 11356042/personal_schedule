import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import RegisterForm

"""解析請求內容，必須是 JSON 物件，否則回傳 None"""
def _parse_json(request):
    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _user_data(user):
    return {"username": user.username}

"""把表單錯誤整理成 {欄位: [錯誤原因, ...]} 的格式"""
def _form_errors(form):
    return {
        field: [e["message"] for e in errors]
        for field, errors in form.errors.get_json_data().items()
    }

INVALID_JSON_MSG = "請求內容不是有效的 JSON 物件，請檢查是否漏掉引號、逗號或大括號"

"""
註冊帳號
前端須傳："username", "password"
"""
@csrf_exempt
@require_POST
def register_view(request):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"錯誤訊息": INVALID_JSON_MSG}, status=400)

    form = RegisterForm(data)
    if not form.is_valid():
        return JsonResponse({"錯誤訊息": _form_errors(form)}, status=400)

    user = form.save()
    login(request, user)
    return JsonResponse({"message": "註冊成功", "user": _user_data(user)}, status=201)

"""
登入帳號
前端須傳："username", "password"
"""
@csrf_exempt
@require_POST
def login_view(request):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"錯誤訊息": INVALID_JSON_MSG}, status=400)

    missing = [f for f in ("username", "password") if not data.get(f)]
    if missing:
        return JsonResponse({"錯誤訊息": f"缺少必填欄位：{'、'.join(missing)}"}, status=400)

    username = data["username"]
    password = data["password"]
    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse({"錯誤訊息": "username 與 password 的值必須是字串"}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is None or user.username != username:
        return JsonResponse({"錯誤訊息": "登入失敗：帳號不存在、密碼錯誤"}, status=401)

    login(request, user)
    return JsonResponse({"message": "登入成功", "user": _user_data(user)})


@require_GET
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"錯誤訊息": "請先登入"}, status=401)
    return JsonResponse(_user_data(request.user))