document.addEventListener("DOMContentLoaded", async function () {
    // =======================================================
    // 1. 登入狀態驗證（雙重檢查：後端 Session + 前端 localStorage）
    // =======================================================
    let savedAccount = localStorage.getItem("loggedInAccount");
    let savedStudentID = localStorage.getItem("loggedInStudentID");
    let savedClass = localStorage.getItem("loggedInClass");

    // 向後端確認真正的登入狀態 (避免 localStorage 遺失但 Session 還在的問題)
    try {
        const response = await fetch("/login/me/", { credentials: "same-origin" });
        if (response.ok) {
            const user = await response.json();
            // 後端確認已登入，同步更新前端暫存
            savedAccount = user.account || user.username;
            savedStudentID = user.student_id || user.username;
            savedClass = user.class_name || "";

            localStorage.setItem("loggedInAccount", savedAccount);
            localStorage.setItem("loggedInStudentID", savedStudentID);
            localStorage.setItem("loggedInClass", savedClass);
        } else {
            // 後端也判定未登入，才踢回登入頁
            alert("請先登入系統！");
            window.location.href = "/login/";
            return;
        }
    } catch (err) {
        console.error("無法驗證登入狀態：", err);
        // 如果連 localStorage 都沒有且網路請求失敗，才退回登入頁
        if (!savedAccount) {
            alert("請先登入系統！");
            window.location.href = "/login/";
            return;
        }
    }

    // =======================================================
    // 2. 動態將使用者資料寫入右上角卡片與歡迎詞
    // =======================================================
    const userAccountElem = document.getElementById("user-account");
    const userStudentIdElem = document.getElementById("user-student-id");
    const userClassElem = document.getElementById("user-class");
    const toastMessageElem = document.getElementById("toast-message");
    const toastOverlay = document.querySelector(".toast-overlay");
    const urlParams = new URLSearchParams(window.location.search);

    if (userAccountElem) userAccountElem.textContent = savedAccount;
    if (userStudentIdElem) userStudentIdElem.textContent = savedStudentID;
    if (userClassElem) userClassElem.textContent = savedClass;

    // 判斷網址列是否帶有查詢參數：若為點擊查詢，隱藏歡迎遮罩；否則顯示歡迎詞
    if (urlParams.get("year") || urlParams.get("class_name")) {
        if (toastOverlay) {
            toastOverlay.style.display = "none";
        }
    } else if (toastMessageElem) {
        toastMessageElem.textContent = `歡迎 ${savedAccount} 登入成功！`;
    }

    // =======================================================
    // 3. 渲染課表資料 (讀取後端傳來的 rows_json)
    // =======================================================
    const timetableBody = document.getElementById("timetableBody");
    if (timetableBody) {
        try {
            const rowsData = JSON.parse('{{ rows_json|safe }}');
            const trElements = timetableBody.querySelectorAll("tr");

            rowsData.forEach((row, periodIndex) => {
                const tr = trElements[periodIndex];
                if (tr) {
                    const tds = tr.querySelectorAll("td");
                    row.cells.forEach((cell, dayIndex) => {
                        const targetTd = tds[dayIndex + 1];
                        if (targetTd && cell.course_name) {
                            targetTd.innerHTML = `
                                <div class="course-box" style="text-align: center; padding: 5px; background: #eef2f7; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                    <div class="course-name" style="font-weight: bold; color: #2c3e50; font-size: 0.95em; margin-bottom: 2px;">${cell.course_name}</div>
                                    <div class="course-teacher" style="font-size: 0.85em; color: #7f8c8d;">${cell.teacher}老師</div>
                                    <div class="course-room" style="font-size: 0.85em; color: #95a5a6; margin-top: 2px;">${cell.classroom}</div>
                                </div>
                            `;
                        }
                    });
                }
            });
        } catch (e) {
            console.log("初始化或未帶查詢參數，暫不渲染課表資料。");
        }
    }

    // =======================================================
    // 4. 綁定按鈕事件 (查詢與登出)
    // =======================================================
    const searchBtn = document.getElementById("searchBtn");
    if (searchBtn) {
        searchBtn.addEventListener("click", function () {
            const year = document.getElementById("yearSelect").value;
            const semester = document.getElementById("semesterSelect").value;
            const class_name = document.getElementById("classSelect").value;

            window.location.href = `${window.location.origin}${window.location.pathname}?year=${year}&semester=${semester}&class_name=${class_name}`;
        });
    }

    const logoutBtn = document.getElementById("logoutBtn");
    const logoutForm = document.getElementById("logoutForm");
    if (logoutBtn && logoutForm) {
        logoutBtn.addEventListener("click", function () {
            localStorage.removeItem("loggedInAccount");
            localStorage.removeItem("loggedInStudentID");
            localStorage.removeItem("loggedInClass");
            logoutForm.submit();
        });
    }
});