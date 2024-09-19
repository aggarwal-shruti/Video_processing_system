from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Subtitle(models.Model):
    video = models.ForeignKey(Video, related_name='subtitles', on_delete=models.CASCADE)
    subtitle_text = models.TextField()
    language = models.CharField(max_length=10, default='en')
    timestamp = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.video.title}-{self.timestamp}"