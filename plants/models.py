from django.db import models
from django.contrib.auth.models import User
from datetime import date

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')

    def __str__(self):
        return self.image.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_librarian = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - {self.profile_picture.name if self.profile_picture else 'No Profile Picture'}"



class Plant(models.Model):
    name = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)

    description = models.TextField(blank=True, null=True)
    sunlight_reqs = models.CharField(max_length=100)
    water_reqs = models.CharField(max_length=100)
    temperature_range = models.CharField(max_length=100, blank=True, null=True)
    humidity_reqs = models.CharField(max_length=100, blank=True, null=True)
    soil = models.CharField(max_length=100, blank=True, null=True)

    is_available = models.BooleanField(default=True)
    borrower = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="borrowed_plants"
    )
    return_date = models.DateField(null=True, blank=True)

    comments = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    image = models.ImageField(upload_to="plant_images/", blank=True, null=True)

    collections = models.ManyToManyField(
        'Collections',
        blank=True,
        related_name="plant_collections"
    )

    size = models.CharField(max_length=20)        # <-- NEW
    difficulty = models.CharField(max_length=20)  # <-- NEW

    # ← changed from CharField to DecimalField with default=0, no empty‐string allowed
    price_range = models.CharField(max_length=20, default="Under $20")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    location = models.CharField(max_length=100, blank=True, null=True, default="Charolottesville, VA")


    def __str__(self):
        return f"{self.name}  borrowed by {self.borrower}"


class BorrowRequest(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    STATUSES = [
        ("Pending", "pending"),
        ("Approved", "approved"),
        ("Rejected", "rejected")
    ]

    status = models.CharField(max_length=10, choices=STATUSES, default="Pending")
    request_date = models.DateField(default=date.today)
    return_date = models.DateField(null=True, blank=True)
    extension_requested = models.BooleanField(default=False)
    extension_granted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user} -> {self.plant.name} :: Status: {self.status}"


class Collections(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    plants = models.ManyToManyField(Plant, blank=True, related_name="collections_plants")

    is_public = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, blank=True, related_name="allowed_collections")
    requested_users = models.ManyToManyField(User, blank=True, related_name="requested_collections")

    def __str__(self):
        return f"{self.title} by {self.creator.username}"


class Review(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews")
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.plant.name}"

