from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ArtistProfileForm, UserProfileForm
from .models import ArtistProfile, UserProfile

def home(request):
    """Homepage view with featured categories and artists"""
    # Get real featured artists if they exist, otherwise use sample data
    featured_artists_qs = ArtistProfile.objects.filter(is_verified=True)[:3]
    
    if featured_artists_qs.exists():
        featured_artists = featured_artists_qs
    else:
        # Sample data for demo
        featured_artists = [
            {'artist_name': 'Sarah Johnson', 'specialty': 'Abstract Painter', 'bio': 'Contemporary artist'},
            {'artist_name': 'Michael Chen', 'specialty': 'Digital Artist', 'bio': 'Digital art specialist'},
            {'artist_name': 'Emma Rodriguez', 'specialty': 'Sculptor', 'bio': 'Modern sculptor'},
        ]
    
    context = {
        'featured_categories': [
            {'name': 'Paintings', 'count': 245, 'image': 'paintings.jpg'},
            {'name': 'Sculptures', 'count': 89, 'image': 'sculptures.jpg'},
            {'name': 'Digital Art', 'count': 156, 'image': 'digital.jpg'},
            {'name': 'Photography', 'count': 302, 'image': 'photography.jpg'},
        ],
        'featured_artists': featured_artists
    }
    return render(request, 'main/home.html', context)

@login_required
def dashboard(request):
    """User dashboard - different content for artists vs regular users"""
    # Check if user has artist profile
    is_artist = hasattr(request.user, 'artist_profile')
    
    # Ensure user has a UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'user': request.user,
        'is_artist': is_artist,
        'user_profile': user_profile,
        'recent_activities': [
            {'action': 'Profile updated', 'item': 'Personal information', 'time': '2 hours ago'},
            {'action': 'Joined ARTO', 'item': 'Welcome to the community!', 'time': '1 day ago'},
        ],
        'stats': {
            'favorites': 0,
            'orders': 0,
            'following': 0,
            'cart_items': 0,
        },
    }
    
    # Add artist-specific data if user is an artist
    if is_artist:
        artist_profile = request.user.artist_profile
        context['artist_profile'] = artist_profile
        context['stats']['artworks'] = 0  # Will update when artwork model is created
        context['recent_activities'].insert(0, {
            'action': 'Artist profile created', 
            'item': 'Ready to upload artworks', 
            'time': 'Recently'
        })
    
    return render(request, 'main/dashboard.html', context)

def register_view(request):
    """User registration with artist/buyer type selection"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            user_type = form.cleaned_data.get('user_type')
            
            if user_type == 'artist':
                messages.success(request, f'Welcome to ARTO, {username}! Your artist profile has been created. Complete your profile to start selling.')
            else:
                messages.success(request, f'Welcome to ARTO, {username}! Start exploring amazing artworks.')
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    """User login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or username}!')
                # Check if there's a 'next' parameter for redirect
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have successfully logged out. Come back soon!')
    return redirect('home')

@login_required
def artist_profile_edit(request):
    """Edit artist profile - only for users who have artist profiles"""
    try:
        artist_profile = request.user.artist_profile
    except ArtistProfile.DoesNotExist:
        messages.error(request, 'You need to register as an artist first.')
        return redirect('become_artist')
    
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your artist profile has been updated successfully!')
            return redirect('artist_profile_view', pk=artist_profile.pk)
    else:
        form = ArtistProfileForm(instance=artist_profile)
    
    return render(request, 'main/artist_profile_edit.html', {
        'form': form, 
        'artist_profile': artist_profile
    })

def artist_profile_view(request, pk):
    """Public artist profile view"""
    artist_profile = get_object_or_404(ArtistProfile, pk=pk)
    
    context = {
        'artist_profile': artist_profile,
        'is_owner': request.user == artist_profile.user if request.user.is_authenticated else False,
        'artworks': [],  # Will populate when artwork model is ready
    }
    
    return render(request, 'main/artist_profile_view.html', context)

def artists_list(request):
    """List all artists with filtering options"""
    artists = ArtistProfile.objects.select_related('user').order_by('-created_at')
    
    # Filter by specialty if provided
    specialty = request.GET.get('specialty')
    if specialty:
        artists = artists.filter(specialty=specialty)
    
    context = {
        'artists': artists,
        'specialties': ArtistProfile.SPECIALTIES,
        'selected_specialty': specialty,
    }
    
    return render(request, 'main/artists_list.html', context)

@login_required
def become_artist(request):
    """Convert regular user to artist"""
    # Check if user is already an artist
    if hasattr(request.user, 'artist_profile'):
        messages.info(request, 'You are already registered as an artist.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES)
        if form.is_valid():
            artist_profile = form.save(commit=False)
            artist_profile.user = request.user
            artist_profile.save()
            
            # Update user profile to mark as artist
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            user_profile.is_artist = True
            user_profile.save()
            
            messages.success(request, 'Congratulations! You are now registered as an artist on ARTO. Start uploading your artworks!')
            return redirect('dashboard')
    else:
        # Pre-fill artist name with user's full name
        initial_name = f"{request.user.first_name} {request.user.last_name}".strip()
        if not initial_name:
            initial_name = request.user.username
        
        form = ArtistProfileForm(initial={'artist_name': initial_name})
    
    return render(request, 'main/become_artist.html', {'form': form})