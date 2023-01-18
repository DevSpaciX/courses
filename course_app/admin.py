from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from embed_video.admin import AdminVideoMixin
from .models import LectureVideo,Lecture,Category,User,Comment,Course


class MyModelAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass



admin.site.register(Course)
admin.site.register(Comment)
admin.site.register(User,UserAdmin)
admin.site.register(Category)
admin.site.register(Lecture)
admin.site.register(LectureVideo, MyModelAdmin)

