"""Conversion service for AVI to MKV remux with metadata preservation.

This service manages the process of converting AVI files to MKV container:
- Fast stream copy (no re-encoding)
- Audio language detection and mapping from filename
- Subtitle file detection and inclusion
- Metadata preservation from multiple sources
- Track order matching
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from renamer.extractors.extractor import MediaExtractor


logger = logging.getLogger(__name__)


class ConversionService:
    """Service for converting AVI files to MKV with metadata preservation.

    This service handles:
    - Validating AVI files for conversion
    - Detecting nearby subtitle files
    - Mapping audio languages from filename to tracks
    - Building ffmpeg command for fast remux
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
        logger.debug("ConversionService initialized")

    def can_convert(self, file_path: Path) -> bool:
        """Check if a file can be converted (is AVI).

        Args:
            file_path: Path to the file to check

        Returns:
            True if file is AVI and can be converted
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        return file_path.suffix.lower() == '.avi'

    def find_subtitle_files(self, avi_path: Path) -> List[Path]:
        """Find subtitle files near the AVI file.

        Looks for subtitle files with the same basename in the same directory.

        Args:
            avi_path: Path to the AVI file

        Returns:
            List of Path objects for found subtitle files

        Example:
            >>> service.find_subtitle_files(Path("/media/movie.avi"))
            [Path("/media/movie.srt"), Path("/media/movie.eng.srt")]
        """
        subtitle_files = []
        base_name = avi_path.stem  # filename without extension
        directory = avi_path.parent

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

        logger.debug(f"Found {len(subtitle_files)} subtitle files for {avi_path.name}")
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
        avi_path: Path,
        mkv_path: Path,
        audio_languages: List[Optional[str]],
        subtitle_files: List[Path]
    ) -> List[str]:
        """Build ffmpeg command for AVI to MKV conversion.

        Creates a command that:
        - Copies video and audio streams (no re-encoding)
        - Sets audio language metadata
        - Includes external subtitle files
        - Sets MKV title from filename

        Args:
            avi_path: Source AVI file
            mkv_path: Destination MKV file
            audio_languages: Language codes for each audio track
            subtitle_files: List of subtitle files to include

        Returns:
            List of command arguments for subprocess
        """
        cmd = ['ffmpeg']

        # Add flags to fix timestamp issues in AVI files
        cmd.extend(['-fflags', '+genpts'])

        # Input file
        cmd.extend(['-i', str(avi_path)])

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

        # Copy codecs (no re-encoding)
        cmd.extend(['-c', 'copy'])

        # Set audio language metadata
        for i, lang in enumerate(audio_languages):
            if lang:
                cmd.extend([f'-metadata:s:a:{i}', f'language={lang}'])

        # Set title metadata from filename
        title = avi_path.stem
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
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """Convert AVI file to MKV with metadata preservation.

        Args:
            avi_path: Source AVI file path
            extractor: Optional MediaExtractor (creates new if None)
            output_path: Optional output path (defaults to same name with .mkv)
            dry_run: If True, build command but don't execute

        Returns:
            Tuple of (success, message)

        Example:
            >>> success, msg = service.convert_avi_to_mkv(
            ...     Path("/media/movie.avi")
            ... )
            >>> print(msg)
        """
        # Validate input
        if not self.can_convert(avi_path):
            error_msg = f"File is not AVI or doesn't exist: {avi_path}"
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
            subtitle_files
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
