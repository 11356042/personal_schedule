document.addEventListener("DOMContentLoaded", async function () {
    // =======================================================
    // 1. 登入狀態驗證（雙重檢查：後端 Session + 前端 localStorage）
    // =======================================================
    let savedAccount = localStorage.getItem("loggedInAccount");
    let savedStudentID = localStorage.getItem("loggedInStudentID");
    let savedClass = localStorage.getItem("loggedInClass");
    let userData = null;
    // 向後端確認真正的登入狀態 (避免 localStorage 遺失但 Session 還在的問題)
    try {
        const response = await fetch("/me/", { credentials: "same-origin" });
        if (response.ok) {
            userData = await response.json();
            console.log("登入資料：", userData);
            console.log("使用者角色：", userData.role);
            console.log("使用者姓名：", userData.real_name);

            // 後端確認已登入，同步更新前端暫存
            savedAccount = userData.account || userData.username || "";
            savedStudentID = userData.student_id || "";
            savedClass = userData.class_name || "";

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
        alert("登入狀態驗證失敗，請重新登入！");
        window.location.href = "/login/";
        return;
    }

    // =======================================================
    // 2. 動態將使用者資料寫入右上角卡片與歡迎詞
    // =======================================================
    const userAccountElem = document.getElementById("user-account");
    const userStudentIdElem = document.getElementById("user-student-id");
    const userClassElem = document.getElementById("user-class");
    const userRealNameElem = document.getElementById("user-real-name");

    const studentIdRow = document.getElementById("student-id-row");
    const classRow = document.getElementById("class-row");
    const realNameRow = document.getElementById("real-name-row");

    const toastMessageElem = document.getElementById("toast-message");
    const toastOverlay = document.querySelector(".toast-overlay");
    const urlParams = new URLSearchParams(window.location.search);

    const classSelect = document.getElementById("classSelect");

    // 顯示帳號
    if (userAccountElem) {
        userAccountElem.textContent = savedAccount;
    }

    // 依照使用者身份顯示基本資料
    if (userData.role === "teacher") {

        // 老師：顯示帳號、姓名
        if (studentIdRow) studentIdRow.style.display = "none";
        if (classRow) classRow.style.display = "none";

        if (realNameRow) realNameRow.style.display = "block";

        if (userRealNameElem) {
            userRealNameElem.textContent = userData.real_name || "";
        }

    } else if (userData.role === "student"){

        // 學生：顯示帳號、學號、班級
        if (studentIdRow) studentIdRow.style.display = "block";
        if (classRow) classRow.style.display = "block";

        if (realNameRow) realNameRow.style.display = "none";

        if (userStudentIdElem) {
            userStudentIdElem.textContent = savedStudentID;
        }

        if (userClassElem) {
            userClassElem.textContent = savedClass;
        }

        // 學生登入後自動帶入自己的班級
        if (classSelect && savedClass) {
            classSelect.value = savedClass;
        }
        // 學生第一次進入課表頁面，自動查詢課表
        if (!urlParams.get("year") ||
        !urlParams.get("semester") ||
        !urlParams.get("class_name")){
            if (!savedClass) {
                alert("目前帳號尚未設定班級，請聯絡管理人員！");
                return;
            }
            const currentYear = new Date().getFullYear() - 1911;
            const params = new URLSearchParams({
                year: currentYear.toString(),
                semester: "1",
                class_name: savedClass
            });
            window.location.replace(
                `${window.location.pathname}?${params.toString()}`
            );
            return;
        }
    }
    // 判斷網址列是否帶有查詢參數：若為點擊查詢，隱藏歡迎遮罩；否則顯示歡迎詞
    if (urlParams.get("year") || urlParams.get("class_name")) {
        if (toastOverlay) {
            toastOverlay.style.display = "none";
        }
    } else if (toastMessageElem) {
        toastMessageElem.textContent = `歡迎 ${savedAccount} 登入成功！`;
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

                // 檢查是否有選擇班級
            if (!class_name) {
                alert("請先選擇班級！");
                return;
            }
            window.location.href =
                `${window.location.origin}${window.location.pathname}?year=${year}&semester=${semester}&class_name=${encodeURIComponent(class_name)}`;
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