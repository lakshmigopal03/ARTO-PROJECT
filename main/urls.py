from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Artist Profile URLs
    path('artists/', views.artists_list, name='artists_list'),
    path('artist/<int:pk>/', views.artist_profile_view, name='artist_profile_view'),
    path('artist/edit/', views.artist_profile_edit, name='artist_profile_edit'),
    path('become-artist/', views.become_artist, name='become_artist'),
]