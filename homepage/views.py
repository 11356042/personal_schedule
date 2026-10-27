from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


# 固定課表資料
# 格式：(星期, 節次): (課程名稱, 教師, 教室)
COURSE_DATA = {
    (1, 1): ("Python 程式設計", "王老師", "A301"),
    (2, 1): ("資料庫管理", "陳老師", "A302"),
    (3, 2): ("網路概論", "林老師", "B201"),
    (4, 3): ("英文", "張老師", "C101"),
    (5, 4): ("數學", "李老師", "A201"),
}


@login_required
def schedule(request):
    weekdays = [
        "星期一",
        "星期二",
        "星期三",
        "星期四",
        "星期五",
    ]

    # 建立 12 節課，每節都有星期一至星期五的格子
    rows = []

    for period in range(1, 13):
        cells = []

        for weekday in range(1, 6):
            course = COURSE_DATA.get((weekday, period))

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
            "cells": cells,
        })

    return render(
        request,
        "timetable.html",
        {
            "weekdays": weekdays,
            "rows": rows,
            "class_name": "資管一甲",
            "year": "115",
            "semester": "1",
        }
    )


def logout_view(request):
    logout(request)
    return redirect("login:login")
