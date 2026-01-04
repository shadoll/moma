class TrackFormatter:
    """Class to format track information into display strings"""

    @staticmethod
    def format_video_track(track: dict) -> str:
        """Format a video track dict into a display string"""
        codec = track.get('codec', 'unknown')
        width = track.get('width', '?')
        height = track.get('height', '?')
        bitrate = track.get('bitrate') # in bps
        bitrate_kbps = bitrate / 1024 if bitrate else None
        fps = track.get('fps')
        profile = track.get('profile')

        video_str = f"{codec} {width}x{height}"
        if bitrate_kbps:
            video_str += f" {bitrate_kbps}kbps"
        if fps:
            video_str += f" {fps}fps"
        if profile:
            video_str += f" ({profile})"

        return video_str

    @staticmethod
    def format_audio_track(track: dict) -> str:
        """Format an audio track dict into a display string"""
        codec = track.get('codec', 'unknown')
        channels = track.get('channels', '?')
        lang = track.get('language', 'und')
        bitrate = track.get('bitrate') # in bps
        bitrate_kbps = bitrate / 1024 if bitrate else None

        audio_str = f"{codec} {channels}ch {lang}"
        if bitrate_kbps:
            audio_str += f" {bitrate_kbps}kbps"
        return audio_str

    @staticmethod
    def format_subtitle_track(track: dict) -> str:
        """Format a subtitle track dict into a display string"""
        lang = track.get('language', 'und')
        format = track.get('format', 'unknown')

        return f"{lang} ({format})"
