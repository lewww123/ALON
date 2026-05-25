from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),

    path('community/', views.community_view, name='community'),
    path('library/', views.library_view, name='library'),
    path('profile/', views.profile_view, name='profile'),
    path('create-post/', views.feed_view, name='feed'),

    # optional old routes, para hindi mag-error kung may old links
    path('create-post/', views.feed_view, name='feed'),
    path('upload/', views.library_view, name='upload_track'),
    path('my-tracks/', views.library_view, name='my_tracks'),

    path('track/<int:pk>/', views.track_detail, name='track_detail'),
    path('discover/', views.api_music_list, name='api_music_list'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]