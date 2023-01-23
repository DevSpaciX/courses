from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from course_app.views import (
    ListOfCourses,
    CreateUser,
    login_view,
    logout_view,
    Profile,
    EditProfileView,
    CourseByCategory,
    CancelView,
    SuccessView,
    DetailCourses,
    stripe_webhook,
    course_comments, mark_as_done_homework,
)

urlpatterns = [
    path("", ListOfCourses.as_view(), name="home-page"),
    path("register/", CreateUser.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/<int:pk>/", Profile.as_view(), name="profile"),
    path("cancel/", CancelView.as_view(), name="cancel"),
    path("success/", SuccessView.as_view(), name="success"),
    path("profile/edit/<int:pk>/", EditProfileView.as_view(), name="profile-edit"),
    path("category/<int:pk>/", CourseByCategory.as_view(), name="category"),
    path("course/detail/<int:pk>/", DetailCourses.as_view(), name="detail-page"),
    path("webhook/", stripe_webhook),
    path("comments/<int:pk>/", course_comments, name="comments"),
    path("course/detail/<int:pk_course>/mark_as_done/<int:pk>/",mark_as_done_homework,name="mark_as_done")


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "course"
