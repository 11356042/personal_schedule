from django.core.management.base import BaseCommand
from login.models import SchoolClass


class Command(BaseCommand):
    help = "初始化預設班級資料"

    def handle(self, *args, **options):
        default_classes = [
            "資管一甲",
            "資管二甲",
            "資管三甲",
            "資管四甲",
            "資管五甲",
        ]

        created_count = 0
        for class_name in default_classes:
            obj, created = SchoolClass.objects.get_or_create(name=class_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"成功建立班級：{class_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"班級已存在，略過：{class_name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"完成！共新增 {created_count} 個班級。")
        )