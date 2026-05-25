from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),

    path('create-post/', views.feed_view, name='feed'),

    path('upload/', views.upload_track, name='upload_track'),
    path('my-tracks/', views.my_tracks, name='my_tracks'),
    path('track/<int:pk>/', views.track_detail, name='track_detail'),

    # Comment action for posts shown on homepage
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('discover/', views.api_music_list, name='api_music_list'),
    
]