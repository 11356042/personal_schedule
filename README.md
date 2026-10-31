# personal_schedule（個人課程查詢系統）

本專案是一個專為個人量身打造的課程查詢與管理系統，使用者註冊登入後，可以管理並查詢自己的課表。

## 功能

- 使用者註冊、登入、登出
- 查詢課表頁面（未登入會自動重導向至登入頁面）

## 技術

| 項目    | 版本   | 用途                              |
| ------- | ------ | --------------------------------- |
| Python  | 3.14.7 | 程式語言                          |
| Django  | 6.1.2  | 網站框架                          |
| SQLite3 | 內建   | 資料庫（本機檔案 `db.sqlite3`） |

## 測試帳號

以下為測試用假帳號，僅供本機開發與展示使用：

| 帳號類型     | 帳號（Username） | 密碼（Password）   | 說明                         |
| ------------ | ---------------- | ------------------ | ---------------------------- |
| 學生測試帳號 | `11356088`     | `TestPass123`    | 推薦使用，符合英數大小寫規則 |
| 老師測試帳號 | `alice`        | `Str0ng!Pass123` | 包含特殊符號，測試通過       |

> **密碼格式規則**：長度需為 8～50 碼，且必須包含至少一個大寫英文字母、一個小寫英文字母與一個數字。

## 本地啟動方式（Windows）

### 事前準備

- 安裝 [Git](https://git-scm.com/download/win)
- 安裝 [Python 3.14.7](https://www.python.org/downloads/windows/)，安裝時請勾選 **Add python.exe to PATH**
- 開啟 PowerShell 或 VS Code 的整合終端機，確認版本：

```powershell
git --version
python --version
```

> 所有指令都請在專案根目錄執行（看得到 `manage.py` 的那一層）。可用 `Get-ChildItem` 確認。

### 1. 取得專案

```powershell
git clone https://github.com/你的帳號/personal_schedule.git
cd personal_schedule
```

### 2. 建立虛擬環境並安裝依賴套件

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

啟用成功後，命令列前面會出現 `(.venv)`。離開虛擬環境請輸入 `deactivate`。

> 每次重新開啟終端機，都要再執行一次 `.venv\Scripts\activate`。

### 3. 資料庫初始化與建立測試資料

`db.sqlite3` 不會被提交到 Git，所以每次重新 Clone 都需要執行：

```powershell
python manage.py check
python manage.py migrate

# 建立測試帳號與課程資料（兩個獨立指令，請依序執行）
python manage.py init_test_users
python manage.py init_school_classes
```

### 4. 啟動開發伺服器

```powershell
python manage.py runserver
```

看到 `Starting development server at http://127.0.0.1:8000/` 即成功。終端機會被伺服器佔住，這是正常的；按 `Ctrl+C` 停止。若 8000 埠被占用，可改用 `python manage.py runserver 8080`。

### 5. 開啟瀏覽器

| 頁面         | 網址                             | 說明                         |
| ------------ | -------------------------------- | ---------------------------- |
| 登入頁面     | http://127.0.0.1:8000/login/     | 登入與註冊入口               |
| 個人課表頁面 | http://127.0.0.1:8000/timetable/ | 未登入會自動重導向至登入頁面 |

登入成功後會自動前往個人課表頁面，登出後回到登入頁面。

## 注意事項

本專案的設定（`DEBUG = True`、固定的 `SECRET_KEY`）僅適用於本機開發與課堂展示。若要公開部署，需要另外處理金鑰保密、`DEBUG`、`ALLOWED_HOSTS`、HTTPS 與資料庫備份。

## 常見問題

| 問題                                                      | 解法                                                                                                   |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `python` 不是內部或外部命令                             | Python 安裝時沒勾選 PATH，請重新安裝並勾選 **Add python.exe to PATH**，或改用 `py` 指令        |
| 無法啟用 `.venv`（PowerShell 顯示「已停用指令碼執行」） | 執行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`，或改用 CMD 啟用                          |
| `ModuleNotFoundError`                                   | 確認已啟用 `.venv`（命令列前有 `(.venv)`），並已執行 `python -m pip install -r requirements.txt` |
| 找不到 `manage.py`                                      | 目前資料夾不對，用 `Get-Location` 確認位置，再 `cd` 進專案資料夾                                   |
| 登入失敗                                                  | 確認已執行 `init_test_users`，且密碼符合格式規則                                                     |
| 登入後沒有課程資料                                        | 重新執行 `init_school_classes`                                                                       |
| 8000 埠被占用                                             | 改用 `runserver 8080`                                                                                |

## 專案結構

```text
personal_schedule/
├── manage.py          Django 指令入口
├── config/            專案設定與總路由
├── login/             登入、註冊與帳號驗證
├── homepage/          主頁面與課表呈現
├── templates/         HTML 模板
├── static/            CSS、JS 與靜態圖片資源
├── requirements.txt   依賴套件清單
└── .gitignore         Git 忽略規則
```

## Git 協作規範

- 一次 commit 只完成一個小目的，訊息格式：`feat:` 新功能、`fix:` 修正、`docs:` 文件
- 開工前先 `git pull --ff-only`；不要使用 `git push --force`
- 禁止提交：`db.sqlite3`、`.venv/`、密碼、API key、個資
