import requests
import random
from django.conf import settings
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Track, Album, Playlist, MusicPost, Comment
from .forms import TrackForm, PlaylistForm, MusicPostForm, UserProfileForm

def home_view(request):
    latest_tracks = Track.objects.filter(is_public=True).order_by('-uploaded_at')[:6]

    popular_tracks = Track.objects.filter(is_public=True).annotate(
        post_count=Count('musicpost')
    ).order_by('-post_count', '-uploaded_at')[:6]

    playlists = Playlist.objects.filter(is_public=True).order_by('-created_at')[:4]

    context = {
        'latest_tracks': latest_tracks,
        'popular_tracks': popular_tracks,
        'playlists': playlists,
        'total_tracks': Track.objects.filter(is_public=True).count(),
        'total_playlists': Playlist.objects.filter(is_public=True).count(),
        'total_posts': MusicPost.objects.count(),
    }

    return render(request, 'home.html', context)


@login_required
def feed_view(request):
    return redirect('community')

@login_required
def upload_track(request):
    if request.method == 'POST':
        form = TrackForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.owner = request.user
            track.save()
            return redirect('home')
    else:
        form = TrackForm()

    return render(request, 'upload_track.html', {
        'form': form
    })


@login_required
def my_tracks(request):
    tracks = Track.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, 'my_tracks.html', {
        'tracks': tracks
    })


def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk, is_public=True)
    return render(request, 'track_detail.html', {
        'track': track
    })
    
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(MusicPost, id=post_id)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        playlist_id = request.POST.get('playlist')
        track_id = request.POST.get('track')

        playlist = None
        track = None

        if playlist_id:
            playlist = get_object_or_404(
                Playlist,
                id=playlist_id,
                owner=request.user,
                is_public=True
            )

        if track_id:
            track = get_object_or_404(
                Track,
                id=track_id,
                owner=request.user,
                is_public=True
            )

        if text or playlist or track:
            Comment.objects.create(
                post=post,
                author=request.user,
                text=text,
                playlist=playlist,
                track=track
            )

    return redirect('community')

def api_music_list(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all').strip()
    country = request.GET.get('country', 'PH').strip()
    selected_artist = request.GET.get('artist', '').strip()
    random_mode = request.GET.get('random', '').strip()

    artists = [
        "Arthur Nery", "SLAYR", "Ben&Ben", "Adie", "Janine Tenoso", "Janine Berdin", "Nateman",
        "December Avenue", "Bruno Mars", "Coldplay", "Rex Orange County", "The Weeknd", "Taylor Swift",
        "Olivia Rodrigo", "NIKI", "Daniel Caesar", "Ed Sheeran", "Ariana Grande", "Dua Lipa",
        "Billie Eilish", "LANY", "Joji",  "SZA","Laufey","Wave to Earth", 
    ]

    api_tracks = []
    error_message = None

    url = "https://itunes.apple.com/search"

    def fetch_tracks(term, limit=4):
        params = {
            "term": term,
            "media": "music",
            "entity": "song",
            "limit": limit,
        }

        if country != "ALL":
            params["country"] = country

        if search_type == "song":
            params["attribute"] = "songTerm"
        elif search_type == "artist":
            params["attribute"] = "artistTerm"
        elif search_type == "album":
            params["attribute"] = "albumTerm"
        elif search_type == "composer":
            params["attribute"] = "composerTerm"

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])

        return []

    try:
        if query:
            api_tracks = fetch_tracks(query, limit=50)

        elif selected_artist:
            api_tracks = fetch_tracks(selected_artist, limit=30)
            query = selected_artist

        elif random_mode == "1":
            artist_pool = artists.copy()
            random.shuffle(artist_pool)

            for artist in artist_pool[:10]:
                api_tracks.extend(fetch_tracks(artist, limit=3))

            query = "Random Mix"

        else:
            artist_pool = artists.copy()
            random.shuffle(artist_pool)

            for artist in artist_pool[:12]:
                api_tracks.extend(fetch_tracks(artist, limit=3))

            query = "Featured Mix"

        unique_tracks = {}

        for track in api_tracks:
            track_id = track.get("trackId")

            if track_id and track_id not in unique_tracks:
                unique_tracks[track_id] = track

        api_tracks = list(unique_tracks.values())
        random.shuffle(api_tracks)
        api_tracks = api_tracks[:50]

        if not api_tracks:
            error_message = "No music found. Try another artist, song, or country filter."

    except requests.RequestException as error:
        error_message = f"Connection error: {error}"

    return render(request, "api_music_list.html", {
        "api_tracks": api_tracks,
        "query": query,
        "search_type": search_type,
        "country": country,
        "selected_artist": selected_artist,
        "featured_artists": artists,
        "error_message": error_message,
    })

def community_view(request):
    posts = MusicPost.objects.select_related(
        'author',
        'track'
    ).prefetch_related(
        'comments__author',
        'comments__playlist',
        'comments__track'
    ).order_by('-created_at')

    latest_tracks = Track.objects.filter(is_public=True).order_by('-uploaded_at')[:5]
    playlists = Playlist.objects.filter(is_public=True).order_by('-created_at')[:5]

    if request.user.is_authenticated:
        user_tracks = Track.objects.filter(owner=request.user, is_public=True)
        user_playlists = Playlist.objects.filter(owner=request.user, is_public=True)

        if request.method == 'POST':
            form = MusicPostForm(request.POST)
            form.fields['track'].queryset = user_tracks

            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('community')
        else:
            form = MusicPostForm()
            form.fields['track'].queryset = user_tracks
    else:
        user_tracks = Track.objects.none()
        user_playlists = Playlist.objects.none()
        form = None

    return render(request, 'community.html', {
        'posts': posts,
        'form': form,
        'latest_tracks': latest_tracks,
        'playlists': playlists,
        'user_tracks': user_tracks,
        'user_playlists': user_playlists,
        'total_tracks': Track.objects.filter(is_public=True).count(),
        'total_playlists': Playlist.objects.filter(is_public=True).count(),
        'total_posts': MusicPost.objects.count(),
    })
    
@login_required
def library_view(request):
    user_tracks = Track.objects.filter(owner=request.user).order_by('-uploaded_at')
    user_playlists = Playlist.objects.filter(owner=request.user).order_by('-created_at')

    upload_form = TrackForm()
    playlist_form = PlaylistForm()

    upload_form.fields['album'].queryset = Album.objects.filter(owner=request.user)
    playlist_form.fields['tracks'].queryset = user_tracks

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload_track':
            upload_form = TrackForm(request.POST, request.FILES)
            upload_form.fields['album'].queryset = Album.objects.filter(owner=request.user)

            if upload_form.is_valid():
                track = upload_form.save(commit=False)
                track.owner = request.user
                track.save()
                return redirect('library')

        elif action == 'create_playlist':
            playlist_form = PlaylistForm(request.POST, request.FILES)
            playlist_form.fields['tracks'].queryset = user_tracks

            if playlist_form.is_valid():
                playlist = playlist_form.save(commit=False)
                playlist.owner = request.user
                playlist.save()
                playlist_form.save_m2m()
                return redirect('library')

    return render(request, 'library.html', {
        'upload_form': upload_form,
        'playlist_form': playlist_form,
        'user_tracks': user_tracks,
        'user_playlists': user_playlists,
    })
    
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {
        'form': form
    })