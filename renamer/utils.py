from pymediainfo import MediaInfo
from .constants import META_DESCRIPTIONS
import magic
import mutagen
from collections import Counter


def get_media_tracks(file_path):
    """Extract compact media track information"""
    tracks_info = []
    try:
        media_info = MediaInfo.parse(file_path)
        video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
        audio_tracks = [t for t in media_info.tracks if t.track_type == 'Audio']
        sub_tracks = [t for t in media_info.tracks if t.track_type == 'Text']
        
        # Video tracks
        for i, v in enumerate(video_tracks[:2]):  # Up to 2 videos
            codec = getattr(v, 'format', None) or getattr(v, 'codec', None) or 'unknown'
            width = getattr(v, 'width', None) or '?'
            height = getattr(v, 'height', None) or '?'
            bitrate = getattr(v, 'bit_rate', None)
            fps = getattr(v, 'frame_rate', None)
            profile = getattr(v, 'format_profile', None)
            
            video_str = f"{codec} {width}x{height}"
            if bitrate:
                video_str += f" {bitrate}bps"
            if fps:
                video_str += f" {fps}fps"
            if profile:
                video_str += f" ({profile})"
            
            tracks_info.append(f"[green]Video {i+1}:[/green] {video_str}")
        
        # Audio tracks
        for i, a in enumerate(audio_tracks[:3]):  # Up to 3 audios
            codec = getattr(a, 'format', None) or getattr(a, 'codec', None) or 'unknown'
            channels = getattr(a, 'channel_s', None) or '?'
            lang = getattr(a, 'language', None) or 'und'
            bitrate = getattr(a, 'bit_rate', None)
            
            audio_str = f"{codec} {channels}ch {lang}"
            if bitrate:
                audio_str += f" {bitrate}bps"
            
            tracks_info.append(f"[yellow]Audio {i+1}:[/yellow] {audio_str}")
        
        # Subtitle tracks
        for i, s in enumerate(sub_tracks[:3]):  # Up to 3 subs
            lang = getattr(s, 'language', None) or 'und'
            format = getattr(s, 'format', None) or getattr(s, 'codec', None) or 'unknown'
            
            sub_str = f"{lang} ({format})"
            tracks_info.append(f"[magenta]Sub {i+1}:[/magenta] {sub_str}")
            
    except Exception as e:
        tracks_info.append(f"[red]Track info error: {str(e)}[/red]")
    
    return "\n".join(tracks_info) if tracks_info else ""


def detect_file_type(file_path):
    """Detect file type and return meta_type and desc"""
    try:
        info = mutagen.File(file_path)
        if info is None:
            # Fallback to magic
            mime = magic.from_file(str(file_path), mime=True)
            if mime == 'video/x-matroska':
                return 'Matroska', 'Matroska multimedia container'
            elif mime == 'video/mp4':
                return 'MP4', 'MPEG-4 video container'
            elif mime == 'video/x-msvideo':
                return 'AVI', 'Audio Video Interleave'
            elif mime == 'video/quicktime':
                return 'QuickTime', 'QuickTime movie'
            elif mime == 'video/x-ms-wmv':
                return 'ASF', 'Windows Media'
            elif mime == 'video/x-flv':
                return 'FLV', 'Flash Video'
            elif mime == 'video/webm':
                return 'WebM', 'WebM multimedia'
            elif mime == 'video/ogg':
                return 'Ogg', 'Ogg multimedia'
            else:
                return 'Unknown', f'Unknown MIME: {mime}'
        else:
            meta_type = type(info).__name__
            meta_desc = META_DESCRIPTIONS.get(meta_type, f'Unknown type {meta_type}')
            return meta_type, meta_desc
    except Exception as e:
        return f'Error: {str(e)}', f'Error detecting type'