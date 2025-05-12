#!/usr/bin/env python3
"""
Offline testing tool for the CloneIA project.
"""
import os
import sys
import json
import argparse
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import (
    load_voice_config, open_audio_file, ensure_directory,
    get_timestamp_filename, PROJECT_ROOT, OUTPUT_DIR
)
from core.text import TextProcessor

logger = logging.getLogger('cloneia.tools.offline_tester')

class OfflineTester:
    """
    Class for testing the CloneIA project without making API calls.
    """

    def __init__(self):
        """
        Initialize the offline tester.
        """
        # Directories
        self.audio_dir = os.path.join(OUTPUT_DIR, "audio")
        self.video_dir = os.path.join(OUTPUT_DIR, "videos")
        self.text_dir = os.path.join(OUTPUT_DIR, "text")

        # Ensure directories exist
        for directory in [self.audio_dir, self.video_dir, self.text_dir]:
            ensure_directory(directory)

        # Text processor
        self.text_processor = TextProcessor()

        logger.info("OfflineTester initialized")

    def simulate_audio_generation(self, text: str, profile_name: Optional[str] = None) -> Optional[str]:
        """
        Simulate audio generation.

        Args:
            text: Text to generate audio for
            profile_name: Name of the voice profile to use

        Returns:
            Optional[str]: Path to the simulated audio file
        """
        # Optimize the text
        optimized_text = self.text_processor.optimize_for_speech(text)

        # Load voice configuration
        config = load_voice_config(profile_name)

        if not config:
            print("Error: Voice configuration not found.")
            return None

        # Generate a timestamp for the file
        filename = get_timestamp_filename("simulated_audio", "mp3")
        output_path = os.path.join(self.audio_dir, filename)

        # Copy an existing audio file (if available)
        sample_audio = None
        samples_dir = os.path.join(PROJECT_ROOT, "reference", "samples")

        if os.path.exists(samples_dir):
            audio_files = [f for f in os.listdir(samples_dir) if f.endswith('.mp3') or f.endswith('.wav')]
            if audio_files:
                sample_audio = os.path.join(samples_dir, audio_files[0])

        if sample_audio and os.path.exists(sample_audio):
            shutil.copy2(sample_audio, output_path)
            print(f"Sample audio file copied to: {output_path}")
        else:
            # Create a text file with the content that would be generated
            text_path = os.path.join(self.text_dir, filename.replace('.mp3', '.txt'))
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"Original text:\n{text}\n\nOptimized text:\n{optimized_text}")

            print(f"Simulated text file created: {text_path}")

        # Display information
        print("\n=== Audio Generation Simulation ===")
        print(f"Profile: {config.get('voice_name')} (ID: {config.get('voice_id')})")
        print(f"Settings: {json.dumps(config.get('settings', {}), indent=2)}")
        print(f"Original text: {text[:100]}...")
        print(f"Optimized text: {optimized_text[:100]}...")
        print(f"Simulated audio file: {output_path}")

        return output_path

    def simulate_video_generation(self, audio_path: str) -> Optional[str]:
        """
        Simulate video generation.

        Args:
            audio_path: Path to the audio file

        Returns:
            Optional[str]: Path to the simulated video file
        """
        # Generate a timestamp for the file
        filename = get_timestamp_filename("simulated_video", "mp4")
        output_path = os.path.join(self.video_dir, filename)

        # Display information
        print("\n=== Video Generation Simulation ===")
        print(f"Audio: {audio_path}")
        print(f"Avatar: 01cbe2535df5453a97f4a872ea532b33 (Flukaku Rapidinha)")
        print(f"Folder: augment")
        print(f"Simulated video file: {output_path}")

        return output_path

    def test_text_optimization(self, text: str, output_file: Optional[str] = None) -> str:
        """
        Test text optimization.

        Args:
            text: Text to optimize
            output_file: Path to save the optimized text

        Returns:
            str: Optimized text
        """
        # Optimize the text
        optimized_text = self.text_processor.optimize_for_speech(text)

        # Display result
        print("\n=== Original Text ===")
        print(text)

        print("\n=== Optimized Text ===")
        print(optimized_text)

        # Save result
        if output_file:
            output_path = output_file
        else:
            # Generate a timestamp for the file
            filename = get_timestamp_filename("optimized_text", "txt")
            output_path = os.path.join(self.text_dir, filename)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=== Original Text ===\n")
                f.write(text)
                f.write("\n\n=== Optimized Text ===\n")
                f.write(optimized_text)

            print(f"\nResult saved to: {output_path}")
        except Exception as e:
            print(f"Error saving result: {e}")

        return optimized_text

    def test_full_flow(self, text: str, profile_name: Optional[str] = None) -> Dict[str, str]:
        """
        Test the full flow (text optimization, audio generation, video generation).

        Args:
            text: Text to process
            profile_name: Name of the voice profile to use

        Returns:
            Dict[str, str]: Paths to the generated files
        """
        # Step 1: Optimize the text
        print("\n=== Step 1: Text Optimization ===")
        optimized_text = self.text_processor.optimize_for_speech(text)

        # Step 2: Simulate audio generation
        print("\n=== Step 2: Audio Generation ===")
        audio_path = self.simulate_audio_generation(optimized_text, profile_name)

        # Step 3: Simulate video generation
        print("\n=== Step 3: Video Generation ===")
        video_path = self.simulate_video_generation(audio_path)

        # Summary
        print("\n=== Simulation Summary ===")
        print(f"Text: {text[:50]}...")
        print(f"Profile: {profile_name or 'default (mix)'}")
        print(f"Simulated audio: {audio_path}")
        print(f"Simulated video: {video_path}")
        print("\nNo ElevenLabs credits were consumed in this simulation.")

        return {
            "text": text,
            "optimized_text": optimized_text,
            "audio_path": audio_path,
            "video_path": video_path
        }

def main():
    parser = argparse.ArgumentParser(description="Offline testing tool for CloneIA")
    parser.add_argument("--text", help="Text to process")
    parser.add_argument("--file", help="Path to a text file to process")
    parser.add_argument("--profile", help="Name of the voice profile to use")
    parser.add_argument("--optimize-only", action="store_true", help="Only test text optimization")
    parser.add_argument("--output", help="Path to save the output")
    parser.add_argument("--open", action="store_true", help="Open the generated file")

    args = parser.parse_args()

    # Get the text
    text = args.text
    if args.file and os.path.exists(args.file):
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Text loaded from file: {args.file}")
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    if not text:
        text = """E aí cambada! Tô de volta com mais uma Rapidinha Cripto!

Hoje vamos falar sobre o Bitcoin, que tá dando um show no mercado. Depois de quebrar a resistência dos 60 mil dólares, o BTC continua subindo e já tá mirando os 70 mil!

O que tá impulsionando essa alta? Primeiro, os ETFs de Bitcoin nos Estados Unidos continuam atraindo bilhões em investimentos. É dinheiro institucional entrando forte no mercado.

É isso cambada! Se gostou, deixa o like e compartilha com a galera. Até a próxima Rapidinha Cripto!"""

    # Create the tester
    tester = OfflineTester()

    # Run the test
    if args.optimize_only:
        result = tester.test_text_optimization(text, args.output)
    else:
        result = tester.test_full_flow(text, args.profile)

        # Open the generated file if requested
        if args.open and result.get("audio_path") and os.path.exists(result["audio_path"]):
            open_audio_file(result["audio_path"])

if __name__ == "__main__":
    main()
