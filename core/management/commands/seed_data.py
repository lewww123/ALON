import random
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Album, Track, Playlist, MusicPost, Comment


class Command(BaseCommand):
    help = "Seed fake data for the ALON music platform"

    def handle(self, *args, **kwargs):
        fake = Faker()

        self.stdout.write(self.style.WARNING("Seeding ALON fake data..."))

        genres = [
            "OPM", "Pop", "R&B", "Indie", "Rock",
            "Hip-hop", "Acoustic", "Alternative", "Lo-fi", "Soul"
        ]

        artists = [
            "Arthur Nery", "SLAYR", "Ben&Ben", "Adie",
            "Janine Tenoso", "Janine Berdin", "Nateman", "December Avenue",
            "Bruno Mars", "Coldplay", "Rex Orange County", "The Weeknd",
            "Moira Dela Torre", "Zack Tabudlo", "NIKI"
        ]

        song_titles = [
            "Midnight Waves", "Blue Hour", "City Lights", "Afterglow",
            "Lost in Sound", "Ocean Drive", "Soft Echoes", "Rainy Evening",
            "Golden Days", "Moonlit Road", "Tides of You", "Slow Burn",
            "Parallel Hearts", "Summer Noise", "Late Night Signal",
            "Stay With the Sound", "Cloud Nine", "Harana sa Gabi",
            "Silent Rhythm", "Waves Apart", "Dream Frequency",
            "Breathe Again", "Electric Sunset", "Letters in Melody",
            "ALON Anthem"
        ]

        album_titles = [
            "Blue Hour Sessions",
            "Midnight Collection",
            "Waves and Echoes",
            "Soft City Lights",
            "ALON Originals",
            "Late Night Soundscape"
        ]

        playlist_titles = [
            "Late Night Drive",
            "OPM Chill Mix",
            "Study Session",
            "Rainy Day Tracks",
            "Roadtrip Sounds",
            "Soft R&B Picks",
            "Indie Waves",
            "Weekend Playlist"
        ]

        post_captions = [
            "This song has been stuck in my head all day.",
            "Current favorite track. The vibe is unreal.",
            "Anyone else into this kind of sound?",
            "This belongs in everyone’s playlist.",
            "Sharing this because it feels like a late-night drive.",
            "The vocals on this one are so clean.",
            "This track gives me calm ocean energy.",
            "Need more songs like this.",
            "Adding this to my comfort playlist.",
            "This is the kind of music I want to discover more."
        ]

        comment_texts = [
            "This is such a good pick!",
            "I love the vibe of this one.",
            "Adding this to my playlist.",
            "This sounds perfect for studying.",
            "The mood is really nice.",
            "I need more songs like this.",
            "This artist is underrated.",
            "Solid recommendation!",
            "This gives late-night vibes.",
            "I would listen to this on repeat."
        ]

        users = self.create_users(fake)
        albums = self.create_albums(users, album_titles, fake)
        tracks = self.create_tracks(users, albums, artists, song_titles, genres, fake)
        playlists = self.create_playlists(users, tracks, playlist_titles, fake)
        posts = self.create_posts(users, tracks, post_captions)
        self.create_comments(users, posts, tracks, playlists, comment_texts)

        self.stdout.write(self.style.SUCCESS("Fake data created successfully!"))
        self.stdout.write(self.style.SUCCESS("Demo password for fake users: testpass123"))

    def create_users(self, fake):
        users = []

        for number in range(10):
            username = f"alon_user_{number + 1}"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": f"{username}@example.com",
                }
            )

            if created:
                user.set_password("testpass123")
                user.save()

            users.append(user)

        return users

    def create_albums(self, users, album_titles, fake):
        albums = []

        for title in album_titles:
            owner = random.choice(users)

            album, created = Album.objects.get_or_create(
                owner=owner,
                title=title,
                defaults={
                    "description": fake.sentence(nb_words=12),
                }
            )

            albums.append(album)

        return albums

    def create_tracks(self, users, albums, artists, song_titles, genres, fake):
        tracks = []

        sample_audio_files = self.get_sample_audio_files()

        for title in song_titles:
            owner = random.choice(users)
            artist = random.choice(artists)

            track = Track.objects.create(
                owner=owner,
                album=random.choice(albums),
                title=title,
                artist_name=artist,
                genre=random.choice(genres),
                description=fake.paragraph(nb_sentences=2),
                is_public=True,
            )

            self.attach_audio_file(track, sample_audio_files, title)

            tracks.append(track)

        return tracks

    def create_playlists(self, users, tracks, playlist_titles, fake):
        playlists = []

        for title in playlist_titles:
            owner = random.choice(users)

            playlist = Playlist.objects.create(
                owner=owner,
                title=title,
                description=fake.sentence(nb_words=14),
                is_public=True,
            )

            random_tracks = random.sample(tracks, k=min(random.randint(3, 7), len(tracks)))
            playlist.tracks.set(random_tracks)
            playlist.save()

            playlists.append(playlist)

        return playlists

    def create_posts(self, users, tracks, post_captions):
        posts = []

        for caption in post_captions:
            post = MusicPost.objects.create(
                author=random.choice(users),
                caption=caption,
                track=random.choice(tracks),
            )

            posts.append(post)

        return posts

    def create_comments(self, users, posts, tracks, playlists, comment_texts):
        for _ in range(40):
            comment_type = random.choice(["text_only", "with_track", "with_playlist"])

            comment = Comment.objects.create(
                post=random.choice(posts),
                author=random.choice(users),
                text=random.choice(comment_texts),
            )

            if comment_type == "with_track":
                comment.track = random.choice(tracks)

            if comment_type == "with_playlist":
                comment.playlist = random.choice(playlists)

            comment.save()

    def get_sample_audio_files(self):
        sample_audio_folder = Path(settings.MEDIA_ROOT) / "sample_audio"

        if not sample_audio_folder.exists():
            sample_audio_folder.mkdir(parents=True, exist_ok=True)

        audio_files = list(sample_audio_folder.glob("*.mp3"))

        if not audio_files:
            self.stdout.write(
                self.style.WARNING(
                    "No sample audio found in media/sample_audio/. "
                    "Fake tracks will use placeholder audio files."
                )
            )

        return audio_files

    def attach_audio_file(self, track, sample_audio_files, title):
        safe_title = title.lower().replace(" ", "_").replace("/", "_")

        if sample_audio_files:
            selected_audio = random.choice(sample_audio_files)

            with open(selected_audio, "rb") as audio:
                track.audio_file.save(
                    f"{safe_title}.mp3",
                    File(audio),
                    save=True
                )
        else:
            track.audio_file.save(
                f"{safe_title}.mp3",
                ContentFile(b"Fake audio placeholder for ALON demo."),
                save=True
            )