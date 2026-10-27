import json

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import TestCase


def post(client, path, payload):
    return client.post(path, json.dumps(payload), content_type="application/json")


class AuthTests(TestCase):
    REGISTER = "/register/"
    LOGIN = "/login/"
    API_LOGIN = "/api/login/"

    def register(self, password="Str0ng!Pass123", username="Alice"):
        return post(self.client, self.REGISTER,
                    {"username": username, "password": password})

    def test_password_is_stored_hashed(self):
        raw = "Str0ng!Pass123"
        self.assertEqual(self.register(raw).status_code, 201)
        user = User.objects.get(username="Alice")
        self.assertNotEqual(user.password, raw)
        self.assertNotIn(raw, user.password)
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(check_password(raw, user.password))

    def test_password_shorter_than_8_is_rejected(self):
        res = self.register(password="Ab1!xyz")  # 7 個字元
        self.assertEqual(res.status_code, 400)
        self.assertFalse(User.objects.exists())

    def test_password_with_8_chars_is_accepted(self):
        res = self.register(password="Ab1!xyz9")  # 剛好 8 個字元
        self.assertEqual(res.status_code, 201)

    def test_duplicate_username_ignoring_case_is_rejected(self):
        self.register(username="Alice")
        res = self.register(username="alice")
        self.assertEqual(res.status_code, 400)

    def test_login_requires_exact_case(self):
        self.register()
        self.client.logout()
        wrong = post(self.client, self.LOGIN,
                     {"username": "alice", "password": "Str0ng!Pass123"})
        self.assertEqual(wrong.status_code, 401)
        right = post(self.client, self.LOGIN,
                     {"username": "Alice", "password": "Str0ng!Pass123"})
        self.assertEqual(right.status_code, 200)

    def test_login_password_is_case_sensitive(self):
        self.register()
        self.client.logout()
        res = post(self.client, self.LOGIN,
                   {"username": "Alice", "password": "str0ng!pass123"})
        self.assertEqual(res.status_code, 401)

    def test_login_page_renders_html_on_get(self):
        res = self.client.get(self.LOGIN)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "login.html")
        self.assertContains(res, "北商校園系統登入")

    def test_api_login_with_account_field_success(self):
        self.register(username="11356042")
        self.client.logout()
        res = post(self.client, self.API_LOGIN,
                   {"account": "11356042", "password": "Str0ng!Pass123", "remember": True})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["message"], "登入成功")
        self.assertEqual(data["user"]["account"], "11356042")
        self.assertEqual(data["redirect_url"], "/timetable/")

    def test_timetable_requires_login_and_redirects_to_login(self):
        res = self.client.get("/timetable/")
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.url.startswith("/login/"))

    def test_timetable_accessible_after_login(self):
        self.register(username="11356042")
        post(self.client, self.API_LOGIN,
             {"account": "11356042", "password": "Str0ng!Pass123"})
        res = self.client.get("/timetable/")
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "timetable.html")
