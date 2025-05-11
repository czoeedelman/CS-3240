from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, UploadedImage, BorrowRequest, Collections, Review
from .forms import CollectionForm, PlantForm, UploadImageForm
from .forms import UploadImageForm, ProfilePictureForm
from .models import Plant
from django.contrib.auth.decorators import user_passes_test
from botocore.exceptions import ClientError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from datetime import date, timedelta


def profile(request):
    borrowed_plants = Plant.objects.filter(borrower = request.user)
    print('this user is ', request.user)
    for profile in Profile.objects.all():
        print(profile.user)
    # profile = get_object_or_404(Profile, user = request.user)
    return render(request, 'profile.html', {'borrowed_plants': borrowed_plants})


def borrow_plant(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)

    existing_request = BorrowRequest.objects.filter(plant=plant, user=request.user)
    if not existing_request.exists():
        BorrowRequest.objects.create(user=request.user, plant=plant)
        plant.is_available = False
        plant.save()

    return redirect("plant_list")

def delete_borrow_request(request, br_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=br_id)
    plant = borrow_request.plant
    borrow_request.delete()
    if not BorrowRequest.objects.filter(plant=plant).exists():
        plant.is_available = True
        plant.save()
    return redirect("my_requests")

from datetime import timedelta
from django.utils import timezone

def approve_request(request, br_id):
    print('here')
    borrow_request = get_object_or_404(BorrowRequest, pk=br_id)
    borrow_request.status = 'Approved'

    DEFAULT_DURATION_DAYS = 14
    borrow_request.return_date = date.today() + timedelta(days=DEFAULT_DURATION_DAYS)

    borrow_request.save()
    plant = borrow_request.plant

    plant.is_available = False
    plant.borrower = borrow_request.user
    plant.return_date = timezone.now() + timedelta(weeks=1)
    print("return date: ", plant.return_date)
    plant.save()
    return redirect("manage_requests")

def decline_request(request, br_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=br_id)
    plant = borrow_request.plant
    borrow_request.status = 'Rejected'
    borrow_request.save()
    if not BorrowRequest.objects.filter(plant=plant, status='Approved').exists():
        plant.is_available = True
        plant.save()
    return redirect("manage_requests")

def plant_add(request):
    if request.method == "POST":
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("plant_list")
    else:
        form = PlantForm()
    return render(request, "plants/plant_add.html", {"form": form})

from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpResponseForbidden

from django.shortcuts import get_object_or_404, redirect, render
import logging

# Set up logging
logger = logging.getLogger(__name__)

