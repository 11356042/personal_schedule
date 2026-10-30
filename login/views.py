import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .forms import RegisterForm
from .models import SchoolClass, UserProfile


"""解析請求內容，必須是 JSON 物件，否則回傳 None"""
def _parse_json(request):
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


"""動態取得使用者的 Profile 資料"""
def _user_data(user):
    profile = getattr(user, "profile", None)
    
    role = profile.role if profile else "student"
    role_display = profile.get_role_display() if profile else "學生"
    class_name = profile.school_class.name if profile and profile.school_class else None
    real_name = profile.real_name if profile else user.username
    student_id = profile.student_id if profile else user.username
    
    return {
        "username": user.username,
        "account": user.username,
        "real_name": real_name,
        "student_id": student_id,
        "role": role,
        "role_display": role_display,
        "class_name": class_name,
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
支援 GET (顯示註冊頁面) 與 POST (處理註冊邏輯)
註冊成功後不進行自動登入，引導使用者重導向至登入頁
"""
@csrf_exempt
def register_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/timetable/")
        school_classes = SchoolClass.objects.all()
        return render(request, "login.html", {"school_classes": school_classes})

    if request.method != "POST":
        return JsonResponse({"錯誤訊息": "不支援的請求方法"}, status=405)

    is_json = request.content_type == "application/json" or not request.POST
    if is_json:
        data = _parse_json(request)
        if data is None:
            return JsonResponse({"錯誤訊息": INVALID_JSON_MSG}, status=400)
    else:
        data = request.POST.dict()

    # 允許前端使用 account 欄位註冊
    if "username" not in data and "account" in data:
        data["username"] = data["account"]

    # 處理前端傳來的 school_class (可以是 ID 或班級名稱)
    raw_class = data.get("school_class")
    if raw_class:
        if isinstance(raw_class, int) or (isinstance(raw_class, str) and raw_class.isdigit()):
            school_class_obj = SchoolClass.objects.filter(id=int(raw_class)).first()
        else:
            school_class_obj = SchoolClass.objects.filter(name=raw_class).first()
        data["school_class"] = school_class_obj.id if school_class_obj else None

    form = RegisterForm(data)
    if not form.is_valid():
        msg = _form_errors(form)
        if is_json:
            return JsonResponse({"錯誤訊息": msg}, status=400)
        return render(request, "login.html", {"error": msg, "school_classes": SchoolClass.objects.all()})

    # 建立帳號與 UserProfile，但不執行 login()，保持未登入狀態
    user = form.save()

    # 回傳 JSON 提示，指示重導向至登入頁面
    if is_json:
        return JsonResponse({
            "message": "註冊成功！請使用新帳號進行登入。",
            "redirect_url": "/login/"
        }, status=200)
    return redirect("/login/")


"""
登入帳號
支援 GET (顯示 login.html 頁面) 與 POST (處理登入認證)
"""
@csrf_exempt
def login_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/timetable/")
        school_classes = SchoolClass.objects.all()
        return render(request, "login.html", {"school_classes": school_classes})
    
    if request.method != "POST":
        return JsonResponse({"錯誤訊息": "不支援的請求方法"}, status=405)

    is_json = request.content_type == "application/json" or not request.POST
    if is_json:
        data = _parse_json(request)
        if data is None:
            return JsonResponse({"錯誤訊息": INVALID_JSON_MSG}, status=400)
    else:
        data = request.POST.dict()

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
        return render(request, "login.html", {"error": msg, "school_classes": SchoolClass.objects.all()})

    if not isinstance(username, str) or not isinstance(password, str):
        msg = "username 與 password 的值必須是字串"
        if is_json:
            return JsonResponse({"錯誤訊息": msg}, status=400)
        return render(request, "login.html", {"error": msg, "school_classes": SchoolClass.objects.all()})

    user = authenticate(request, username=username, password=password)

    if user is None or user.username != username:
        msg = "登入失敗：帳號不存在或密碼錯誤"
        if is_json:
            return JsonResponse({"錯誤訊息": msg}, status=401)
        return render(request, "login.html", {"error": msg, "school_classes": SchoolClass.objects.all()})

    login(request, user)

    # 記住帳號 (remember / rememberAccount)
    remember = data.get("remember") or data.get("rememberAccount")
    if remember and str(remember).lower() not in ("false", "0", "null", "undefined"):
        request.session.set_expiry(1209600)  # 兩週
    else:
        request.session.set_expiry(0)        # 瀏覽器關閉即過期

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