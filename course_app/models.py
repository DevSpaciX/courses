from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


from django.db import models
from embed_video.fields import EmbedVideoField


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    amount = models.PositiveIntegerField()
    course = models.ForeignKey("Course",on_delete=models.SET_NULL,null=True)


class Homework(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    homework = models.URLField(null=False)
    course = models.ForeignKey("Course",on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return f"{self.student}`s work ({self.course})"


class User(AbstractUser):
    image = models.ImageField(upload_to="images/", default="hqdefault.jpg")
    course_paid = models.ManyToManyField("Course", blank=True,related_name="user_course")
    listened_lecture = models.ManyToManyField("Lecture",blank=True)
    rework_lecture = models.ManyToManyField("Lecture",blank=True,related_name="user_rework")


class Comment(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    course = models.ForeignKey(
        "Course", blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.content[:10]


class Category(models.Model):
    title = models.CharField(max_length=15)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=500)
    categories = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to="images/", default="hqdefault.jpg")



    def __str__(self):
        return self.title

    def get_display_price(self):
        return self.price


class LectureVideo(models.Model):
    video = EmbedVideoField()


class Lecture(models.Model):
    title = models.CharField(max_length=30, null=True)
    text = models.TextField(max_length=200)
    video = models.ForeignKey(LectureVideo, on_delete=models.PROTECT)
    home_work = models.URLField(max_length=100)
    is_done = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lecture")

    def __str__(self):
        return self.title
