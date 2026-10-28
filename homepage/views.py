
import random

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


# 可選擇的學年、學期、年級
YEARS = ["113", "114", "115"]
SEMESTERS = ["1", "2"]
CLASSES = ["資管一", "資管二", "資管三", "資管四", "資管五"]


# 模擬資管系課程資料
COURSES = [
    ("國文", "王老師", "A301"),
    ("英文", "陳老師", "A302"),
    ("體育", "林老師", "操場"),
    ("管理學", "張老師", "B201"),
    ("計算機概論", "李老師", "B202"),
    ("程式設計", "黃老師", "C101"),
    ("Python 程式設計", "林老師", "C102"),
    ("Java 程式設計", "陳老師", "C103"),
    ("資料庫管理", "王老師", "C201"),
    ("網頁設計", "張老師", "C202"),
    ("資訊網路", "李老師", "B301"),
    ("電子商務", "黃老師", "B302"),
    ("統計學", "吳老師", "A401"),
    ("會計學", "周老師", "A402"),
    ("經濟學", "林老師", "A403"),
    ("管理數學", "陳老師", "A405"),
    ("物件導向程式設計", "王老師", "C301"),
    ("資料結構", "李老師", "C302"),
    ("作業系統", "張老師", "C303"),
    ("系統分析與設計", "黃老師", "C401"),
    ("軟體工程", "吳老師", "C402"),
    ("資訊安全", "周老師", "B401"),
    ("企業資源規劃", "林老師", "B402"),
    ("行銷管理", "陳老師", "A501"),
    ("專案管理", "王老師", "A502"),
    ("大數據分析", "李老師", "C501"),
    ("人工智慧概論", "張老師", "C502"),
    ("雲端運算", "黃老師", "C503"),
    ("資訊管理導論", "吳老師", "B501"),
    ("畢業專題", "周老師", "專題教室"),
]


# 每一節課的時間
PERIOD_TIMES = {
    1: "08:10～09:00",
    2: "09:10～10:00",
    3: "10:10～11:00",
    4: "11:10～12:00",
    5: "13:30～14:20",
    6: "14:25～15:15",
    7: "15:25～16:15",
    8: "16:20～17:10",
    9: "17:15～18:05",
    10: "",
    11: "18:30～19:15",
    12: "19:20～20:05",
}


# 建立所有組合的模擬課表
# 使用固定亂數種子，讓課表每次啟動都保持一致
SCHEDULE_DATA = {}
rng = random.Random(42)

for year in YEARS:
    for semester in SEMESTERS:
        for class_name in CLASSES:
            schedule = {}

            # 星期一至星期五，每天第 1～8 節
            available_slots = [
                (day, period)
                for day in range(1, 6)
                for period in range(1, 9)
            ]

            # 每份課表安排 20 堂課
            selected_courses = rng.sample(COURSES, 20)
            selected_slots = rng.sample(available_slots, 20)

            for slot, course in zip(selected_slots, selected_courses):
                schedule[slot] = course

            SCHEDULE_DATA[(year, semester, class_name)] = schedule


@login_required
def schedule(request):
    # 讀取使用者選擇的條件
    year = request.GET.get("year", "115")
    semester = request.GET.get("semester", "1")
    class_name = request.GET.get("class_name", "資管一")

    # 避免輸入不存在的選項
    if year not in YEARS:
        year = "115"

    if semester not in SEMESTERS:
        semester = "1"

    if class_name not in CLASSES:
        class_name = "資管一"

    # 取得對應的課表
    course_data = SCHEDULE_DATA.get(
        (year, semester, class_name), {}
    )

    weekdays = [
        (1, "星期一"),
        (2, "星期二"),
        (3, "星期三"),
        (4, "星期四"),
        (5, "星期五"),
    ]

    # 整理成 HTML 可以使用的資料
    rows = []

    for period in range(1, 13):
        cells = []

        for weekday in range(1, 6):
            course = course_data.get((weekday, period))

            if course:
                course_name, teacher, classroom = course
            else:
                course_name = ""
                teacher = ""
                classroom = ""

            cells.append({
                "course_name": course_name,
                "teacher": teacher,
                "classroom": classroom,
            })

        rows.append({
            "period": period,
            "time": PERIOD_TIMES[period],
            "cells": cells,
        })

    context = {
        "year": year,
        "semester": semester,
        "class_name": class_name,
        "years": YEARS,
        "semesters": SEMESTERS,
        "classes": CLASSES,
        "weekdays": weekdays,
        "rows": rows,
        "username": request.user.username,
    }

    return render(
        request,
        "timetable.html",
        context
    )


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("/login/")

    return redirect("timetable:schedule")