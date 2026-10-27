const form = document.getElementById("loginForm");

// 記住帳號功能：頁面載入時若有記住的帳號則自動帶入
document.addEventListener("DOMContentLoaded", function() {
    const savedAccount = localStorage.getItem("savedLoginAccount");
    const accountInput = document.getElementById("account");
    const rememberCheckbox = document.getElementById("rememberAccount");

    if (savedAccount && accountInput) {
        accountInput.value = savedAccount;
        if (rememberCheckbox) {
            rememberCheckbox.checked = true;
        }
    }
});

if (form) {
    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const accountInput = document.getElementById("account");
        const passwordInput = document.getElementById("password");
        const rememberCheckbox = document.getElementById("rememberAccount");

        const account = accountInput ? accountInput.value.trim() : "";
        const password = passwordInput ? passwordInput.value : "";
        const remember = rememberCheckbox ? rememberCheckbox.checked : false;

        if (!account || !password) {
            alert("請輸入帳號和密碼！");
            return;
        }

        // 必須有大寫、小寫英文字母及數字，長度 8 碼以上
        const passwordRule = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[\S]{8,50}$/;

        if (!passwordRule.test(password)) {
            alert("密碼必須包含大寫、小寫英文字母及數字，長度需要 8 碼以上！");
            return;
        }

        try {
            // 將帳號與密碼傳送至 Django 後端 (支援 /api/login/ 及 /login/)
            const response = await fetch("/api/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: account,
                    account: account,
                    password: password,
                    remember: remember
                }),
                credentials: "same-origin"
            });

            const data = await response.json();

            if (!response.ok) {
                const message =
                    data["錯誤訊息"] || data.message || "登入失敗！";

                alert(
                    typeof message === "string"
                        ? message
                        : JSON.stringify(message)
                );
                return;
            }

            // 處理「記住帳號」狀態儲存
            if (remember) {
                localStorage.setItem("savedLoginAccount", account);
            } else {
                localStorage.removeItem("savedLoginAccount");
            }

            // 格式正確，將輸入的帳號與學號/班級存進瀏覽器暫存空間
            const studentID = (data.user && data.user.student_id) ? data.user.student_id : account;
            const className = (data.user && data.user.class_name) ? data.user.class_name : "資管一甲";

            localStorage.setItem("loggedInAccount", account);
            localStorage.setItem("loggedInStudentID", studentID); 
            localStorage.setItem("loggedInClass", className); 

            // 後端確認登入成功後，跳轉至課表頁面
            window.location.href = data.redirect_url || "/timetable/";

        } catch (error) {
            console.error("登入錯誤：", error);
            alert("無法連接伺服器，請確認後端是否正常運作！");
        }
    });
}
