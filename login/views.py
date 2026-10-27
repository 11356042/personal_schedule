import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import RegisterForm

"""解析請求內容，必須是 JSON 物件，否則回傳 None"""
def _parse_json(request):
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _user_data(user):
    return {
        "username": user.username,
        "account": user.username,
        "student_id": user.username,
        "class_name": "資管一甲",
    }

"""把表單錯誤整理成 {欄位: [錯誤原因, ...]} 的格式"""
def _form_errors(form):
    return {
        field: [e["message"] for e in errors]
        for field, errors in form.errors.get_json_data().items()
    }

INVALID_JSON_MSG = "請求內容不是有效的 JSON 物件，請檢查是否漏掉引號、逗號或大括號"

"""
註冊帳號
前端須傳："username" 或 "account", "password"
"""
@csrf_exempt
@require_POST
def register_view(request):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"錯誤訊息": INVALID_JSON_MSG}, status=400)

    # 允許前端使用 account 欄位註冊
    if "username" not in data and "account" in data:
        data["username"] = data["account"]

    form = RegisterForm(data)
    if not form.is_valid():
        return JsonResponse({"錯誤訊息": _form_errors(form)}, status=400)

    user = form.save()
    login(request, user)
    return JsonResponse({"message": "註冊成功", "user": _user_data(user)}, status=201)

"""
登入帳號
前端可傳："username" 或 "account", "password", 可選 "remember" / "rememberAccount"
支援 GET (顯示 login.html 頁面) 與 POST (處理登入認證，支援 JSON 與表單提交)
"""
@csrf_exempt
def login_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/timetable/")
        return render(request, "login.html")

    if request.method != "POST":
        return JsonResponse({"錯誤訊息": "不支援的請求方法"}, status=405)

    is_json = request.content_type == "application/json" or not request.POST
    if is_json:
        data = _parse_json(request)
        if data is None:
            return JsonResponse({"錯誤訊息": INVALID_JSON_MSG}, status=400)
    else:
        data = request.POST.dict()

    # 支援 username 或 account
    username = data.get("username") or data.get("account")
    password = data.get("password")

    missing = []
    if not username:
        missing.append("account" if "account" in data and "username" not in data else "username")
    if not password:
        missing.append("password")

    if missing:
        msg = f"缺少必填欄位：{'、'.join(missing)}"
        if is_json:
            return JsonResponse({"錯誤訊息": msg}, status=400)
        return render(request, "login.html", {"error": msg})

    if not isinstance(username, str) or not isinstance(password, str):
        msg = "username 與 password 的值必須是字串"
        if is_json:
            return JsonResponse({"錯誤訊息": msg}, status=400)
        return render(request, "login.html", {"error": msg})

    user = authenticate(request, username=username, password=password)

    if user is None or user.username != username:
        msg = "登入失敗：帳號不存在、密碼錯誤"
        if is_json:
            return JsonResponse({"錯誤訊息": msg}, status=401)
        return render(request, "login.html", {"error": msg})

    login(request, user)

    # 記住帳號 (remember / rememberAccount)
    remember = data.get("remember") or data.get("rememberAccount")
    if remember and str(remember).lower() not in ("false", "0", "null", "undefined"):
        # 記住兩週
        request.session.set_expiry(1209600)
    else:
        # 瀏覽器關閉即過期
        request.session.set_expiry(0)

    if is_json:
        return JsonResponse({
            "message": "登入成功",
            "user": _user_data(user),
            "redirect_url": "/timetable/"
        })
    return redirect("/timetable/")


@require_GET
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"錯誤訊息": "請先登入"}, status=401)
    return JsonResponse(_user_data(request.user))
