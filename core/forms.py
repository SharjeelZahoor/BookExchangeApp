from django import forms
from .models import Book, GENRE_CHOICES, CONDITION_CHOICES
from .models import ExchangeRequest, Book

class ExchangeRequestForm(forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ['from_book']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['from_book'].queryset = Book.objects.filter(owner=user, status='available')

class BookForm(forms.ModelForm):
    genre = forms.ChoiceField(choices=GENRE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition', 'location', 'photo', 'external_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'external_url': forms.URLInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
        
from .models import Wishlist

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['title', 'author', 'genre', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
