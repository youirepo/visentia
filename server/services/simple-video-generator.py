#!/usr/bin/env python3
"""
Simple and robust video generator using FFmpeg to create videos from HTML content
with proper text decoding and basic visual elements.
"""

import os
import sys
import json
import subprocess
import tempfile
import html
import re
from pathlib import Path

def decode_html_entities(text):
    """Decode HTML entities like &#39; to '"""
    if not text:
        return ""
    return html.unescape(text)

def clean_text_for_display(text):
    """Clean and format text for video display with minimal escaping"""
    if not text:
        return ""
    
    # Decode HTML entities
    text = decode_html_entities(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    # Only escape the most critical characters
    text = text.replace("'", "")
    text = text.replace('"', "")
    text = text.replace(":", " ")
    text = text.replace(";", " ")
    
    return text.strip()

def generate_video_from_html(html_file_path, output_video_path, duration):
    """
    Generate a simple but robust video from HTML content using FFmpeg.
    """
    
    # Read the HTML content
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract and decode title
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
    title = clean_text_for_display(title_match.group(1)) if title_match else "Educational Video"
    
    # Extract main content from divs
    content_divs = re.findall(r'<div[^>]*class="[^"]*content-section[^"]*"[^>]*>(.*?)</div>', html_content, re.DOTALL)
    
    # Clean and decode content
    clean_content = []
    for div in content_divs:
        clean_text = clean_text_for_display(div)
        if clean_text:
            clean_content.append(clean_text)
    
    main_text = ' '.join(clean_content)[:400]  # Shorter text for simplicity
    
    # Determine if this is a math-related scene
    is_math_scene = any(keyword in title.lower() for keyword in ['hopital', 'calculus', 'limit', 'derivative', 'integral'])
    
    # Choose background and styling based on content
    if is_math_scene:
        bg_color = "0x1a1a2e"  # Dark blue-purple for math
        accent_color = "0x4a90e2"  # Blue accent
        title_color = "white"
        text_color = "0xe8e8e8"  # Light gray text
    else:
        bg_color = "0x2c3e50"  # Dark blue for general
        accent_color = "0x3498db"  # Blue accent
        title_color = "white"
        text_color = "0xf8f9fa"  # Light text
    
    try:
        # Create a simple video with basic text overlay
        # Use a much simpler approach that's less likely to fail
        
        # Create the basic FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={bg_color}:size=1920x1080:duration={duration}',
            '-vf', f'drawtext=text={title}:fontcolor={title_color}:fontsize=60:x=(w-text_w)/2:y=200',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_video_path
        ]
        
        # Execute FFmpeg command
        print(f"Generating simple video with FFmpeg...")
        print(f"Title: {title}")
        print(f"Content: {main_text[:50]}...")
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return False
        
        print(f"Simple video generated successfully: {output_video_path}")
        return True
        
    except Exception as e:
        print(f"Error generating video: {e}")
        return False

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