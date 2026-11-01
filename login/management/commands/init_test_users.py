from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from login.models import UserProfile, SchoolClass


class Command(BaseCommand):
    help = "初始化建立測試帳號 (11356088 與 alice)"

    def handle(self, *args, **options):

        # =================================
        # 1. 建立學生測試帳號
        # =================================
        u1, created1 = User.objects.get_or_create(
            username="11356088"
        )

        u1.set_password("TestPass123")
        u1.save()

        # 建立或取得學生 Profile
        profile1, profile_created1 = UserProfile.objects.get_or_create(
            user=u1,
            defaults={
                "role": "student",
                "real_name": "測試學生",
                "student_id": "11356088",
            }
        )

        # 指定學生班級：資管一甲
        school_class = SchoolClass.objects.get(name="資管三甲")

        profile1.role = "student"
        profile1.student_id = "11356088"
        profile1.school_class = school_class
        profile1.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"[學生設定成功] 11356088 / 班級：{school_class.name}"
            )
        )

        # =================================
        # 2. 建立老師測試帳號
        # =================================
        u2, created2 = User.objects.get_or_create(
            username="alice"
        )

        u2.set_password("Str0ng!Pass123")
        u2.save()

        profile2, profile_created2 = UserProfile.objects.get_or_create(
            user=u2,
            defaults={
                "role": "teacher",
                "real_name": "測試老師",
            }
        )

        profile2.role = "teacher"
        profile2.real_name = profile2.real_name or "測試老師"
        profile2.student_id = None
        profile2.school_class = None
        profile2.save()

        self.stdout.write(
            self.style.SUCCESS(
                "[老師設定成功] alice / 姓名："
                + profile2.real_name
            )
        )