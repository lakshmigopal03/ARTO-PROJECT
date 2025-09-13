
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image

class ArtistProfile(models.Model):
    SPECIALTIES = (
        ('painter', 'Painter'),
        ('sculptor', 'Sculptor'),
        ('digital_artist', 'Digital Artist'),
        ('photographer', 'Photographer'),
        ('mixed_media', 'Mixed Media Artist'),
        ('illustrator', 'Illustrator'),
        ('other', 'Other'),
    )
    
    EXPERIENCE_LEVELS = (
        ('beginner', 'Beginner (0-2 years)'),
        ('intermediate', 'Intermediate (3-5 years)'),
        ('experienced', 'Experienced (6-10 years)'),
        ('professional', 'Professional (10+ years)'),
    )
    
    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    
    # Basic Artist Information
    artist_name = models.CharField(max_length=100, help_text="Display name for your art")
    bio = models.TextField(max_length=500, blank=True, help_text="Tell people about yourself and your art")
    specialty = models.CharField(max_length=20, choices=SPECIALTIES, default='other')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='beginner')
    
    # Contact & Social
    website = models.URLField(blank=True, help_text="Your personal website or portfolio")
    instagram = models.CharField(max_length=100, blank=True, help_text="Instagram username (without @)")
    facebook = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True, help_text="Twitter username (without @)")
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Profile Settings
    profile_image = models.ImageField(upload_to='artist_profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="Verified by ARTO team")
    accepts_commissions = models.BooleanField(default=False, help_text="Available for custom work")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Artist Profile"
        verbose_name_plural = "Artist Profiles"
    
    def __str__(self):
        return f"{self.artist_name} ({self.user.username})"
    
    def get_absolute_url(self):
        return reverse('artist_profile', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile image if it exists
        if self.profile_image:
            img = Image.open(self.profile_image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_image.path)

class UserProfile(models.Model):
    """Extended profile for regular users (collectors/buyers)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    is_artist = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    newsletter_subscription = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"