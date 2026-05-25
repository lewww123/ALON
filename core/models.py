from django.db import models
from django.contrib.auth.models import User


class Album(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=150)
    cover = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Track(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracks')
    title = models.CharField(max_length=150)
    artist_name = models.CharField(max_length=150)
    audio_file = models.FileField(upload_to='tracks/')
    cover_image = models.ImageField(upload_to='track_covers/', blank=True, null=True)
    genre = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='playlist_covers/', blank=True, null=True)
    tracks = models.ManyToManyField(Track, blank=True, related_name='playlists')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MusicPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='music_posts')
    caption = models.TextField()
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True)
    likes = models.ManyToManyField(User, blank=True, related_name='liked_music_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author.username}"


class Comment(models.Model):
    post = models.ForeignKey(MusicPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)

    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shared_in_comments'
    )

    track = models.ForeignKey(
        Track,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shared_in_comments'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username}"