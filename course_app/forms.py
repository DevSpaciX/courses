from django import forms
from django.contrib.auth.forms import UserCreationForm

from course_app.models import User, Comment


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields = (
            "username",
            "image",
        )


class CommentCourseFrom(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
