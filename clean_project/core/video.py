#!/usr/bin/env python3
"""
Video generation module for the CloneIA project.
"""
import os
import random
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import moviepy.editor as mp
    from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from core.utils import (
    ensure_directory, get_timestamp_filename,
    PROJECT_ROOT, OUTPUT_DIR, RESOURCES_DIR,
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS,
    BG_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR
)
from core.text import TextProcessor

logger = logging.getLogger('cloneia.video')

class VideoGenerator:
    """
    Class for generating videos from audio and images.
    """
    
    def __init__(self):
        """
        Initialize the video generator.
        """
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy library not found. Video generation will not work.")
        
        # Directories
        self.output_dir = os.path.join(OUTPUT_DIR, "videos")
        self.resources_dir = RESOURCES_DIR
        self.reference_dir = os.path.join(PROJECT_ROOT, "reference", "videos")
        
        # Ensure directories exist
        for directory in [self.output_dir, self.resources_dir, self.reference_dir]:
            ensure_directory(directory)
        
        # Video settings
        self.video_width = VIDEO_WIDTH
        self.video_height = VIDEO_HEIGHT
        self.fps = FPS
        
        # Colors
        self.bg_color = BG_COLOR
        self.text_color = TEXT_COLOR
        self.highlight_color = HIGHLIGHT_COLOR
        
        # Text processor
        self.text_processor = TextProcessor()
        
        logger.info("VideoGenerator initialized")
    
    def create_title_image(self, title: str, width: int = VIDEO_WIDTH, 
                          height: int = VIDEO_HEIGHT) -> np.ndarray:
        """
        Create an image with the video title.
        
        Args:
            title: Title of the video
            width: Width of the image
            height: Height of the image
            
        Returns:
            np.ndarray: NumPy array representing the image
        """
        # Create a black background image
        img = Image.new('RGB', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load a custom font, or use the default
        try:
            font_path = os.path.join(self.resources_dir, "fonts", "Roboto-Bold.ttf")
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 80)
                subtitle_font = ImageFont.truetype(font_path, 60)
            else:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
        except Exception as e:
            logger.error(f"Error loading font: {e}")
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add the title
        title_text = "RAPIDINHA NO CRIPTO"
        title_width = draw.textlength(title_text, font=title_font)
        title_position = ((width - title_width) // 2, height // 3)
        draw.text(title_position, title_text, font=title_font, fill=self.highlight_color)
        
        # Add the subtitle (news)
        # Break the title into lines if it's too long
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if draw.textlength(test_line, font=subtitle_font) < width * 0.8:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw the subtitle lines
        y_position = height // 2
        for line in lines:
            line_width = draw.textlength(line, font=subtitle_font)
            line_position = ((width - line_width) // 2, y_position)
            draw.text(line_position, line, font=subtitle_font, fill=self.text_color)
            y_position += 70
        
        # Convert to NumPy array
        return np.array(img)
    
    def create_text_clip(self, text: str, duration: float, 
                        position: Union[str, Tuple[str, str]] = 'center', 
                        fontsize: int = 60) -> TextClip:
        """
        Create a text clip.
        
        Args:
            text: Text to display
            duration: Duration of the clip in seconds
            position: Position of the text
            fontsize: Font size
            
        Returns:
            TextClip: Text clip
        """
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy library not found. Cannot create text clip.")
            return None
        
        try:
            font_path = os.path.join(self.resources_dir, "fonts", "Roboto-Regular.ttf")
            if os.path.exists(font_path):
                text_clip = TextClip(text, fontsize=fontsize, color='white', font=font_path)
            else:
                text_clip = TextClip(text, fontsize=fontsize, color='white')
            
            text_clip = text_clip.set_position(position).set_duration(duration)
            return text_clip
        except Exception as e:
            logger.error(f"Error creating text clip: {e}")
            # Fallback to a color clip with the same duration
            return ColorClip(size=(100, 100), color=(0, 0, 0), duration=duration)
    
    def extract_frame_from_video(self, video_path: str, 
                                time_point: Optional[float] = None) -> np.ndarray:
        """
        Extract a frame from a video.
        
        Args:
            video_path: Path to the video
            time_point: Time point to extract the frame (if None, uses a random point)
            
        Returns:
            np.ndarray: NumPy array representing the frame
        """
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy library not found. Cannot extract frame.")
            return np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
        
        try:
            video = mp.VideoFileClip(video_path)
            
            if time_point is None:
                time_point = random.uniform(0, max(0.1, video.duration - 0.1))
            
            frame = video.get_frame(time_point)
            video.close()
            
            return frame
        except Exception as e:
            logger.error(f"Error extracting frame from video {video_path}: {e}")
            # Return a black frame as fallback
            return np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
    
    def create_intro_animation(self, duration: float = 3.0) -> CompositeVideoClip:
        """
        Create an intro animation for the video.
        
        Args:
            duration: Duration of the intro in seconds
            
        Returns:
            CompositeVideoClip: Video clip with the intro animation
        """
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy library not found. Cannot create intro animation.")
            return None
        
        try:
            # Create a black background
            bg_clip = ColorClip(
                size=(self.video_width, self.video_height),
                color=self.bg_color,
                duration=duration
            )
            
            # Create the title text
            title_text = "RAPIDINHA NO CRIPTO"
            title_clip = TextClip(
                title_text,
                fontsize=80,
                color=self.highlight_color,
                font='Arial-Bold' if os.path.exists('/Library/Fonts/Arial Bold.ttf') else None
            )
            
            # Animate the title (fade in and zoom)
            title_clip = title_clip.set_position('center').set_duration(duration)
            title_clip = title_clip.crossfadein(1.0)
            
            # Create the subtitle
            subtitle_text = "com Renato Santanna Silva"
            subtitle_clip = TextClip(
                subtitle_text,
                fontsize=40,
                color='white',
                font='Arial' if os.path.exists('/Library/Fonts/Arial.ttf') else None
            )
            
            # Animate the subtitle (appear after the title)
            subtitle_clip = subtitle_clip.set_position(('center', self.video_height // 2 + 80)).set_duration(duration - 0.5)
            subtitle_clip = subtitle_clip.set_start(0.5)  # Start after 0.5 seconds
            subtitle_clip = subtitle_clip.crossfadein(0.5)
            
            # Combine the clips
            intro_clip = CompositeVideoClip([bg_clip, title_clip, subtitle_clip])
            
            # Add a fade out transition at the end
            intro_clip = intro_clip.crossfadeout(0.5)
            
            return intro_clip
        except Exception as e:
            logger.error(f"Error creating intro animation: {e}")
            # Return a black clip as fallback
            return ColorClip(
                size=(self.video_width, self.video_height),
                color=self.bg_color,
                duration=duration
            )
    
    def generate_video_from_script(self, script_path: str, audio_path: Optional[str] = None, 
                                  output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a video from a script and audio.
        
        This method creates a professional video for the "Rapidinha no Cripto" segment,
        using frames from reference videos, smooth transitions, and graphic elements
        such as titles, captions, and visual effects.
        
        Args:
            script_path: Path to the script file
            audio_path: Path to the audio file (if None, generates a name based on the script)
            output_path: Path to save the video (if None, generates a name based on timestamp)
            
        Returns:
            Optional[str]: Path to the generated video, or None if failed
        """
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy library not found. Cannot generate video.")
            return None
        
        try:
            # Check if the script exists
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return None
            
            # Read the script
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check if the audio exists
            if audio_path and not os.path.exists(audio_path):
                logger.error(f"Audio not found: {audio_path}")
                audio_path = None
            
            # Generate output path if not provided
            if not output_path:
                filename = get_timestamp_filename("rapidinha", "mp4")
                output_path = os.path.join(self.output_dir, filename)
            
            # Parse the script
            parsed_script = self.text_processor.parse_script(script_content)
            intro_text = parsed_script['intro']
            news_items = parsed_script['news']
            outro_text = parsed_script['outro']
            
            # Find reference videos
            reference_videos = []
            for filename in os.listdir(self.reference_dir):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    reference_videos.append(os.path.join(self.reference_dir, filename))
            
            if not reference_videos:
                logger.error("No reference videos found.")
                return None
            
            # Estimated total duration (will be adjusted based on audio)
            total_duration = 180  # 3 minutes by default
            
            # If we have audio, use its duration
            if audio_path:
                audio = mp.AudioFileClip(audio_path)
                total_duration = audio.duration
                audio.close()
            
            # Duration of each section
            intro_animation_duration = 3.0  # Fixed duration for the intro animation
            intro_duration = total_duration * 0.1
            news_duration = total_duration * 0.8 / max(1, len(news_items))
            outro_duration = total_duration * 0.1
            
            # Create clips for each section
            clips = []
            
            # Add intro animation
            intro_animation = self.create_intro_animation(duration=intro_animation_duration)
            clips.append(intro_animation)
            
            # Create intro clip with script content
            if intro_text:
                intro_frame = self.extract_frame_from_video(random.choice(reference_videos))
                intro_clip = mp.ImageClip(intro_frame).set_duration(intro_duration)
                
                # Add intro text
                intro_text_clip = self.create_text_clip(
                    intro_text,
                    intro_duration,
                    position=('center', 'center'),
                    fontsize=70
                )
                
                intro_clip = CompositeVideoClip([intro_clip, intro_text_clip])
                intro_clip = intro_clip.crossfadein(0.5)  # Add fade in
                clips.append(intro_clip)
            
            # Create clips for each news item
            for i, news in enumerate(news_items):
                # Extract title and content
                title = news['title']
                content = news['content']
                
                # Create title image with news number
                numbered_title = f"{i+1}. {title}"
                title_image = self.create_title_image(numbered_title)
                title_clip = mp.ImageClip(title_image).set_duration(news_duration * 0.3)
                
                # Add fade in transition for the title
                title_clip = title_clip.crossfadein(0.5)
                
                # Extract a frame from the reference video for the content
                # Try to use a different frame for each news item
                if len(reference_videos) > i:
                    video_for_content = reference_videos[i]
                else:
                    video_for_content = random.choice(reference_videos)
                
                content_frame = self.extract_frame_from_video(video_for_content)
                
                # Apply a darkening effect to the frame to improve text readability
                darkened_frame = content_frame * 0.7  # Reduce brightness to 70%
                content_clip = mp.ImageClip(darkened_frame).set_duration(news_duration * 0.7)
                
                # Add content text with improved style
                content_text_clip = self.create_text_clip(
                    content,
                    news_duration * 0.7,
                    position=('center', 'center'),
                    fontsize=60
                )
                
                # Add a semi-transparent rectangle behind the text to improve readability
                text_bg = ColorClip(
                    size=(self.video_width * 0.9, self.video_height * 0.4),
                    color=(0, 0, 0, 0.5),  # Black with 50% transparency
                    duration=news_duration * 0.7
                ).set_position('center')
                
                # Combine the elements
                content_clip = CompositeVideoClip([content_clip, text_bg, content_text_clip])
                
                # Add transition between title and content
                content_clip = content_clip.crossfadein(0.5)
                
                # Add the clips
                clips.append(title_clip)
                clips.append(content_clip)
            
            # Create outro clip
            if outro_text:
                outro_frame = self.extract_frame_from_video(random.choice(reference_videos))
                
                # Apply a darkening effect to the frame
                darkened_outro_frame = outro_frame * 0.7
                outro_clip = mp.ImageClip(darkened_outro_frame).set_duration(outro_duration)
                
                # Add outro text
                outro_text_clip = self.create_text_clip(
                    outro_text,
                    outro_duration,
                    position=('center', 'center'),
                    fontsize=70
                )
                
                # Add a semi-transparent rectangle behind the text
                outro_bg = ColorClip(
                    size=(self.video_width * 0.9, self.video_height * 0.3),
                    color=(0, 0, 0, 0.5),
                    duration=outro_duration
                ).set_position('center')
                
                outro_clip = CompositeVideoClip([outro_clip, outro_bg, outro_text_clip])
                
                # Add fade in transition
                outro_clip = outro_clip.crossfadein(0.5)
                
                clips.append(outro_clip)
            
            # Add a final screen with credits
            credits_duration = 3.0
            credits_clip = ColorClip(
                size=(self.video_width, self.video_height),
                color=self.bg_color,
                duration=credits_duration
            )
            
            # Add credits text
            credits_text = "Gerado por Clone IA\nRapidinha no Cripto\n\n© " + datetime.now().strftime("%Y")
            credits_text_clip = self.create_text_clip(
                credits_text,
                credits_duration,
                position=('center', 'center'),
                fontsize=50
            )
            
            credits_clip = CompositeVideoClip([credits_clip, credits_text_clip])
            
            # Add fade in transition
            credits_clip = credits_clip.crossfadein(0.5)
            
            clips.append(credits_clip)
            
            # Concatenate all clips
            final_clip = mp.concatenate_videoclips(clips)
            
            # Add audio if available
            if audio_path:
                audio = mp.AudioFileClip(audio_path)
                final_clip = final_clip.set_audio(audio)
            
            # Set final resolution
            final_clip = final_clip.resize(height=self.video_height, width=self.video_width)
            
            # Save the video
            logger.info(f"Generating video: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=self.fps,
                threads=4,
                preset='medium'
            )
            
            logger.info(f"Video generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return None
    
    def create_simple_video(self, script_path: str, audio_path: Optional[str] = None, 
                           output_path: Optional[str] = None) -> Optional[str]:
        """
        Create a simple video with text on a colored background.
        
        Args:
            script_path: Path to the script file
            audio_path: Path to the audio file
            output_path: Path to save the video
            
        Returns:
            Optional[str]: Path to the generated video, or None if failed
        """
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy library not found. Cannot create video.")
            return None
        
        try:
            # Check if the script exists
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return None
            
            # Read the script
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Generate output path if not provided
            if not output_path:
                filename = get_timestamp_filename("simple_video", "mp4")
                output_path = os.path.join(self.output_dir, filename)
            
            # Create a background clip
            bg_clip = ColorClip(
                size=(self.video_width, self.video_height),
                color=self.bg_color,
                duration=60  # Default duration, will be adjusted
            )
            
            # Create a text clip
            text_clip = self.create_text_clip(
                script_content,
                60,  # Default duration, will be adjusted
                position=('center', 'center'),
                fontsize=60
            )
            
            # Combine the clips
            video_clip = CompositeVideoClip([bg_clip, text_clip])
            
            # If we have audio, use its duration and add it to the video
            if audio_path and os.path.exists(audio_path):
                audio = mp.AudioFileClip(audio_path)
                video_clip = video_clip.set_duration(audio.duration)
                video_clip = video_clip.set_audio(audio)
            else:
                # Default duration
                video_clip = video_clip.set_duration(60)
            
            # Save the video
            logger.info(f"Generating simple video: {output_path}")
            video_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=self.fps,
                threads=4,
                preset='medium'
            )
            
            logger.info(f"Simple video generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating simple video: {e}")
            return None
    
    def generate_video_for_heygen(self, script_path: str, audio_path: Optional[str] = None, 
                                 output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a video suitable for HeyGen.
        
        Args:
            script_path: Path to the script file
            audio_path: Path to the audio file
            output_path: Path to save the video
            
        Returns:
            Optional[str]: Path to the generated video, or None if failed
        """
        # This is a simplified version that just creates a basic video
        # In a real implementation, you would customize this for HeyGen's requirements
        return self.create_simple_video(script_path, audio_path, output_path)
