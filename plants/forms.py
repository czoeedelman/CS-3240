from django import forms
from .models import UploadedImage, Plant
from .models import Profile
from .models import Collections


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']

class PlantForm(forms.ModelForm):
    SUNLIGHT_CHOICES = [
        ('Low/Artificial', 'Low/Artificial'),
        ('Partial/Bright Indirect', 'Partial/Bright Indirect'),
        ('Direct Sunlight', 'Direct Sunlight'),
    ]

    WATER_CHOICES = [
        ('Dry', 'Dry'),
        ('Moist', 'Moist'),
        ('Frequent', 'Frequent'),
    ]

    HUMIDITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    SIZE_CHOICES = [
        ('XS (5-12 inches)', 'XS (5-12 inches)'),
        ('SM (7-18 inches)', 'SM (7-18 inches)'),
        ('MD (1-2 FT)', 'MD (1-2 FT)'),
        ('LG (1.5-2.5 FT)', 'LG (1.5-2.5 FT)'),
        ('XL (2-3 FT)', 'XL (2-3 FT)'),
        ('XXL (3-5 FT)', 'XXL (3-5 FT)'),
    ]

    DIFFICULTY_CHOICES = [
        ('No-fuss', 'No-fuss'),
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
    ]

    PRICE_CHOICES = [
        ('Under $20', 'Under $20'),
        ('$20-$50', '$20-$50'),
        ('$50-$100', '$50-$100'),
        ('$100-$150', '$100-$150'),
        ('$150-$200', '$150-$200'),
        ('$200 & Above', '$200 & Above'),
    ]

    sunlight_reqs = forms.ChoiceField(choices=SUNLIGHT_CHOICES)
    water_reqs = forms.ChoiceField(choices=WATER_CHOICES)
    humidity_reqs = forms.ChoiceField(choices=HUMIDITY_CHOICES)
    size = forms.ChoiceField(choices=SIZE_CHOICES)
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES)
    location = forms.CharField(max_length=100, required=False, initial="Charlottesville, VA")
    price_input = forms.DecimalField(label="Price", required=True, min_value=0)

    class Meta:
        model = Plant
        fields = ['name', 'description', 'sunlight_reqs', 'water_reqs', 'humidity_reqs', 'size', 'difficulty', 'price_input', 'temperature_range', 'soil', 'image']

    def save(self, commit=True):
        instance = super().save(commit=False)
        price = self.cleaned_data['price_input']
        instance.price = price

        # Automatically decide price_range
        if price < 20:
            instance.price_range = "Under $20"
        elif 20 <= price <= 50:
            instance.price_range = "$20-$50"
        elif 50 < price <= 100:
            instance.price_range = "$50-$100"
        elif 100 < price <= 150:
            instance.price_range = "$100-$150"
        elif 150 < price <= 200:
            instance.price_range = "$150-$200"
        else:
            instance.price_range = "$200 & Above"

        if commit:
            instance.save()
        return instance

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collections
        fields = ['title', 'description', 'plants', 'is_public']  # Do not include 'is_public' here for non-librarians
        widgets = {
            'plants': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.user = user

        # Filter plants to exclude those in private collections
        self.fields['plants'].queryset = Plant.objects.exclude(collections__is_public=False)

        if self.user and self.user.profile.is_librarian:
            self.fields['is_public'] = forms.BooleanField(required=False, initial=True)
        else:
            self.fields['is_public'] = forms.BooleanField(required=False, initial=True, widget=forms.HiddenInput())

    def save(self, commit=True):
        collection = super().save(commit=False)

        if not hasattr(collection, 'creator'):
            collection.creator = self.user

        if not self.user.profile.is_librarian:
            collection.is_public = True  # Non-librarians can't toggle this; it defaults to True

        if commit:
            collection.save()
            self.save_m2m()

        for plant in self.cleaned_data.get('plants', []):
            if not collection.pk:
                collection.save()
            plant.collections.add(collection)

        for plant in Plant.objects.all():
            if plant not in self.cleaned_data.get('plants', []):
                plant.collections.remove(collection)

        return collection
