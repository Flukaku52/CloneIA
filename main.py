#!/usr/bin/env python3
"""
Main entry point for the CloneIA project.
"""
import os
import argparse
import logging
from typing import Dict, Optional

from core.utils import (
    load_api_key, open_audio_file,
    ensure_directory, get_timestamp_filename,
    PROJECT_ROOT, OUTPUT_DIR
)
from core.text import TextProcessor
from core.audio import AudioGenerator
from core.video import VideoGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'cloneia.log'))
    ]
)
logger = logging.getLogger('cloneia.main')

class CloneIA:
    """
    Main class for the CloneIA project.
    """

    def __init__(self, api_key: Optional[str] = None, voice_profile: Optional[str] = None):
        """
        Initialize the CloneIA.

        Args:
            api_key: ElevenLabs API key (if None, will try to load from environment)
            voice_profile: Name of the voice profile to use (if None, will use default)
        """
        # API key
        self.api_key = api_key or load_api_key()

        # Directories
        self.output_dir = OUTPUT_DIR
        self.audio_dir = os.path.join(self.output_dir, "audio")
        self.video_dir = os.path.join(self.output_dir, "videos")
        self.text_dir = os.path.join(self.output_dir, "text")

        # Ensure directories exist
        for directory in [self.output_dir, self.audio_dir, self.video_dir, self.text_dir]:
            ensure_directory(directory)

        # Components
        self.text_processor = TextProcessor()
        self.audio_generator = AudioGenerator(self.api_key, voice_profile)
        self.video_generator = VideoGenerator()

        logger.info("CloneIA initialized")

    def generate_rapidinha(self, text: str, output_prefix: Optional[str] = None,
                          optimize_text: bool = True, generate_video: bool = True,
                          dry_run: bool = False) -> Dict[str, str]:
        """
        Generate a complete "Rapidinha Cripto" segment.

        Args:
            text: Text content for the segment
            output_prefix: Prefix for output files (if None, uses timestamp)
            optimize_text: Whether to optimize the text for speech
            generate_video: Whether to generate a video
            dry_run: If True, simulates the generation without making API calls

        Returns:
            Dict[str, str]: Paths to the generated files
        """
        # Generate output prefix if not provided
        if not output_prefix:
            timestamp = get_timestamp_filename("rapidinha", "")
            output_prefix = timestamp.rstrip(".")

        # Step 1: Save the original text
        text_path = os.path.join(self.text_dir, f"{output_prefix}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)

        logger.info(f"Text saved to: {text_path}")

        # Step 2: Optimize the text (if requested)
        if optimize_text:
            optimized_text = self.text_processor.optimize_for_speech(text)

            # Save the optimized text
            optimized_path = os.path.join(self.text_dir, f"{output_prefix}_optimized.txt")
            with open(optimized_path, 'w', encoding='utf-8') as f:
                f.write(optimized_text)

            logger.info(f"Optimized text saved to: {optimized_path}")
        else:
            optimized_text = text

        # Step 3: Generate audio
        audio_path = os.path.join(self.audio_dir, f"{output_prefix}.mp3")
        audio_result = self.audio_generator.generate_audio(
            optimized_text, audio_path, optimize=False, dry_run=dry_run
        )

        if not audio_result:
            logger.error("Audio generation failed")
            return {
                "text": text_path,
                "optimized": optimized_path if optimize_text else None,
                "audio": None,
                "video": None
            }

        logger.info(f"Audio generated: {audio_result}")

        # Step 4: Generate video (if requested)
        video_path = None
        if generate_video and not dry_run:
            video_path = os.path.join(self.video_dir, f"{output_prefix}.mp4")
            video_result = self.video_generator.create_simple_video(
                text_path, audio_result, video_path
            )

            if video_result:
                logger.info(f"Video generated: {video_result}")
            else:
                logger.error("Video generation failed")

        return {
            "text": text_path,
            "optimized": optimized_path if optimize_text else None,
            "audio": audio_result,
            "video": video_path
        }

    def generate_from_script(self, script_path: str, output_prefix: Optional[str] = None,
                            optimize_text: bool = True, generate_video: bool = True,
                            dry_run: bool = False) -> Dict[str, str]:
        """
        Generate a complete "Rapidinha Cripto" segment from a script file.

        Args:
            script_path: Path to the script file
            output_prefix: Prefix for output files (if None, uses timestamp)
            optimize_text: Whether to optimize the text for speech
            generate_video: Whether to generate a video
            dry_run: If True, simulates the generation without making API calls

        Returns:
            Dict[str, str]: Paths to the generated files
        """
        # Check if the script exists
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            return {}

        # Read the script
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # Generate from the script content
        return self.generate_rapidinha(
            script_content, output_prefix, optimize_text, generate_video, dry_run
        )

    def generate_for_heygen(self, text: str, output_prefix: Optional[str] = None,
                           optimize_text: bool = True, generate_video: bool = False,
                           avatar_id: Optional[str] = None, folder_name: str = "augment",
                           dry_run: bool = False) -> Dict[str, str]:
        """
        Generate audio and video using HeyGen.

        Args:
            text: Text content for the segment
            output_prefix: Prefix for output files (if None, uses timestamp)
            optimize_text: Whether to optimize the text for speech
            generate_video: Whether to generate a video with HeyGen
            avatar_id: ID of the avatar to use (if None, uses the configured avatar)
            folder_name: Name of the folder in HeyGen to save the video
            dry_run: If True, simulates the generation without making API calls

        Returns:
            Dict[str, str]: Paths to the generated files
        """
        # Generate output prefix if not provided
        if not output_prefix:
            timestamp = get_timestamp_filename("heygen", "")
            output_prefix = timestamp.rstrip(".")

        # Step 1: Save the original text
        text_path = os.path.join(self.text_dir, f"{output_prefix}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)

        logger.info(f"Text saved to: {text_path}")

        # Step 2: Optimize the text (if requested)
        if optimize_text:
            optimized_text = self.text_processor.optimize_for_speech(text)

            # Save the optimized text
            optimized_path = os.path.join(self.text_dir, f"{output_prefix}_optimized.txt")
            with open(optimized_path, 'w', encoding='utf-8') as f:
                f.write(optimized_text)

            logger.info(f"Optimized text saved to: {optimized_path}")
        else:
            optimized_text = text

        # Step 3: Generate audio
        audio_path = os.path.join(self.audio_dir, f"{output_prefix}.mp3")
        audio_result = self.audio_generator.generate_audio(
            optimized_text, audio_path, optimize=False, dry_run=dry_run
        )

        if not audio_result:
            logger.error("Audio generation failed")
            return {
                "text": text_path,
                "optimized": optimized_path if optimize_text else None,
                "audio": None
            }

        logger.info(f"Audio generated: {audio_result}")

        # Step 4: Generate video with HeyGen or prepare instructions
        video_result = None
        if generate_video and not dry_run:
            try:
                # Import the HeyGen video generator
                from gerar_video_heygen import generate_heygen_video

                # Generate the video
                video_path = os.path.join(self.video_dir, f"{output_prefix}.mp4")
                video_result = generate_heygen_video(
                    audio_path=audio_result,
                    script_path=text_path,
                    output_path=video_path,
                    avatar_id=avatar_id,
                    folder_name=folder_name
                )

                if video_result:
                    logger.info(f"HeyGen video generated: {video_result}")
                else:
                    logger.error("HeyGen video generation failed")
            except Exception as e:
                logger.error(f"Error generating HeyGen video: {e}")
        else:
            # Prepare HeyGen instructions
            heygen_path = os.path.join(self.text_dir, f"{output_prefix}_heygen.txt")
            with open(heygen_path, 'w', encoding='utf-8') as f:
                f.write("=== HeyGen Instructions ===\n\n")
                f.write("1. Go to HeyGen (https://www.heygen.com/)\n")
                f.write("2. Create a new video in the 'augment' folder\n")
                f.write("3. Select your custom avatar\n")
                f.write("4. Upload the audio file as the voice source\n")
                f.write("5. Generate the video\n")
                f.write("6. Download the video and edit as needed\n\n")
                f.write(f"Audio file: {audio_result}\n")

            logger.info(f"HeyGen instructions saved to: {heygen_path}")

        return {
            "text": text_path,
            "optimized": optimized_path if optimize_text else None,
            "audio": audio_result,
            "video": video_result,
            "heygen_instructions": None if generate_video else heygen_path
        }

def main():
    parser = argparse.ArgumentParser(description="CloneIA - AI Clone for Rapidinha Cripto")
    parser.add_argument("--text", help="Text content for the segment")
    parser.add_argument("--script", help="Path to a script file")
    parser.add_argument("--output", help="Prefix for output files")
    parser.add_argument("--profile", help="Name of the voice profile to use")
    parser.add_argument("--no-optimize", action="store_true", help="Disable text optimization")
    parser.add_argument("--no-video", action="store_true", help="Disable video generation")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making API calls")
    parser.add_argument("--heygen", action="store_true", help="Use HeyGen for video generation")
    parser.add_argument("--heygen-auto", action="store_true", help="Automatically generate HeyGen video")
    parser.add_argument("--avatar", help="ID of the avatar to use for HeyGen")
    parser.add_argument("--folder", default="augment", help="Name of the folder in HeyGen to save the video")
    parser.add_argument("--open", action="store_true", help="Open the generated audio file")

    args = parser.parse_args()

    # Create the CloneIA instance
    clone = CloneIA(voice_profile=args.profile)

    # Get the text content
    text = args.text
    if args.script and os.path.exists(args.script):
        with open(args.script, 'r', encoding='utf-8') as f:
            text = f.read()

    if not text:
        text = """E aí cambada! Tô de volta com mais uma Rapidinha Cripto!

Hoje vamos falar sobre o Bitcoin, que tá dando um show no mercado. Depois de quebrar a resistência dos 60 mil dólares, o BTC continua subindo e já tá mirando os 70 mil!

O que tá impulsionando essa alta? Primeiro, os ETFs de Bitcoin nos Estados Unidos continuam atraindo bilhões em investimentos. É dinheiro institucional entrando forte no mercado.

É isso cambada! Se gostou, deixa o like e compartilha com a galera. Até a próxima Rapidinha Cripto!"""

    # Generate the content
    if args.heygen or args.heygen_auto:
        result = clone.generate_for_heygen(
            text,
            args.output,
            not args.no_optimize,
            args.heygen_auto,  # Automatically generate video if --heygen-auto is specified
            args.avatar,
            args.folder,
            args.dry_run
        )
    else:
        result = clone.generate_rapidinha(
            text,
            args.output,
            not args.no_optimize,
            not args.no_video,
            args.dry_run
        )

    # Open the generated audio file if requested
    if args.open and result.get("audio") and os.path.exists(result["audio"]):
        open_audio_file(result["audio"])

    # Open the generated video file if requested
    if args.open and result.get("video") and os.path.exists(result["video"]):
        try:
            open_audio_file(result["video"])  # This function can also open videos
        except Exception as e:
            logger.error(f"Error opening video file: {e}")

if __name__ == "__main__":
    main()
