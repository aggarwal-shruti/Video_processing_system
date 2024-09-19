from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View, DetailView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Video, Subtitle
from .forms import VideoUploadForm
from .tasks import *
import time
import os


class VideoUploadView(CreateView):
    model = Video
    form_class = VideoUploadForm
    template_name = 'upload.html'
    success_url = reverse_lazy('video_list')

    def form_valid(self, form):
        
        video = form.save()
        extract_subtitles.delay(video.id)
        process_video.delay(video.id)  # Asynchronously process the video
        time.sleep(5)
        return super().form_valid(form)


class VideoListView(ListView):
    model = Video
    template_name = 'video_list.html'
    context_object_name = 'videos'
    

class VideoDetailView(DetailView):
    model = Video
    template_name = 'video_detail.html'
    context_object_name = 'video'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        
        subtitle_file_path = os.path.splitext(video.video_file.path)[0] + '.vtt'
        
        if os.path.exists(subtitle_file_path):
            # Add the subtitle URL to the context
            subtitle_url = os.path.join(settings.MEDIA_URL, 'videos', os.path.basename(subtitle_file_path))
            context['subtitle_url'] = subtitle_url
        else:
            context['subtitle_url'] = None
        
        return context


class SearchSubtitlesView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        video_id = request.GET.get('video_id', None)
        results = []

        if query and video_id:
            try:
                # Fetch the video object
                video = Video.objects.get(id=video_id)
                
                # Search case-insensitive in the subtitle text, but only for the specific video
                subtitles = Subtitle.objects.filter(video=video, subtitle_text__icontains=query)
                
                for subtitle in subtitles:
                    results.append({
                        'video_title': subtitle.video.title,
                        'timestamp': subtitle.timestamp,
                        'subtitle_text': subtitle.subtitle_text,
                    })
            except Video.DoesNotExist:
                return JsonResponse({"error": "Video not found"}, status=404)

        return JsonResponse(results, safe=False)


