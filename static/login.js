const form = document.getElementById("loginForm");

form.addEventListener("submit",async function(event) {
    event.preventDefault();

    const account = document.getElementById("account").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("請輸入帳號和密碼！");
        return;
    }

        // 必須有大寫、小寫英文字母及數字，長度 8 碼
    const passwordRule = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[A-Za-z0-9]{8,50}$/;

    if (!passwordRule.test(password)) {
        alert("密碼必須包含大寫、小寫英文字母及數字，長度需要 8 碼以上！");
        return;
    }
    try {
        // 將帳號與密碼傳送至 Django 後端
        const response = await fetch("/api/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
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
        // 格式正確，將輸入的帳號與模擬學號存進瀏覽器暫存空間
        localStorage.setItem("loggedInAccount", account);
        localStorage.setItem("loggedInStudentID", account); 
        localStorage.setItem("loggedInClass", "資管一甲"); 

        // 後端確認登入成功後，跳轉至課表頁面
        window.location.href = "/timetable/";

    } catch (error) {
        console.error("登入錯誤：", error);
        alert("無法連接伺服器，請確認後端是否正常運作！");
    }
}); 