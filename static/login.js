document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // 1. 元素 DOM 宣告
    // ==========================================
    const loginForm = document.getElementById("loginForm");
    const accountInput = document.getElementById("account");
    const passwordInput = document.getElementById("password");
    const rememberCheckbox = document.getElementById("rememberAccount");

    const registerModal = document.getElementById("registerModal");
    const openRegisterModalBtn = document.getElementById("openRegisterModal");
    const closeRegisterModalBtn = document.getElementById("closeRegisterModal");
    const registerForm = document.getElementById("registerForm");
    const registerError = document.getElementById("registerError");

    const regRoleSelect = document.getElementById("reg_role");
    const classGroup = document.getElementById("classGroup");
    const studentIdGroup = document.getElementById("studentIdGroup");

    // ==========================================
    // 2. 頁面載入：自動帶入「記住帳號」
    // ==========================================
    const savedAccount = localStorage.getItem("savedLoginAccount");
    if (savedAccount && accountInput) {
        accountInput.value = savedAccount;
        if (rememberCheckbox) {
            rememberCheckbox.checked = true;
        }
    }

    // ==========================================
    // 3. 註冊 Modal 視窗開關與互動控制
    // ==========================================
    if (openRegisterModalBtn && registerModal) {
        openRegisterModalBtn.addEventListener("click", () => {
            registerModal.style.display = "flex";
        });
    }

    if (closeRegisterModalBtn && registerModal) {
        closeRegisterModalBtn.addEventListener("click", () => {
            registerModal.style.display = "none";
            if (registerError) registerError.style.display = "none";
        });
    }

    // 點擊背景遮罩關閉 Modal
    window.addEventListener("click", (e) => {
        if (e.target === registerModal) {
            registerModal.style.display = "none";
            if (registerError) registerError.style.display = "none";
        }
    });

    // 切換身分：老師隱藏班級與學號，學生顯示
    if (regRoleSelect) {
        regRoleSelect.addEventListener("change", () => {
            const isTeacher = regRoleSelect.value === "teacher";
            if (classGroup) classGroup.style.display = isTeacher ? "none" : "block";
            if (studentIdGroup) studentIdGroup.style.display = isTeacher ? "none" : "block";
        });
    }

    // ==========================================
    // 4. 表單送出：註冊 (AJAX Fetch)
    // ==========================================
    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            if (registerError) registerError.style.display = "none";

            // 取得 CSRF Token
            const csrfTokenInput = this.querySelector("[name=csrfmiddlewaretoken]");
            const csrfToken = csrfTokenInput ? csrfTokenInput.value : "";

            // 收集表單資料
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                if (key !== "csrfmiddlewaretoken") {
                    data[key] = value;
                }
            });

            const registerUrl = this.getAttribute("action") || "/register/";

            try {
                const response = await fetch(registerUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify(data),
                });

                const result = await response.json();

                if (response.ok) {
                    // 1. 跳出成功提示
                    alert(result.message || "註冊成功！請重新登入。");

                    // 2. 將剛註冊的帳號填入登入欄位
                    if (accountInput && (data.username || data.account)) {
                        accountInput.value = data.username || data.account;
                    }

                    // 3. 關閉 Modal 並重置註冊表單
                    if (registerModal) registerModal.style.display = "none";
                    registerForm.reset();

                    // 4. 若不在登入頁，跳轉至登入頁
                    if (result.redirect_url && window.location.pathname !== "/login/") {
                        window.location.href = result.redirect_url;
                    }
                } else {
                    let errorMsg = "";
                    if (result.錯誤訊息) {
                        if (typeof result.錯誤訊息 === "object") {
                            errorMsg = Object.values(result.錯誤訊息).flat().join("<br>");
                        } else {
                            errorMsg = result.錯誤訊息;
                        }
                    } else {
                        errorMsg = "註冊失敗，請重試。";
                    }
                    if (registerError) {
                        registerError.innerHTML = errorMsg;
                        registerError.style.display = "block";
                    }
                }
            } catch (err) {
                console.error("註冊錯誤：", err);
                if (registerError) {
                    registerError.innerText = "網路錯誤，請稍後再試。";
                    registerError.style.display = "block";
                }
            }
        });
    }

    // ==========================================
    // 5. 表單送出：登入 (AJAX Fetch)
    // ==========================================
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const account = accountInput ? accountInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value : "";
            const remember = rememberCheckbox ? rememberCheckbox.checked : false;

            if (!account || !password) {
                alert("請輸入帳號和密碼！");
                return;
            }

            // 密碼規則：大寫、小寫字母與數字，8 碼以上
            const passwordRule = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[\S]{8,50}$/;
            if (!passwordRule.test(password)) {
                alert("密碼必須包含大寫、小寫英文字母及數字，長度需要 8 碼以上！");
                return;
            }

            try {
                const response = await fetch("/api/login/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        username: account,
                        account: account,
                        password: password,
                        remember: remember,
                    }),
                    credentials: "same-origin",
                });

                const data = await response.json();

                if (!response.ok) {
                    const message = data["錯誤訊息"] || data.message || "登入失敗！";
                    alert(typeof message === "string" ? message : JSON.stringify(message));
                    return;
                }

                // 處理「記住帳號」狀態
                if (remember) {
                    localStorage.setItem("savedLoginAccount", account);
                } else {
                    localStorage.removeItem("savedLoginAccount");
                }

                // 儲存登入者資訊至瀏覽器暫存
                const studentID = data.user && data.user.student_id ? data.user.student_id : "";
                const className = data.user && data.user.class_name ? data.user.class_name : "";

                localStorage.setItem("loggedInAccount", account);
                localStorage.setItem("loggedInStudentID", studentID);
                localStorage.setItem("loggedInClass", className);

                // 登入成功後跳轉至課表頁面
                window.location.href = data.redirect_url || "/timetable/";
            } catch (error) {
                console.error("登入錯誤：", error);
                alert("無法連接伺服器，請確認後端是否正常運作！");
            }
        });
    }
});