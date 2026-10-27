from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        error_messages={"required": "請輸入帳號"},
    )
    password = forms.CharField(
        min_length=8,
        strip=False,
        error_messages={
            "required": "請輸入密碼",
            "min_length": "密碼至少需要 8 個字元",
        },
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("此帳號已被使用")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
        )