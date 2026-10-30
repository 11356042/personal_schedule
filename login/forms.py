from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import SchoolClass, UserProfile

ROLE_CHOICES = (
    ('student', '學生'),
    ('teacher', '老師'),
)

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        error_messages={"required": "請輸入帳號"},
    )
    real_name = forms.CharField(
        max_length=50,
        error_messages={"required": "請輸入姓名"}
    )
    student_id = forms.CharField(
        max_length=20,
        required=False
    )
    password = forms.CharField(
        min_length=8,
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            "required": "請輸入密碼",
            "min_length": "密碼至少需要 8 個字元",
        },
    )
    password_confirm = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
        error_messages={"required": "請再次輸入密碼"},
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='student',
        error_messages={"required": "請選擇身份"}
    )
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(),
        required=False,
        empty_label="請選擇班級",
        error_messages={"invalid_choice": "請選擇有效的班級"}
    )

    # 💥 關鍵修正：單獨檢查帳號是否已存在（不分大小寫）
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("此帳號已被註冊，請換一個帳號")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
        # 至少包含一個大寫英文字母
            if not any(c.isupper() for c in password):
                raise forms.ValidationError("密碼必須包含至少一個大寫英文字母")

        # 至少包含一個小寫英文字母
            if not any(c.islower() for c in password):
                raise forms.ValidationError("密碼必須包含至少一個小寫英文字母")

        # 至少包含一個數字
            if not any(c.isdigit() for c in password):
                raise forms.ValidationError("密碼必須包含至少一個數字")

        # 執行 Django 原本的密碼強度驗證
        validate_password(password)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        role = cleaned_data.get("role")
        student_id = cleaned_data.get("student_id")
        school_class = cleaned_data.get("school_class")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "兩次輸入的密碼不一致")

        # 學生身份時的特定欄位檢驗
        if role == 'student':
            if not student_id:
                self.add_error('student_id', "學生身份必須輸入學號")
            if not school_class:
                self.add_error('school_class', "學生身份必須選擇班級")

        return cleaned_data

    def save(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]
        role = self.cleaned_data["role"]

        # 建立 User 物件
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        
        # 建立 UserProfile
        UserProfile.objects.create(
            user=user,
            role=role,
            real_name=self.cleaned_data.get("real_name"),
            student_id=self.cleaned_data.get("student_id") if role == 'student' else None,
            school_class=self.cleaned_data.get("school_class") if role == 'student' else None
        )
        return user