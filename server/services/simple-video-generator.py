#!/usr/bin/env python3
"""
Enhanced video generator using FFmpeg to create videos from HTML content
with proper text decoding, visual elements, and improved styling.
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
    """Clean and format text for video display"""
    if not text:
        return ""
    
    # Decode HTML entities
    text = decode_html_entities(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    # Escape single quotes for FFmpeg
    text = text.replace("'", "\\'")
    
    return text.strip()

def generate_video_from_html(html_file_path, output_video_path, duration):
    """
    Generate an enhanced video from HTML content using FFmpeg with:
    - Proper HTML entity decoding
    - Visual elements and diagrams
    - Improved styling and layout
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
    
    main_text = ' '.join(clean_content)[:800]  # Increased text limit
    
    # Determine if this is a math-related scene
    is_math_scene = any(keyword in title.lower() for keyword in ['hopital', 'calculus', 'limit', 'derivative', 'integral'])
    
    # Choose background and styling based on content
    if is_math_scene:
        bg_color = "0x1a1a2e"  # Dark blue-purple for math
        accent_color = "0x4a90e2"  # Blue accent
        title_color = "0xffffff"  # White title
        text_color = "0xe8e8e8"  # Light gray text
    else:
        bg_color = "0x2c3e50"  # Dark blue for general
        accent_color = "0x3498db"  # Blue accent
        title_color = "0xffffff"  # White title
        text_color = "0xf8f9fa"  # Light text
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create enhanced video with multiple visual elements
        ffmpeg_filters = []
        
        # Base background
        ffmpeg_filters.append(f"color=c={bg_color}:size=1920x1080:duration={duration}")
        
        # Add gradient overlay for depth
        ffmpeg_filters.append(f"geq=r='r(X,Y)*0.9+0.1':g='g(X,Y)*0.9+0.1':b='b(X,Y)*0.9+0.1'")
        
        # Add visual elements based on content type
        if is_math_scene:
            # Add mathematical visual elements
            ffmpeg_filters.append(f"drawbox=x=100:y=200:w=1720:h=2:color={accent_color}@0.8:t=fill")
            ffmpeg_filters.append(f"drawbox=x=100:y=800:w=1720:h=2:color={accent_color}@0.8:t=fill")
            ffmpeg_filters.append(f"drawbox=x=100:y=200:w=2:h=600:color={accent_color}@0.6:t=fill")
            ffmpeg_filters.append(f"drawbox=x=1820:y=200:w=2:h=600:color={accent_color}@0.6:t=fill")
            
            # Add corner decorations
            ffmpeg_filters.append(f"drawbox=x=50:y=50:w=100:h=100:color={accent_color}@0.3:t=2")
            ffmpeg_filters.append(f"drawbox=x=1770:y=50:w=100:h=100:color={accent_color}@0.3:t=2")
            ffmpeg_filters.append(f"drawbox=x=50:y=930:w=100:h=100:color={accent_color}@0.3:t=2")
            ffmpeg_filters.append(f"drawbox=x=1770:y=930:w=100:h=100:color={accent_color}@0.3:t=2")
        
        # Add title with enhanced styling
        title_filter = (f"drawtext=text='{title}':fontcolor={title_color}:"
                       f"fontsize=72:fontfile=/System/Library/Fonts/Arial.ttf:"
                       f"x=(w-text_w)/2:y=120:"
                       f"shadowcolor=black:shadowx=2:shadowy=2")
        ffmpeg_filters.append(title_filter)
        
        # Add main content with better formatting
        if main_text:
            # Split text into lines for better readability
            words = main_text.split()
            lines = []
            current_line = ""
            max_chars_per_line = 80
            
            for word in words:
                if len(current_line + " " + word) <= max_chars_per_line:
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Limit to 6 lines for readability
            lines = lines[:6]
            
            # Add each line of text
            for i, line in enumerate(lines):
                y_pos = 300 + (i * 45)  # 45px spacing between lines
                text_filter = (f"drawtext=text='{line}':fontcolor={text_color}:"
                              f"fontsize=48:fontfile=/System/Library/Fonts/Arial.ttf:"
                              f"x=(w-text_w)/2:y={y_pos}:"
                              f"shadowcolor=black:shadowx=1:shadowy=1")
                ffmpeg_filters.append(text_filter)
        
        # Add footer with series info
        footer_text = "Educational Video Series"
        footer_filter = (f"drawtext=text='{footer_text}':fontcolor={accent_color}:"
                        f"fontsize=32:fontfile=/System/Library/Fonts/Arial.ttf:"
                        f"x=(w-text_w)/2:y=950:")
        ffmpeg_filters.append(footer_filter)
        
        # Build the complete FFmpeg command
        ffmpeg_cmd = ['ffmpeg', '-y']
        ffmpeg_cmd.extend(['-f', 'lavfi'])
        ffmpeg_cmd.extend(['-i', f'color=c={bg_color}:size=1920x1080:duration={duration}'])
        
        # Apply all filters
        filter_complex = ";".join(ffmpeg_filters)
        ffmpeg_cmd.extend(['-vf', filter_complex])
        
        ffmpeg_cmd.extend(['-c:v', 'libx264'])
        ffmpeg_cmd.extend(['-pix_fmt', 'yuv420p'])
        ffmpeg_cmd.extend(['-r', '30'])
        ffmpeg_cmd.append(output_video_path)
        
        # Execute FFmpeg command
        print(f"Generating enhanced video with FFmpeg...")
        print(f"Title: {title}")
        print(f"Content: {main_text[:100]}...")
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return False
        
        print(f"Enhanced video generated successfully: {output_video_path}")
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
