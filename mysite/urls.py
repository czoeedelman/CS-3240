from django.contrib import admin
from django.http import HttpResponse  # Import HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.urls import path, include
from plants import views as plant_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from plants.models import Profile  # Import Profile model


def home_view(request):  
    return HttpResponse("This is the initial deployment to ensure Heroku is working")


def home(request):
    profile_picture_url = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            if profile.profile_picture:
                profile_picture_url = profile.profile_picture.url
        except Profile.DoesNotExist:
            pass
    return render(request, "home.html", {"profile_picture_url": profile_picture_url})


def profile(request):
    if request.user.is_authenticated:
        # Ensure groups exist
        librarian_group, _ = Group.objects.get_or_create(name="Librarians")
        patron_group, _ = Group.objects.get_or_create(name="Patrons")

        # Automatically assign new users to "Patrons" if they don't belong to any group
        if not request.user.groups.exists():
            request.user.groups.add(patron_group)
            request.user.save()

        if request.user.groups.filter(name="Librarians").exists():
            return render(request, "librarian_landing.html", {"user": request.user})
        elif request.user.groups.filter(name="Patrons").exists():
            return render(request, "patron_landing.html", {"user": request.user})

    # If not logged in, redirect to home
    return redirect("home")


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name="home"),
    path('profile/', profile, name="profile"),
    path('accounts/', include('allauth.urls')),
    path("role-check/", plant_views.role_check, name="role_check"),
    path('patron/', login_required(lambda request: render(request, "patron_landing.html")), name="patron_landing"),
    path('librarian/', login_required(lambda request: render(request, "librarian_landing.html")), name="librarian_landing"),
    path("plants/", include("plants.urls")),
]
