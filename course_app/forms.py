from django.contrib.auth.forms import UserCreationForm

from course_app.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields = ("username","image",)