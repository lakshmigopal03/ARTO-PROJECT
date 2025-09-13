from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ArtistProfile, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(
        choices=[('buyer', 'Art Collector/Buyer'), ('artist', 'Artist/Seller')],
        widget=forms.RadioSelect,
        initial='buyer'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create appropriate profile based on user type
            user_type = self.cleaned_data['user_type']
            if user_type == 'artist':
                ArtistProfile.objects.create(
                    user=user,
                    artist_name=f"{user.first_name} {user.last_name}",
                    bio="Welcome to ARTO! Add your bio here."
                )
                UserProfile.objects.create(user=user, is_artist=True)
            else:
                UserProfile.objects.create(user=user, is_artist=False)
        
        return user

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = [
            'artist_name', 'bio', 'specialty', 'experience_level',
            'website', 'instagram', 'facebook', 'twitter',
            'city', 'country', 'profile_image', 'accepts_commissions'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell people about yourself and your artistic journey...'}),
            'artist_name': forms.TextInput(attrs={'placeholder': 'Your artistic name'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'instagram': forms.TextInput(attrs={'placeholder': 'username'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://facebook.com/yourpage'}),
            'twitter': forms.TextInput(attrs={'placeholder': 'username'}),
            'city': forms.TextInput(attrs={'placeholder': 'Your city'}),
            'country': forms.TextInput(attrs={'placeholder': 'Your country'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'birth_date', 'newsletter_subscription']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }