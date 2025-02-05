from django import forms
from django.contrib import admin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

from .models import InventoryProduct, Volume, Item  # Adjust the import path as necessary
from .models import Product, VolumesPackage
from ..abstract.utlites.menu_nums import CategoryChoices
from unfold.admin import ModelAdmin
from djmoney.money import Money


class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = ['product', 'volume_number', 'price', 'start_chapter', 'end_chapter', 'image']

@admin.register(Volume)
class VolumeAdmin(ModelAdmin):
    form = VolumeForm
    search_fields = ['product__name', 'volume_number']  # Adjust fields based on your needs
    list_display = ['product', 'volume_number', 'price']  # Adjust fields as necessary
    autocomplete_fields = ['product']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['product', 'volume_number', 'price', 'start_chapter', 'end_chapter', 'image']

@admin.register(Item)
class ItemAdmin(ModelAdmin):
    form = ItemForm
    search_fields = ['product__name', 'volume_number']  # Adjust fields based on your needs
    list_display = ['product', 'volume_number', 'price']  # Adjust fields as necessary
    autocomplete_fields = ['product']


class InventoryProductForm(forms.ModelForm):
    class Meta:
        model = InventoryProduct
        fields = ('language', 'quantity', 'price', 'volume')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['price'].initial = Money(5000, 'IQD')
            self.fields['quantity'].initial = 1


@admin.register(InventoryProduct)
class InventoryProductAdmin(ModelAdmin):
    form = InventoryProductForm
    list_display = ["language", "quantity", "price", "volume"]
    list_filter = ["language"]
    # it will use the search field of the Volume model
    autocomplete_fields = ['volume']


class VolumePackageForm(forms.ModelForm):
    # volumes = forms.MultipleChoiceField(choices=Volume.objects.all())
    image_upload = forms.ImageField(required=False)  # Change FileField to ImageField if you're dealing with images

    class Meta:
        model = VolumesPackage
        fields = ['package_name', 'price', 'volumes', 'image_upload']
        widgets = {
            'image_upload': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class VolumesPackageAdmin(ModelAdmin):
    form = VolumePackageForm
    autocomplete_fields = ('volumes',)  # Enable autocomplete for 'volumes'
    list_display = ["product", "price", "created_at"]
    search_fields = ["product__name"]
    # list_filter = ["product"]

    @transaction.atomic
    def save_model(self, request, obj, form, change):

        if form.is_valid():
            # Handle image upload
            if image := form.cleaned_data.get('image_upload'):
                image_path = f'volumes_package/{image.name}'
                obj.image.save(image_path, image, save=False)


            # Set type to 'Package'
            obj.type = 'Package'

            # # Save the object if it's new
            if not obj.id:
                super().save_model(request, obj, form, change)

            # Now we can access the many-to-many relationship
            if volumes := form.cleaned_data.get('volumes'):
                volumes_qs = Volume.objects.filter(id__in=volumes)
                if volumes.values_list('product', flat=True).distinct().count() > 1:
                    raise ValueError('All volumes must belong to the same product')

                obj.product = volumes_qs.first().product
                obj.start_volume = volumes_qs.order_by('volume_number').first().volume_number
                obj.end_volume = volumes_qs.order_by('-volume_number').first().volume_number
                obj.volume_count = volumes_qs.count()

                obj.save(update_fields=['product', 'start_volume', 'end_volume', 'volume_count'])

                # Assign the M2M relationship
                obj.volumes.set(volumes_qs)
            # Save again to update the fields we just set
            super().save_model(request, obj, form, change)
        else:
            print("Form errors:", form.errors)


admin.site.register(VolumesPackage, VolumesPackageAdmin)


class ProductForm(forms.ModelForm):
    category = forms.MultipleChoiceField(choices=CategoryChoices.choices)

    class Meta:
        model = Product
        fields = '__all__'


class ProductAdmin(ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    form = ProductForm


admin.site.register(Product, ProductAdmin)


# class VolumeAdmin(ModelAdmin):
#     list_display = ["product", "volume_number", "price", "created_at"]
#     search_fields = ["product__name"]
#     list_filter = ["product"]
#
# admin.site.register(Volume, VolumeAdmin)


