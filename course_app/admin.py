from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from embed_video.admin import AdminVideoMixin
from .models import LectureVideo, Lecture, Category, User, Comment, Course, Homework, Payment


class MyModelAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass


admin.site.register(Course)
admin.site.register(Comment)


@admin.register(User)
class SuperUser(UserAdmin):
    list_display = UserAdmin.list_display + ("get_course",)

    def get_course(self, obj):
        return [course_paid.title for course_paid in obj.course_paid.all()]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "image",
                    "course_paid",
                    "listened_lecture",
                    "rework_lecture",
                )
            },
        ),
    )


admin.site.register(Payment)
admin.site.register(Homework)
admin.site.register(Category)
admin.site.register(Lecture)
admin.site.register(LectureVideo, MyModelAdmin)
