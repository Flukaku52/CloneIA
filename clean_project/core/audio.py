#!/usr/bin/env python3
"""
Audio generation module for the CloneIA project.
"""
import os
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Any, Union

from core.utils import (
    load_elevenlabs_api_key, load_voice_config, save_voice_config,
    DEFAULT_VOICE_SETTINGS, ensure_directory, get_timestamp_filename,
    PROJECT_ROOT, OUTPUT_DIR
)
from core.text import optimize_text

logger = logging.getLogger('cloneia.audio')

class AudioGenerator:
    """
    Class for generating audio from text using the ElevenLabs API.
    """

    def __init__(self, api_key: Optional[str] = None, voice_profile: Optional[str] = None):
        """
        Initialize the audio generator.

        Args:
            api_key: ElevenLabs API key (if None, will try to load from environment)
            voice_profile: Name of the voice profile to use (if None, will use default)
        """
        # API key
        self.api_key = api_key or load_elevenlabs_api_key()

        # Directory for storing generated audio
        self.audio_dir = os.path.join(OUTPUT_DIR, "audio")
        ensure_directory(self.audio_dir)

        # Voice settings
        self.voice_settings = DEFAULT_VOICE_SETTINGS.copy()

        # Load voice configuration
        self.voice_id = None
        self.voice_name = "Rapidinha Voice"
        self._load_voice_config(voice_profile)

        logger.info(f"AudioGenerator initialized with voice: {self.voice_name} (ID: {self.voice_id})")

    def _load_voice_config(self, profile_name: Optional[str] = None) -> None:
        """
        Load voice configuration from file.

        Args:
            profile_name: Name of the voice profile to load
        """
        config = load_voice_config(profile_name)

        if config:
            self.voice_id = config.get("voice_id")
            self.voice_name = config.get("voice_name", "Rapidinha Voice")

            # Load advanced settings if available
            if "settings" in config:
                self.voice_settings.update(config["settings"])
                logger.info(f"Advanced settings loaded: {self.voice_settings}")

            logger.info(f"Voice configuration loaded. ID: {self.voice_id}, Name: {self.voice_name}")

    def generate_audio(self, text: str, output_path: Optional[str] = None,
                      optimize: bool = True, dry_run: bool = False) -> Optional[str]:
        """
        Generate audio from text using the ElevenLabs API.

        Args:
            text: Text to convert to audio
            output_path: Path to save the audio file (if None, generates a name based on timestamp)
            optimize: Whether to optimize the text for speech
            dry_run: If True, simulates the generation without making API calls

        Returns:
            Optional[str]: Path to the generated audio file, or None if failed
        """
        if not self.api_key and not dry_run:
            logger.error("ElevenLabs API key not configured. Cannot generate audio.")
            return None

        # Optimize text if requested
        if optimize:
            original_text = text
            text = optimize_text(text)
            logger.info(f"Text optimized: {len(original_text)} chars -> {len(text)} chars")

        # Generate output path if not provided
        if not output_path:
            filename = get_timestamp_filename("rapidinha_audio", "mp3")
            output_path = os.path.join(self.audio_dir, filename)

        # Simulation mode
        if dry_run:
            logger.info(f"[DRY RUN] Would generate audio for text: '{text[:50]}...'")
            logger.info(f"[DRY RUN] Would save to: {output_path}")
            logger.info(f"[DRY RUN] Would use voice: {self.voice_name} (ID: {self.voice_id})")
            logger.info(f"[DRY RUN] Settings: {json.dumps(self.voice_settings, indent=2)}")
            return output_path

        try:
            # Check if we have a configured voice
            voice_identifier = self.voice_id if self.voice_id else "Rachel"

            # Prepare the API request
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_identifier}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }

            data = {
                "text": text,
                "model_id": self.voice_settings.get("model_id", "eleven_multilingual_v2"),
                "voice_settings": self.voice_settings
            }

            # Make the API request
            logger.info(f"Generating audio for text: '{text[:50]}...'")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()

            # Save the audio
            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Audio generated successfully: {output_path}")
            return output_path

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return None

    def clone_voice(self, audio_files: List[str], voice_name: str = "Rapidinha Voice",
                   dry_run: bool = False) -> Optional[str]:
        """
        Clone a voice from audio files.

        Args:
            audio_files: List of paths to audio files
            voice_name: Name of the voice to create
            dry_run: If True, simulates the cloning without making API calls

        Returns:
            Optional[str]: ID of the cloned voice, or None if failed
        """
        if not self.api_key and not dry_run:
            logger.error("ElevenLabs API key not configured. Cannot clone voice.")
            return None

        # Verify valid audio files
        valid_files = [f for f in audio_files if os.path.exists(f)]

        if not valid_files:
            logger.error("No valid audio files found.")
            return None

        logger.info(f"Cloning voice from {len(valid_files)} audio files...")

        # Simulation mode
        if dry_run:
            logger.info(f"[DRY RUN] Would clone voice '{voice_name}' from {len(valid_files)} files")
            logger.info(f"[DRY RUN] Files: {valid_files[:5]}{'...' if len(valid_files) > 5 else ''}")

            # Create a simulated voice ID
            import hashlib
            simulated_id = hashlib.md5(voice_name.encode()).hexdigest()[:24]

            # Save a simulated configuration
            voice_config = {
                "voice_id": simulated_id,
                "voice_name": voice_name,
                "settings": self.voice_settings
            }

            save_voice_config(voice_config)

            logger.info(f"[DRY RUN] Simulated voice ID: {simulated_id}")
            return simulated_id

        try:
            # Prepare files for upload
            files = []
            for audio_file in valid_files:
                with open(audio_file, 'rb') as f:
                    files.append(('files', (os.path.basename(audio_file), f.read(), 'audio/mpeg')))

            # Make the API request
            url = "https://api.elevenlabs.io/v1/voices/add"
            headers = {"xi-api-key": self.api_key}
            data = {
                "name": voice_name,
                "description": "Cloned voice for Rapidinha Cripto"
            }

            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()

            # Process the response
            result = response.json()
            voice_id = result.get("voice_id")

            if voice_id:
                logger.info(f"Voice cloned successfully! ID: {voice_id}")

                # Update voice ID and name
                self.voice_id = voice_id
                self.voice_name = voice_name

                # Save voice configuration
                voice_config = {
                    "voice_id": voice_id,
                    "voice_name": voice_name,
                    "settings": self.voice_settings
                }

                save_voice_config(voice_config)

                return voice_id
            else:
                logger.error("Failed to clone voice. No voice ID returned.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error cloning voice: {e}")
            return None

    def extract_audio_samples(self, video_dir: str, output_dir: Optional[str] = None,
                             max_samples: int = 5, max_duration: int = 30) -> List[str]:
        """
        Extract audio samples from videos for voice cloning.

        Args:
            video_dir: Directory containing videos
            output_dir: Directory to save audio samples (if None, uses default)
            max_samples: Maximum number of samples to extract
            max_duration: Maximum duration of each sample in seconds

        Returns:
            List[str]: List of paths to extracted audio files
        """
        try:
            import moviepy.editor as mp
        except ImportError:
            logger.error("Error: moviepy library not found. Install moviepy.")
            return []

        # Directory for storing samples
        if not output_dir:
            output_dir = os.path.join(PROJECT_ROOT, "reference", "voice_samples")

        ensure_directory(output_dir)

        try:
            # List all videos in the directory
            video_files = []
            for filename in os.listdir(video_dir):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    video_files.append(os.path.join(video_dir, filename))

            if not video_files:
                logger.warning("No videos found in the directory.")
                return []

            # Limit the number of videos
            video_files = video_files[:max_samples]

            # Extract audio samples
            audio_samples = []
            for i, video_file in enumerate(video_files):
                try:
                    # Extract audio from video
                    video = mp.VideoFileClip(video_file)

                    # Limit duration
                    if video.duration > max_duration:
                        video = video.subclip(0, max_duration)

                    # Save audio
                    audio_path = os.path.join(output_dir, f"sample_{i+1}.mp3")
                    video.audio.write_audiofile(audio_path, codec='mp3')

                    # Add to list of samples
                    audio_samples.append(audio_path)

                    # Close video
                    video.close()

                except Exception as e:
                    logger.error(f"Error extracting audio from video {video_file}: {e}")

            logger.info(f"Extracted {len(audio_samples)} audio samples for voice cloning.")
            return audio_samples

        except Exception as e:
            logger.error(f"Error extracting audio samples: {e}")
            return []

    def extract_short_samples(self, source_dir: str, output_dir: Optional[str] = None,
                             min_duration: float = 7.0, max_duration: float = 12.0,
                             num_samples: int = 40) -> List[str]:
        """
        Extract short audio samples from longer audio files.

        Args:
            source_dir: Directory containing source audio files
            output_dir: Directory to save short samples (if None, uses default)
            min_duration: Minimum duration of each sample in seconds
            max_duration: Maximum duration of each sample in seconds
            num_samples: Number of samples to extract

        Returns:
            List[str]: List of paths to extracted audio files
        """
        try:
            import moviepy.editor as mp
        except ImportError:
            logger.error("Error: moviepy library not found. Install moviepy.")
            return []

        # Directory for storing samples
        if not output_dir:
            output_dir = os.path.join(PROJECT_ROOT, "reference", "samples", "short_samples")

        ensure_directory(output_dir)

        try:
            # List all audio files in the directory
            audio_files = []
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.mp3', '.wav', '.m4a')):
                    audio_files.append(os.path.join(source_dir, filename))

            if not audio_files:
                logger.warning("No audio files found in the directory.")
                return []

            # Extract short samples
            short_samples = []
            sample_count = 0

            for audio_file in audio_files:
                if sample_count >= num_samples:
                    break

                try:
                    # Load audio file
                    audio = mp.AudioFileClip(audio_file)

                    # Skip if too short
                    if audio.duration < min_duration:
                        continue

                    # Determine number of samples to extract from this file
                    file_samples = min(3, num_samples - sample_count)

                    for i in range(file_samples):
                        # Determine start time (avoid the first and last 1 second)
                        max_start = max(0, audio.duration - max_duration - 1)
                        if max_start <= 1:
                            start_time = 1
                        else:
                            start_time = 1 + (i * max_start / file_samples)

                        # Determine end time
                        end_time = min(start_time + max_duration, audio.duration - 1)

                        # Ensure minimum duration
                        if end_time - start_time < min_duration:
                            continue

                        # Extract sample
                        sample = audio.subclip(start_time, end_time)

                        # Save sample
                        sample_path = os.path.join(output_dir, f"short_sample_{sample_count+1}.mp3")
                        sample.write_audiofile(sample_path, codec='mp3')

                        # Add to list of samples
                        short_samples.append(sample_path)
                        sample_count += 1

                    # Close audio
                    audio.close()

                except Exception as e:
                    logger.error(f"Error extracting short sample from {audio_file}: {e}")

            # Create a report
            report = {
                "total_samples": len(short_samples),
                "min_duration": min_duration,
                "max_duration": max_duration,
                "samples": [
                    {
                        "path": sample,
                        "duration": mp.AudioFileClip(sample).duration
                    }
                    for sample in short_samples
                ]
            }

            report_path = os.path.join(output_dir, "duration_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"Extracted {len(short_samples)} short audio samples.")
            return short_samples

        except Exception as e:
            logger.error(f"Error extracting short samples: {e}")
            return []
