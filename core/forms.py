from django import forms
from django.contrib.auth.models import User
from .models import Track, Album, Playlist, MusicPost, Comment


class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = [
            'album',
            'title',
            'artist_name',
            'audio_file',
            'cover_image',
            'genre',
            'description',
            'is_public',
        ]


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'cover', 'description']


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = [
            'title',
            'description',
            'cover',
            'tracks',
            'is_public',
        ]


class MusicPostForm(forms.ModelForm):
    class Meta:
        model = MusicPost
        fields = ['caption', 'track']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]