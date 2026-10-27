# personal_schedule (個人課程查詢系統)

本專案是一個專為個人量身打造的課程查詢與管理系統。

## 功能

- 使用者註冊、登入、登出
- 登入後可對個人資料進行新增、查看、修改、刪除
- 每位使用者只能存取自己的資料

## 技術

- Python 3.14.7
- Django 6.1.2
- SQLite3

## 測試帳號

系統提供以下測試帳號供登入使用：

| 帳號類型 | 帳號（Account / Username） | 密碼（Password） | 說明 |
| :--- | :--- | :--- | :--- |
| **學生測試帳號** | `11356088` | `TestPass123` | 推薦使用，符合英數大小寫規則 |
| **單元測試帳號** | `alice` | `Str0ng!Pass123` | 包含特殊符號，測試通過 |

> **密碼格式規則**：密碼長度需為 8～50 碼，且必須包含至少一個大寫英文字母、一個小寫英文字母與一個數字。

> [!TIP]
> **若重新 Clone 專案後資料庫尚未包含測試帳號**，請在專案目錄執行下列指令一鍵建立：
> ```bash
> python manage.py init_test_users
> ```

## 本地啟動方式

1. 啟動 Django 開發伺服器：
   ```bash
   python manage.py runserver
   ```
2. 開啟瀏覽器訪問：
   - 登入頁面：[http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
   - 個人課表頁面：[http://127.0.0.1:8000/timetable/](http://127.0.0.1:8000/timetable/)（未登入會自動重導向至登入頁面）

## 專案結構

```Shell
config/      專案設定與總路由
login/       登入、註冊與帳號驗證
homepage/    主頁面與課表呈現
templates/   HTML 模板
static/      CSS、JS 與靜態圖片資源
```
