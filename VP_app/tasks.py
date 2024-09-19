import subprocess
from django.conf import settings
from celery import shared_task
from .models import Video, Subtitle
from datetime import datetime
import os
from django.utils.text import slugify

@shared_task(name='VP_app.tasks.extract_subtitles', ignore_result=False) 
def extract_subtitles(video_id):
   
    video = Video.objects.get(id=video_id)
    video_path = video.video_file.path
    output_srt_path = f'{video_path}.srt'

    # Command to extract subtitles using FFmpeg
    command = ['ffmpeg', '-i', video_path, '-map', '0:s:0', output_srt_path]

    # Execute the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error: {result.stderr.decode('utf-8')}")

    # Read the SRT file and store subtitles
    with open(output_srt_path, 'r', encoding='utf-8') as srt_file:
        timestamp = 0.0
        subtitle_text = ''
        for line in srt_file:
            if line.strip().isdigit():
                if subtitle_text:
                    Subtitle.objects.create(
                        video=video,
                        subtitle_text=subtitle_text,
                        timestamp=timestamp
                    )
                    subtitle_text = ''
            elif '-->' in line:
                try:
                    start_time_str = line.split('-->')[0].strip()
                    start_time_obj = datetime.strptime(start_time_str, '%H:%M:%S,%f')
                    timestamp = start_time_obj.hour * 3600 + start_time_obj.minute * 60 + start_time_obj.second + start_time_obj.microsecond / 1e6
                except ValueError as e:
                    print(f"Error parsing timestamp: {e}")
                    continue 
            else:
                subtitle_text += f'{line.strip()} '


@shared_task(name='VP_app.tasks.process_video')
def process_video(video_id):
    try:
        video = Video.objects.get(id=video_id)
        video_path = video.video_file.path
        output_vtt_path = f'{os.path.splitext(video_path)[0]}.vtt'

        # Convert the subtitles from SRT or extract from the video and convert to VTT
        command = ['ffmpeg', '-i', video_path, '-map', '0:s:0', output_vtt_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise Exception(f"Error extracting subtitles: {result.stderr.decode('utf-8')}")

        print(f"Subtitles extracted and saved as: {output_vtt_path}")

    except Video.DoesNotExist:
        print(f"Video with ID {video_id} does not exist.")
    except Exception as e:
        print(f"Error during video processing: {str(e)}")
