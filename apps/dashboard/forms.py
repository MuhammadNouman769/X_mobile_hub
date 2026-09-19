from django import forms
from django.forms import inlineformset_factory

from apps.products.models import Brand, Category, Product, ProductColorVariant


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'brand', 'category', 'name', 'model_number', 'short_description', 'description',
            'ram', 'storage', 'display_size', 'battery', 'camera', 'processor',
            'price', 'discount_price', 'stock_quantity',
            'is_featured', 'is_new_arrival', 'is_active',
        ]
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8GB'}),
            'storage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 256GB'}),
            'display_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6.7 inch'}),
            'battery': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5000mAh'}),
            'camera': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50MP + 12MP'}),
            'processor': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductColorVariantForm(forms.ModelForm):
    class Meta:
        model = ProductColorVariant
        fields = ['color_name', 'color_hex', 'image', 'hover_image', 'stock_quantity', 'is_default']
        widgets = {
            'color_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Midnight Black'}),
            'color_hex': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'hover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


ProductVariantFormSet = inlineformset_factory(
    Product, ProductColorVariant, form=ProductColorVariantForm,
    extra=1, can_delete=True,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon_class', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-phone'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'logo', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
