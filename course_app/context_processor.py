from .models import Category


def context(request):
    categories = Category.objects.all()
    return {
        "categories": categories,
    }
