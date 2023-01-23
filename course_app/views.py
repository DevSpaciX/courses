import datetime
import json

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, F
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from course_app.forms import CustomUserCreationForm, CommentCourseFrom
from course_app.models import Course, Category, Lecture, Comment, Homework, Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(generic.TemplateView):
    template_name = "course/success.html"


class CancelView(generic.TemplateView):
    template_name = "course/cancel.html"


class ListOfCourses(generic.ListView):
    model = Course
    template_name = "course/base.html"

    def get_queryset(self):
        return Course.objects.all().annotate(num_courses=Count('user_course')).order_by('-num_courses')[:10].select_related("categories")


class DetailCourses(LoginRequiredMixin,generic.DetailView):
    queryset = Course.objects.prefetch_related("lecture__video")
    template_name = "course/course_detail.html"


    def get_context_data(self, **kwargs):
        product = Course.objects.get(pk=self.kwargs["pk"])
        lectures = Lecture.objects.filter(course_id=self.kwargs["pk"])
        context = super(DetailCourses, self).get_context_data(**kwargs)
        context.update(
            {
                "lectures": lectures,
                "product": product,
                "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        user = request.user.pk
        product_id = self.kwargs["pk"]
        product = Course.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": product.price,
                        "product_data": {
                            "name": product.title,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    "quantity": 1,
                },
            ],
            metadata={"product_id": product.id, "user_id": user},
            mode="payment",
            success_url=YOUR_DOMAIN ,
            cancel_url=YOUR_DOMAIN + "/cancel/",
        )
        return JsonResponse({"id": checkout_session.id})


class CreateUser(generic.CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = "course/registration/../templates/course/accounts/registration.html"
    success_url = reverse_lazy("course:home-page")

    def form_valid(self, form):
        form.save()
        username = self.request.POST["username"]
        password = self.request.POST["password1"]
        image = self.request.FILES
        # authenticate user then login
        user = authenticate(username=username, password=password, image=image)
        login(self.request, user)
        return HttpResponseRedirect(reverse("course:home-page"))


def login_view(request):
    if request.method == "GET":
        return render(request, "course/registration/../templates/course/accounts/login.html")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("course:home-page"))
        else:
            error_context = {"errors": "invalid data"}
            return render(request, "course/registration/../templates/course/accounts/login.html", context=error_context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("course:home-page"))


class EditProfileView(generic.UpdateView):
    model = get_user_model()
    template_name = "course/profile_update.html"
    fields = ["username", "image"]

    def get_success_url(self):
        user_id = self.kwargs['pk']
        return reverse_lazy('course:profile', kwargs={'pk': user_id})


class Profile(generic.DetailView):
    queryset = get_user_model().objects.all()
    template_name = "course/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs["pk"]
        print(self.kwargs)
        context["number_done_lectures"] = get_user_model().objects.get(pk=pk).listened_lecture.all()
        return context




class CourseByCategory(generic.ListView):
    model = Course
    template_name = "course/base.html"

    def get_queryset(self):
        return Course.objects.filter(categories_id=self.kwargs["pk"]).annotate(
            num_courses=Count('user_course')).order_by('-num_courses')[:10].select_related("categories")


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        product_id = session["metadata"]["product_id"]
        user_id = session["metadata"]["user_id"]
        user = get_user_model().objects.get(pk=user_id)
        user.course_paid.add(Course.objects.get(pk=product_id))
        user.save()

        Payment.objects.create(
            user=get_user_model().objects.get(pk=user_id),
            amount=Course.objects.get(pk=product_id).get_display_price(),
            course=Course.objects.get(pk=product_id)
        )

    return HttpResponse(status=200)


def course_comments(request, pk):
    if request.method == "GET":
        comments = Comment.objects.filter(course_id=pk)
        context = {
            "comments": comments,
        }
        return render(request, "course/comments.html", context=context)
    if request.method == "POST":
        creation_form = CommentCourseFrom(request.POST or None)
        if creation_form.is_valid():
            sender = request.user
            content = request.POST.get("content")
            created_at = datetime.datetime.now()
            Comment.objects.create(
                sender=sender,
                content=content,
                created_at=created_at,
                course_id=pk,
            )
            return HttpResponseRedirect(reverse("course:home-page"))
        else:
            return render(request, "course/base.html")


def mark_as_done_homework(request, pk_course,pk):
    lecture = Lecture.objects.get(pk=pk)
    user = get_user_model().objects.get(pk=request.user.pk)
    if request.method == "POST":
        if lecture not in user.listened_lecture.all():
            user.listened_lecture.add(lecture.pk)
            Homework.objects.create(
                student = user,
                homework=lecture.home_work,
                course = Course.objects.get(pk=pk_course)
            )

        else:
            user.listened_lecture.remove(lecture.pk)
            Homework.objects.filter(
                student = user,
                homework=lecture.home_work,
                course = Course.objects.get(pk=pk_course)
            ).delete()

        user.save()
        return HttpResponseRedirect(reverse_lazy("course:detail-page", args=[pk_course]))

