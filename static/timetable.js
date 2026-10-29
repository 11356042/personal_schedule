document.addEventListener("DOMContentLoaded", function() {
    // =======================================================
    // 1. 最高優先權：精準阻擋「按下查詢重整網頁時」重複跳出的歡迎遮罩
    // =======================================================
    const toastOverlay = document.querySelector(".toast-overlay");
    const urlParams = new URLSearchParams(window.location.search);
    
    // 如果網址列帶有 year 或 class_name 參數，代表這是按查詢進來的，立刻把遮罩藏起來
    if (urlParams.get("year") || urlParams.get("class_name")) {
        if (toastOverlay) {
            toastOverlay.style.display = "none";
        }
    }

    // =======================================================
    // 2. 核心數據串聯：讀取後端轉好的 json 變數，用純 JS 把課表寫入空白格子中
    // =======================================================
    const timetableBody = document.getElementById("timetableBody");

    if (timetableBody) {
        try {
            // 🌟 關鍵串聯點：利用 Django 標籤，在 JS 中直接解鎖後端傳過來的 JSON 課表陣列
            // 它會讀取你在 views.py 最下方寫好的 context["rows_json"] 變數
            const rowsData = JSON.parse('{{ rows_json|safe }}');
            
            // 抓取你 HTML 網頁上目前寫死的 12 節 <tr> 元素
            const trElements = timetableBody.querySelectorAll("tr");

            // 開始遍歷後端過來的 12 節課 rows 資料
            rowsData.forEach((row, periodIndex) => {
                const tr = trElements[periodIndex];
                if (tr) {
                    const tds = tr.querySelectorAll("td"); // tds[0]是節次，tds[1]~tds[5]是星期一到五

                    // 遍歷這一節課內 星期一到星期五 的 cells 資料 (共 5 格)
                    row.cells.forEach((cell, dayIndex) => {
                        const targetTd = tds[dayIndex + 1]; // 對應到 HTML 表格中的星期格
                        
                        if (targetTd && cell.course_name) {
                            // 將後端 views.py 算好的真實隨機課表文字與樣式，用 JS 強行填入原本寫死的空白格子中！
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
    // 3. 查詢按鈕點擊事件：直接觸發網頁重導向，向後端發送篩選條件
    // =======================================================
    const searchBtn = document.getElementById("searchBtn");

    if (searchBtn) {
        searchBtn.addEventListener("click", function() {
            const year = document.getElementById("yearSelect").value;
            const semester = document.getElementById("semesterSelect").value;
            const class_name = document.getElementById("classSelect").value;

            // 讓網頁帶著參數重新整理，觸發你的後端 views.py 重新抓取對應班級的 SCHEDULE_DATA
            window.location.href = `${window.location.origin}${window.location.pathname}?year=${year}&semester=${semester}&class_name=${class_name}`;
        });
    }
});
