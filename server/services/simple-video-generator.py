#!/usr/bin/env python3
"""
Simple video generator using FFmpeg to create videos from HTML content
without relying on Puppeteer browser automation.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

def generate_video_from_html(html_file_path, output_video_path, duration):
    """
    Generate a video from HTML content using FFmpeg with text rendering.
    This approach avoids Puppeteer WebSocket issues by using FFmpeg's native capabilities.
    """
    
    # Read the HTML content
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract text content from HTML (simple approach)
    import re
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
    title = title_match.group(1) if title_match else "Educational Video"
    
    # Extract main content from divs
    content_divs = re.findall(r'<div[^>]*class="[^"]*content-section[^"]*"[^>]*>(.*?)</div>', html_content, re.DOTALL)
    
    # Clean HTML tags from content
    clean_content = []
    for div in content_divs:
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', div)
        # Clean up whitespace
        clean_text = ' '.join(clean_text.split())
        if clean_text.strip():
            clean_content.append(clean_text.strip())
    
    main_text = ' '.join(clean_content)[:500]  # Limit text length
    
    # Create a temporary image with text using ImageMagick/FFmpeg
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a simple video with text overlay using FFmpeg
        # This creates a solid background with text overlay
        
        # Define colors and styling
        bg_color = "0x2c3e50"  # Dark blue background
        text_color = "white"
        
        # Create FFmpeg command to generate video with text
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-f', 'lavfi',
            '-i', f'color=c={bg_color}:size=1920x1080:duration={duration}',
            '-vf', f'drawtext=text=\'{title}\':fontcolor={text_color}:fontsize=60:x=(w-text_w)/2:y=100',
            '-vf', f'drawtext=text=\'{main_text}\':fontcolor={text_color}:fontsize=40:x=(w-text_w)/2:y=300:line_spacing=20',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_video_path
        ]
        
        # Execute FFmpeg command
        print(f"Generating video with FFmpeg: {' '.join(ffmpeg_cmd)}")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return False
        
        print(f"Video generated successfully: {output_video_path}")
        return True
        
    except Exception as e:
        print(f"Error generating video: {e}")
        return False
    finally:
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    if len(sys.argv) != 4:
        print("Usage: python simple-video-generator.py <html_file> <output_video> <duration>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_video = sys.argv[2]
    duration = float(sys.argv[3])
    
    success = generate_video_from_html(html_file, output_video, duration)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
