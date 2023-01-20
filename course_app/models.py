from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


from django.db import models
from embed_video.fields import EmbedVideoField


class User(AbstractUser):
    # paid_course = models.ForeignKey("Course",on_delete=models.PROTECT,blank=True,null=True)
    image = models.ImageField(upload_to='images/', default='hqdefault.jpg')
    course_paid = models.ManyToManyField("Course",blank=True)




class Comment(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    content = models.CharField(max_length=100)


class Category(models.Model):
    title = models.CharField(max_length=15)


class Course(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=500)
    commentary = models.ForeignKey(Comment,on_delete=models.CASCADE,blank=True,null=True)
    categories = models.ForeignKey(Category,on_delete=models.PROTECT)
    price = models.PositiveIntegerField()
    subscribers = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,blank=True,null=True,related_name="course")
    image = models.ImageField(upload_to='images/',default='hqdefault.jpg')

    def __str__(self):
        return self.title

    def get_display_price(self):
        return self.price


class LectureVideo(models.Model):
    video = EmbedVideoField()


class Lecture(models.Model):
    title = models.CharField(max_length=30,null=True)
    text = models.TextField(max_length=200)
    video = models.ForeignKey(LectureVideo,on_delete=models.PROTECT)
    home_work = models.URLField(max_length=100)
    is_done = models.BooleanField(default=False)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="lecture")

    def __str__(self):
        return self.title



