from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "初始化建立測試帳號 (11356088 與 alice)"

    def handle(self, *args, **options):
        # 學生測試帳號 11356088
        u1, created1 = User.objects.get_or_create(username="11356088")
        u1.set_password("TestPass123")
        u1.save()
        action1 = "建立成功" if created1 else "更新密碼成功"
        self.stdout.write(self.style.SUCCESS(f"[{action1}] 帳號: 11356088 / 密碼: TestPass123"))

        # alice 測試帳號
        u2, created2 = User.objects.get_or_create(username="alice")
        u2.set_password("Str0ng!Pass123")
        u2.save()
        action2 = "建立成功" if created2 else "更新密碼成功"
        self.stdout.write(self.style.SUCCESS(f"[{action2}] 帳號: alice / 密碼: Str0ng!Pass123"))

