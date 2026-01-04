"""Conversion service for video to MKV remux with metadata preservation.

This service manages the process of converting AVI/MPG/MPEG/WebM files to MKV container:
- Fast stream copy (no re-encoding)
- Audio language detection and mapping from filename
- Subtitle file detection and inclusion
- Metadata preservation from multiple sources
- Track order matching
"""

import logging
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from renamer.extractors.extractor import MediaExtractor


logger = logging.getLogger(__name__)


class ConversionService:
    """Service for converting video files to MKV with metadata preservation.

    This service handles:
    - Validating video files for conversion (AVI, MPG, MPEG, WebM)
    - Detecting nearby subtitle files
    - Mapping audio languages from filename to tracks
    - Building ffmpeg command for fast remux or HEVC encoding
    - Executing conversion with progress

    Example:
        service = ConversionService()

        # Check if file can be converted
        if service.can_convert(Path("/media/movie.avi")):
            success, message = service.convert_avi_to_mkv(
                Path("/media/movie.avi"),
                extractor=media_extractor
            )
    """

    # Supported subtitle extensions
    SUBTITLE_EXTENSIONS = {'.srt', '.ass', '.ssa', '.sub', '.idx'}

    def __init__(self):
        """Initialize the conversion service."""
        self.cpu_arch = self._detect_cpu_architecture()
        logger.debug(f"ConversionService initialized with CPU architecture: {self.cpu_arch}")

    def _detect_cpu_architecture(self) -> str:
        """Detect CPU architecture for optimization.

        Returns:
            Architecture string: 'x86_64', 'arm64', 'aarch64', or 'unknown'
        """
        machine = platform.machine().lower()

        # Try to get more specific CPU info
        try:
            if machine in ['x86_64', 'amd64']:
                # Check for Intel vs AMD
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    if 'intel' in cpuinfo or 'xeon' in cpuinfo:
                        return 'intel_x86_64'
                    elif 'amd' in cpuinfo:
                        return 'amd_x86_64'
                    else:
                        return 'x86_64'
            elif machine in ['arm64', 'aarch64']:
                # Check for specific ARM chips
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    if 'rk3588' in cpuinfo or 'rockchip' in cpuinfo:
                        return 'arm64_rk3588'
                    else:
                        return 'arm64'
        except Exception as e:
            logger.debug(f"Could not read /proc/cpuinfo: {e}")

        return machine

    def _get_x265_params(self, preset: str = 'medium') -> str:
        """Get optimized x265 parameters based on CPU architecture.

        Args:
            preset: Encoding preset (ultrafast, superfast, veryfast, faster, fast, medium, slow)

        Returns:
            x265 parameter string optimized for the detected CPU
        """
        # Base parameters for quality
        base_params = [
            'profile=main10',
            'level=4.1',
        ]

        # CPU-specific optimizations
        if self.cpu_arch in ['intel_x86_64', 'amd_x86_64', 'x86_64']:
            # Intel Xeon / AMD optimization
            # Enable assembly optimizations and threading
            cpu_params = [
                'pools=+',  # Enable thread pools
                'frame-threads=4',  # Parallel frame encoding (adjust based on cores)
                'lookahead-threads=2',  # Lookahead threads
                'asm=auto',  # Enable CPU-specific assembly optimizations
            ]

            # For faster encoding on servers
            if preset in ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast']:
                cpu_params.extend([
                    'ref=2',  # Fewer reference frames for speed
                    'bframes=3',  # Fewer B-frames
                    'me=1',  # Faster motion estimation (DIA)
                    'subme=1',  # Faster subpixel refinement
                    'rd=2',  # Faster RD refinement
                ])
            else:  # medium or slow
                cpu_params.extend([
                    'ref=3',
                    'bframes=4',
                    'me=2',  # HEX motion estimation
                    'subme=2',
                    'rd=3',
                ])

        elif self.cpu_arch in ['arm64_rk3588', 'arm64', 'aarch64']:
            # ARM64 / RK3588 optimization
            # RK3588 has 4x Cortex-A76 + 4x Cortex-A55
            cpu_params = [
                'pools=+',
                'frame-threads=4',  # Use big cores
                'lookahead-threads=1',  # Lighter lookahead for ARM
                'asm=auto',  # Enable NEON optimizations
            ]

            # ARM is slower, so optimize more aggressively for speed
            if preset in ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast']:
                cpu_params.extend([
                    'ref=1',  # Minimal reference frames
                    'bframes=2',
                    'me=0',  # Full search (faster on ARM)
                    'subme=0',
                    'rd=1',
                    'weightp=0',  # Disable weighted prediction for speed
                    'weightb=0',
                ])
            else:  # medium
                cpu_params.extend([
                    'ref=2',
                    'bframes=3',
                    'me=1',
                    'subme=1',
                    'rd=2',
                ])

        else:
            # Generic/unknown architecture - conservative settings
            cpu_params = [
                'pools=+',
                'frame-threads=2',
                'ref=2',
                'bframes=3',
            ]

        return ':'.join(base_params + cpu_params)

    def can_convert(self, file_path: Path) -> bool:
        """Check if a file can be converted (is AVI, MPG, MPEG, or WebM).

        Args:
            file_path: Path to the file to check

        Returns:
            True if file is AVI, MPG, MPEG, or WebM and can be converted
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        return file_path.suffix.lower() in {'.avi', '.mpg', '.mpeg', '.webm'}

    def find_subtitle_files(self, video_path: Path) -> List[Path]:
        """Find subtitle files near the video file.

        Looks for subtitle files with the same basename in the same directory.

        Args:
            video_path: Path to the video file

        Returns:
            List of Path objects for found subtitle files

        Example:
            >>> service.find_subtitle_files(Path("/media/movie.avi"))
            [Path("/media/movie.srt"), Path("/media/movie.eng.srt")]
        """
        subtitle_files = []
        base_name = video_path.stem  # filename without extension
        directory = video_path.parent

        # Look for files with same base name and subtitle extensions
        for sub_ext in self.SUBTITLE_EXTENSIONS:
            # Exact match: movie.srt
            exact_match = directory / f"{base_name}{sub_ext}"
            if exact_match.exists():
                subtitle_files.append(exact_match)

            # Pattern match: movie.eng.srt, movie.ukr.srt, etc.
            pattern_files = list(directory.glob(f"{base_name}.*{sub_ext}"))
            for sub_file in pattern_files:
                if sub_file not in subtitle_files:
                    subtitle_files.append(sub_file)

        logger.debug(f"Found {len(subtitle_files)} subtitle files for {video_path.name}")
        return subtitle_files

    def map_audio_languages(
        self,
        extractor: MediaExtractor,
        audio_track_count: int
    ) -> List[Optional[str]]:
        """Map audio languages from filename to track indices.

        Extracts audio language list from filename and maps them to tracks
        in order. If filename has fewer languages than tracks, remaining
        tracks get None.

        Args:
            extractor: MediaExtractor with filename data
            audio_track_count: Number of audio tracks in the file

        Returns:
            List of language codes (or None) for each audio track

        Example:
            >>> langs = service.map_audio_languages(extractor, 2)
            >>> print(langs)
            ['ukr', 'eng']
        """
        # Get audio_langs from filename extractor
        audio_langs_str = extractor.get('audio_langs', 'Filename')

        if not audio_langs_str:
            logger.debug("No audio languages found in filename")
            return [None] * audio_track_count

        # Split by comma and clean
        langs = [lang.strip().lower() for lang in audio_langs_str.split(',')]

        # Map to tracks (pad with None if needed)
        result = []
        for i in range(audio_track_count):
            if i < len(langs):
                result.append(langs[i])
            else:
                result.append(None)

        logger.debug(f"Mapped audio languages: {result}")
        return result

    def build_ffmpeg_command(
        self,
        source_path: Path,
        mkv_path: Path,
        audio_languages: List[Optional[str]],
        subtitle_files: List[Path],
        encode_hevc: bool = False,
        crf: int = 18,
        preset: str = 'medium'
    ) -> List[str]:
        """Build ffmpeg command for video to MKV conversion.

        Creates a command that:
        - Copies video and audio streams (no re-encoding) OR
        - Encodes video to HEVC with high quality settings
        - Sets audio language metadata
        - Includes external subtitle files
        - Sets MKV title from filename

        Args:
            source_path: Source video file (AVI, MPG, MPEG, or WebM)
            mkv_path: Destination MKV file
            audio_languages: Language codes for each audio track
            subtitle_files: List of subtitle files to include
            encode_hevc: If True, encode video to HEVC instead of copying
            crf: Constant Rate Factor for HEVC (18=visually lossless, 23=high quality default)
            preset: x265 preset (ultrafast, veryfast, faster, fast, medium, slow)

        Returns:
            List of command arguments for subprocess
        """
        cmd = ['ffmpeg']

        # Add flags to fix timestamp issues (particularly for AVI files)
        cmd.extend(['-fflags', '+genpts'])

        # Input file
        cmd.extend(['-i', str(source_path)])

        # Add subtitle files as inputs
        for sub_file in subtitle_files:
            cmd.extend(['-i', str(sub_file)])

        # Map video stream
        cmd.extend(['-map', '0:v:0'])

        # Map all audio streams
        cmd.extend(['-map', '0:a'])

        # Map subtitle streams
        for i in range(len(subtitle_files)):
            cmd.extend(['-map', f'{i+1}:s:0'])

        # Video codec settings
        if encode_hevc:
            # HEVC encoding with CPU-optimized parameters
            cmd.extend(['-c:v', 'libx265'])
            cmd.extend(['-crf', str(crf)])
            # Use specified preset
            cmd.extend(['-preset', preset])
            # 10-bit encoding for better quality (if source supports it)
            cmd.extend(['-pix_fmt', 'yuv420p10le'])
            # CPU-optimized x265 parameters
            x265_params = self._get_x265_params(preset)
            cmd.extend(['-x265-params', x265_params])
            # Copy audio streams (no audio re-encoding)
            cmd.extend(['-c:a', 'copy'])
            # Copy subtitle streams
            cmd.extend(['-c:s', 'copy'])
        else:
            # Copy all streams (no re-encoding)
            cmd.extend(['-c', 'copy'])

        # Set audio language metadata
        for i, lang in enumerate(audio_languages):
            if lang:
                cmd.extend([f'-metadata:s:a:{i}', f'language={lang}'])

        # Set title metadata from filename
        title = source_path.stem
        cmd.extend(['-metadata', f'title={title}'])

        # Output file
        cmd.append(str(mkv_path))

        logger.debug(f"Built ffmpeg command: {' '.join(cmd)}")
        return cmd

    def convert_avi_to_mkv(
        self,
        avi_path: Path,
        extractor: Optional[MediaExtractor] = None,
        output_path: Optional[Path] = None,
        dry_run: bool = False,
        encode_hevc: bool = False,
        crf: int = 18,
        preset: str = 'medium'
    ) -> Tuple[bool, str]:
        """Convert video file to MKV with metadata preservation.

        Args:
            avi_path: Source video file path (AVI, MPG, MPEG, or WebM)
            extractor: Optional MediaExtractor (creates new if None)
            output_path: Optional output path (defaults to same name with .mkv)
            dry_run: If True, build command but don't execute
            encode_hevc: If True, encode video to HEVC instead of copying
            crf: Constant Rate Factor for HEVC (18=visually lossless, 23=high quality)
            preset: x265 preset (ultrafast, veryfast, faster, fast, medium, slow)

        Returns:
            Tuple of (success, message)

        Example:
            >>> success, msg = service.convert_avi_to_mkv(
            ...     Path("/media/movie.avi"),
            ...     encode_hevc=True,
            ...     crf=18
            ... )
            >>> print(msg)
        """
        # Validate input
        if not self.can_convert(avi_path):
            error_msg = f"File is not a supported format (AVI/MPG/MPEG/WebM) or doesn't exist: {avi_path}"
            logger.error(error_msg)
            return False, error_msg

        # Create extractor if needed
        if extractor is None:
            try:
                extractor = MediaExtractor(avi_path)
            except Exception as e:
                error_msg = f"Failed to create extractor: {e}"
                logger.error(error_msg)
                return False, error_msg

        # Determine output path
        if output_path is None:
            output_path = avi_path.with_suffix('.mkv')

        # Check if output already exists
        if output_path.exists():
            error_msg = f"Output file already exists: {output_path.name}"
            logger.warning(error_msg)
            return False, error_msg

        # Get audio track count from MediaInfo
        audio_tracks = extractor.get('audio_tracks', 'MediaInfo') or []
        audio_track_count = len(audio_tracks)

        if audio_track_count == 0:
            error_msg = "No audio tracks found in file"
            logger.error(error_msg)
            return False, error_msg

        # Map audio languages
        audio_languages = self.map_audio_languages(extractor, audio_track_count)

        # Find subtitle files
        subtitle_files = self.find_subtitle_files(avi_path)

        # Build ffmpeg command
        cmd = self.build_ffmpeg_command(
            avi_path,
            output_path,
            audio_languages,
            subtitle_files,
            encode_hevc,
            crf,
            preset
        )

        # Dry run mode
        if dry_run:
            cmd_str = ' '.join(cmd)
            info_msg = f"Would convert: {avi_path.name} → {output_path.name}\n"
            info_msg += f"Audio languages: {audio_languages}\n"
            info_msg += f"Subtitles: {[s.name for s in subtitle_files]}\n"
            info_msg += f"Command: {cmd_str}"
            logger.info(info_msg)
            return True, info_msg

        # Execute conversion
        try:
            logger.info(f"Starting conversion: {avi_path.name} → {output_path.name}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                check=False  # Don't raise on non-zero exit, check file instead
            )

            # Check if conversion succeeded by verifying output file exists
            if output_path.exists() and output_path.stat().st_size > 0:
                success_msg = f"Converted successfully: {avi_path.name} → {output_path.name}"
                logger.info(success_msg)
                return True, success_msg
            else:
                # Try to decode stderr for error message
                try:
                    error_output = result.stderr.decode('utf-8', errors='replace')
                except Exception:
                    error_output = "Unknown error (could not decode ffmpeg output)"

                error_msg = f"ffmpeg conversion failed: {error_output[-500:]}"  # Last 500 chars
                logger.error(error_msg)
                return False, error_msg

        except FileNotFoundError:
            error_msg = "ffmpeg not found. Please install ffmpeg."
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Conversion failed: {e}"
            logger.error(error_msg)
            return False, error_msg