def plant_edit(request, pk):
    plant = get_object_or_404(Plant, pk=pk)

    if request.method == "POST":
        form = PlantForm(request.POST, request.FILES, instance=plant)
        if form.is_valid():
            form.save()

            # Get 'next' parameter from POST, defaulting to 'plant_list'
            next_url = request.POST.get('next', 'plant_list')  
            
            # Log the URL that the user will be redirected to
            logger.info(f"Redirecting to: {next_url}")

            return redirect(next_url)
    else:
        form = PlantForm(instance=plant)

    return render(request, "plants/plant_edit.html", {"form": form, "plant": plant})

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Plant
def plant_delete(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    if request.user.profile.is_librarian:  # Optional permission check
        plant.delete()
    return redirect('plant_list')

from django.shortcuts import render
from django.db.models import Q
from .models import Plant

def plant_list(request):
    # Start with all plants that are in public collections
    plants = Plant.objects.exclude(collections__is_public=False).distinct()

    query = request.GET.get('q', '')
    sunlight = request.GET.get('sunlight', '')
    water = request.GET.get('water', '')
    humidity = request.GET.get('humidity', '')
    size = request.GET.get('size', '')
    difficulty = request.GET.get('difficulty', '')
    price_range = request.GET.get('price_range', '')

    if query:
        plants = plants.filter(
            Q(name__icontains=query)
        )

    if sunlight:
        plants = plants.filter(sunlight_reqs=sunlight)

    if water:
        plants = plants.filter(water_reqs=water)

    if humidity:
        plants = plants.filter(humidity_reqs=humidity)

    if size:
        plants = plants.filter(size=size)

    if difficulty:
        plants = plants.filter(difficulty=difficulty)

    if price_range:
        plants = plants.filter(price_range=price_range)

    return render(request, "plants/plant_list.html", {"plants": plants})

def upload_image(request):
    if request.method == "POST":
        profile_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_form.is_valid():
            try:
                profile = Profile.objects.get(user=request.user)
                profile.profile_picture = profile_form.cleaned_data['profile_picture']
                profile.save()
                return redirect("upload_success")
            except ObjectDoesNotExist:
                error_message = "Profile does not exist for the current user."
                return render(request, "upload.html", {"profile_form": profile_form, "error": error_message})
            except ClientError as e:
                return render(request, "upload.html", {"profile_form": profile_form, "error": str(e)})
    else:
        profile_form = ProfilePictureForm()
    return render(request, "upload.html", {"profile_form": profile_form})

def upload_success(request):
    return render(request, "upload_success.html")

@login_required
def patron_landing(request):
    # A simple page just for patrons
    return render(request, "patron_landing.html")

@login_required
def librarian_landing(request):
    # A simple page just for librarians
    return render(request, "librarian_landing.html")

@login_required
def role_check(request):
    """
    After Google login, this view checks if the user is a librarian or patron
    and redirects them to the appropriate landing page.
    """
    # 1) Access the user's profile
    #    If you haven't set up signals, you must ensure a Profile object exists 
    #    for every user. That can be done in admin or via code.
    profile = Profile.objects.get(user=request.user)

    # 2) Check role and redirect
    if profile.is_librarian:
        return redirect("librarian_landing")
    else:
        return redirect("patron_landing")

@user_passes_test(lambda u: u.profile.is_librarian)
def promote_user(request, user_id):
    """
    A librarian-only view that promotes a given user to librarian.
    """
    user_to_promote = User.objects.get(id=user_id)
    user_to_promote.profile.is_librarian = True
    user_to_promote.profile.save()
    return redirect("somewhere")  # redirect back to a list of users or a success page

@login_required
def my_requests(request):
    borrow_requests = BorrowRequest.objects.filter(user=request.user)
    print(borrow_requests.count())
    return render(request, "my_requests.html", {"borrow_requests": borrow_requests})

@login_required
def request_collection(request, collection_id):
    collection = get_object_or_404(Collections, pk=collection_id)
    if collection.is_public or request.user in collection.allowed_users.all():
        return redirect("view_collections")
    
    collection.requested_users.add(request.user)
    return redirect("view_collections")

@login_required
def manage_requests(request):
    # Ensure only librarians can access this view
    if not request.user.profile.is_librarian:
        return redirect("home")

    if request.method == "POST":
        # Handle borrow request approval/rejection
        if "borrow_request_id" in request.POST:
            borrow_request_id = request.POST.get("borrow_request_id")
            action = request.POST.get("action")
            borrow_request = get_object_or_404(BorrowRequest, pk=borrow_request_id)

            if action == "approve":
                borrow_request.request_date = date.today()
                borrow_request.status = "Approved"
                borrow_request.return_date = date.today() + timedelta(days=30)
                borrow_request.save()
                plant = borrow_request.plant
                plant.is_available = False
                plant.borrower = borrow_request.user
                plant.return_date = timezone.now() + timedelta(weeks=1)
                plant.save()
            elif action == "reject":
                borrow_request.status = "Rejected"
                borrow_request.save()
                plant = borrow_request.plant
                if not BorrowRequest.objects.filter(plant=plant, status="Approved").exists():
                    plant.is_available = True
                    plant.save()

        #Handle extension approval/rejection 
        elif "extension_request_id" in request.POST:
            extension_request_id = request.POST.get("extension_request_id")
            action = request.POST.get("action")
            borrow_request = get_object_or_404(BorrowRequest, pk=extension_request_id)

            if action == "approve_extension":
                if borrow_request.return_date:
                    borrow_request.return_date += timedelta(days=30)
                else:
                    borrow_request.return_date = date.today() + timedelta(days=30)
                borrow_request.extension_requested = False
                borrow_request.extension_granted = True
                borrow_request.save()
            elif action == "reject_extension":
                borrow_request.extension_requested = False  # Just reset without extending
                borrow_request.save()

        # Handle collection access requests
        elif "collection_id" in request.POST:
            collection_id = request.POST.get("collection_id")
            user_id = request.POST.get("user_id")
            action = request.POST.get("action")
            collection = get_object_or_404(Collections, pk=collection_id)
            user = get_object_or_404(User, pk=user_id)

            if action == "approve":
                collection.allowed_users.add(user)
                collection.requested_users.remove(user)
            elif action == "reject":
                collection.requested_users.remove(user)

        return redirect("manage_requests")

    # Fetch pending borrow requests
    borrow_requests = BorrowRequest.objects.filter(status="Pending")

    # Fetch extension requests
    extension_requests = BorrowRequest.objects.filter(extension_requested=True, status="Approved")

    # Fetch collection access requests
    collection_requests = Collections.objects.filter(requested_users__isnull=False).distinct()

    return render(request, "manage_requests.html", {
        "borrow_requests": borrow_requests,
        "collection_requests": collection_requests,
        "extension_requests": extension_requests,
    })


@login_required
def create_collection(request):
    if request.method == "POST":
        form = CollectionForm(request.POST, user=request.user)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user
            collection.save()
            form.save_m2m()
            return redirect("view_collections")
    else:
        form = CollectionForm(user=request.user)
        
    return render(request, "create_collection.html", {"form": form})

@login_required
def view_collections(request):
    collections = Collections.objects.all()
    form = CollectionForm(user=request.user) if request.method == "GET" else CollectionForm(request.POST, user=request.user)
    

    if request.method == "POST":
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user  # use 'creator' if that's the field name
            collection.save()
            form.save_m2m()
            return redirect("view_collections")

    return render(request, "view_collections.html", {
        "collections": collections,
        "form": form
    })

@login_required
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collections, pk=collection_id)

    if not collection.is_public:
        if request.user not in collection.allowed_users.all() and not request.user.profile.is_librarian:
            return HttpResponseForbidden("You are not allowed to view this private collection.")

    plants = collection.plants.all()

    # Hide any plants that are also in private collections the user isn't allowed to see
    if not request.user.profile.is_librarian:
        private_collections = Collections.objects.filter(
            is_public=False
        ).exclude(
            allowed_users=request.user
        )

        # Exclude any plant that is also in any restricted private collection
        plants = plants.exclude(collections__in=private_collections).distinct()
        
    query = request.GET.get("q")
    if query:
        plants = plants.filter(name__icontains=query)

    return render(request, "collection_detail.html", {
        "collection": collection,
        "plants": plants,
    })




