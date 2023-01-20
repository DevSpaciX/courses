import json

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from course_app.forms import CustomUserCreationForm
from course_app.models import Course, Category, Lecture

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(generic.TemplateView):
    template_name = "course/success.html"


class CancelView(generic.TemplateView):
    template_name = "course/cancel.html"


class ListOfCourses(generic.ListView):
    model = Course
    template_name = "course/base.html"


class DetailCourses(generic.DetailView):
    model = Course
    template_name = "course/course_detail.html"

    def get_context_data(self, **kwargs):
        product = Course.objects.get(pk=self.kwargs["pk"])
        lectures = Lecture.objects.filter(course_id=self.kwargs["pk"])
        context = super(DetailCourses, self).get_context_data(**kwargs)
        context.update({
            "lectures": lectures,
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY

        })
        return context
    def post(self, request, *args, **kwargs):
        user = request.user.pk
        product_id = self.kwargs["pk"]
        product = Course.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.title,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id,
                "user_id": user
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })



class CreateUser(generic.CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = "course/registration.html"
    success_url = reverse_lazy("course:home-page")

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        image = self.request.FILES
        # authenticate user then login
        user = authenticate(username=username, password=password,image=image)
        login(self.request, user)
        return HttpResponseRedirect(reverse("course:home-page"))


def login_view(request):
    if request.method == "GET":
        return render(request,"course/login.html")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username,password=password)

        if user:
            login(request,user)
            return HttpResponseRedirect(reverse("course:home-page"))
        else:
            error_context = {
                "errors":"invalid data"
            }
            return render(request,"course/login.html",context=error_context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("course:home-page"))


class EditProfileView(generic.UpdateView):
    model = get_user_model()
    template_name = "course/profile_update.html"
    fields = ["username","image"]
    success_url = reverse_lazy("course:profile")


def profile(request):
    return render(request,"course/profile.html")


class CourseByCategory(generic.ListView):
    model = Course
    template_name = "course/base.html"
    def get_queryset(self):
        return (
            Course.objects.filter(categories_id=self.kwargs["pk"])
        )

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # handle_checkout_session(session)
        product_id = session["metadata"]["product_id"]
        user_id = session["metadata"]["user_id"]

        user = get_user_model().objects.get(pk=user_id)
        user.course_paid.add(Course.objects.get(pk=product_id))
        user.save()

    return HttpResponse(status=200)
