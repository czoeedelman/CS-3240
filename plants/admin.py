from django.contrib import admin
from .models import Plant, UploadedImage, BorrowRequest, Collections
from .models import Profile

admin.site.register(Plant)
admin.site.register(UploadedImage)
admin.site.register(BorrowRequest)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_librarian", "profile_picture")

@admin.register(Collections)
class CollectionsAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "is_public")
    filter_horizontal = ("allowed_users", "requested_users")  # Allows editing ManyToMany fields