@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collections, pk=collection_id)

    if collection.creator != request.user and not request.user.profile.is_librarian:
        return redirect("view_collections")

    form = CollectionForm(request.POST or None, instance=collection, user=request.user)

    if request.method == "POST" and form.is_valid():
        if not request.user.profile.is_librarian:
            form.instance.creator = collection.creator

        form.save()
        return redirect("view_collections")

    return render(request, "edit_collection.html", {"form": form, "collection": collection})


@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collections, pk=collection_id)

    if collection.creator == request.user or request.user.profile.is_librarian:
        # Only allow deletion if the user is the creator or a librarian
        collection.delete()

    return redirect("view_collections")


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

@login_required
def leave_review(request, plant_id):
    if request.method == "POST":
        plant = Plant.objects.get(pk=plant_id)
        comment = request.POST.get("comment")
        rating = request.POST.get("rating")
        Review.objects.create(
            plant=plant,
            user=request.user,
            comment=comment,
            rating=rating
        )
        return redirect("plant_list")
    
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user == request.user:
        review.delete()
    return redirect("plant_list")

@login_required
def manage_patrons(request):
    if not request.user.profile.is_librarian:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    users = User.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        

        if action == "toggle librarian":
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, pk=user_id)
            user.profile.is_librarian = not user.profile.is_librarian
            user.profile.save()

        elif action == "remove_borrowed_plant":
            plant_id = request.POST.get("plant_id")
            plant = get_object_or_404(Plant, pk=plant_id)
            plant.borrower = None
            plant.is_available = True
            plant.save()

        elif action == "remove_from_collection":
            collection_id = request.POST.get("collection_id")
            collection = get_object_or_404(Collections, pk=collection_id)
            collection.allowed_users.add(user)

        elif action == "promote_to_librarian":
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, pk=user_id)
            user.profile.is_librarian = True
            user.profile.save()
        elif action == "demote_to_patron":
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, pk=user_id)
            user.profile.is_librarian = False
            user.profile.save()

        return redirect("manage_patrons")

    return render(request, "manage_patrons.html", {"users": users})

@login_required
def upload_profile_picture(request):
    if request.method == 'POST':
        print("Files in request:", request.FILES)  # Debug print
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            try:
                profile = form.save()
                print(f"Profile picture saved: {profile.profile_picture.url}")  # Debug print
                messages.success(request, 'Profile picture updated successfully!')
            except Exception as e:
                print(f"Error saving profile picture: {str(e)}")  # Debug print
                messages.error(request, f'Error updating profile picture: {str(e)}')
        else:
            print(f"Form errors: {form.errors}")  # Debug print
            messages.error(request, f'Error updating profile picture: {form.errors}')
    return redirect('profile')

def request_extension(request, br_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=br_id, user=request.user)

    if borrow_request.status == "Approved" and not borrow_request.extension_requested:
        borrow_request.extension_requested = True
        borrow_request.save()

    return redirect("my_requests")
