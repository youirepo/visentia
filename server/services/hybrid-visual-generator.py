#!/usr/bin/env python3
"""
Hybrid Visual Generator for Educational Videos
Replaces Manim with a more stable approach using:
- Reveal.js for structured slides
- Mermaid.js for diagrams
- KaTeX for math expressions
- Matplotlib for graphs
- SVG + GSAP for animations
"""

import os
import sys
import json
import re
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from jinja2 import Template, Environment, FileSystemLoader
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from PIL import Image
import base64
import io

@dataclass
class SceneContent:
    """Represents the parsed content for a single scene"""
    scene_number: int
    title: str
    description: str
    duration: float
    math_content: List[str]
    diagram_content: List[str]
    graph_content: List[Dict[str, Any]]
    animation_content: List[Dict[str, Any]]
    text_content: List[str]
    highlights: List[Dict[str, Any]]

@dataclass
class SeriesInfo:
    """Represents series metadata"""
    title: str
    subject: str
    difficulty_level: str
    style: str

class ContentParser:
    """Parses scene text to detect and extract different content types"""
    
    def __init__(self):
        # Math patterns
        self.math_patterns = [
            r'\$\$.*?\$\$',  # Block math
            r'\$.*?\$',      # Inline math
            r'\\\(.*?\\\)',  # LaTeX inline
            r'\\\[.*?\\\]',  # LaTeX block
        ]
        
        # Diagram patterns
        self.diagram_keywords = [
            'flowchart', 'diagram', 'chart', 'graph', 'tree', 'timeline',
            'venn', 'sequence', 'class', 'state', 'gitgraph', 'pie'
        ]
        
        # Graph patterns
        self.graph_keywords = [
            'plot', 'graph', 'function', 'curve', 'data', 'coordinates',
            'equation', 'derivative', 'integral', 'limit'
        ]
    
    def parse_scene(self, scene_text: str, scene_number: int, title: str, 
                   description: str, duration: float) -> SceneContent:
        """Parse scene text and extract different content types"""
        
        # Extract math content
        math_content = self._extract_math(scene_text)
        
        # Extract diagram content
        diagram_content = self._extract_diagrams(scene_text)
        
        # Extract graph content
        graph_content = self._extract_graphs(scene_text)
        
        # Extract animation content
        animation_content = self._extract_animations(scene_text)
        
        # Extract text content (remaining text after other extractions)
        text_content = self._extract_text_content(scene_text, math_content, diagram_content)
        
        # Extract highlights
        highlights = self._extract_highlights(scene_text)
        
        return SceneContent(
            scene_number=scene_number,
            title=title,
            description=description,
            duration=duration,
            math_content=math_content,
            diagram_content=diagram_content,
            graph_content=graph_content,
            animation_content=animation_content,
            text_content=text_content,
            highlights=highlights
        )
    
    def _extract_math(self, text: str) -> List[str]:
        """Extract mathematical expressions from text"""
        math_expressions = []
        
        for pattern in self.math_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            math_expressions.extend(matches)
        
        return math_expressions
    
    def _extract_diagrams(self, text: str) -> List[str]:
        """Extract Mermaid diagram definitions from text"""
        diagrams = []
        
        # Look for mermaid code blocks
        mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
        matches = re.findall(mermaid_pattern, text, re.DOTALL | re.IGNORECASE)
        diagrams.extend(matches)
        
        # Look for flowchart keywords and generate basic diagrams
        for keyword in self.diagram_keywords:
            if keyword in text.lower():
                # Generate a basic diagram based on context
                diagram = self._generate_basic_diagram(text, keyword)
                if diagram:
                    diagrams.append(diagram)
        
        return diagrams
    
    def _extract_graphs(self, text: str) -> List[Dict[str, Any]]:
        """Extract graph definitions and data from text"""
        graphs = []
        
        # Look for graph keywords
        for keyword in self.graph_keywords:
            if keyword in text.lower():
                graph_config = self._generate_graph_config(text, keyword)
                if graph_config:
                    graphs.append(graph_config)
        
        return graphs
    
    def _extract_animations(self, text: str) -> List[Dict[str, Any]]:
        """Extract animation specifications from text"""
        animations = []
        
        # Look for animation keywords
        animation_keywords = ['animate', 'move', 'highlight', 'fade', 'slide', 'rotate']
        
        for keyword in animation_keywords:
            if keyword in text.lower():
                animation_config = self._generate_animation_config(text, keyword)
                if animation_config:
                    animations.append(animation_config)
        
        return animations
    
    def _extract_text_content(self, text: str, math_content: List[str], 
                             diagram_content: List[str]) -> List[str]:
        """Extract remaining text content after removing math and diagrams"""
        # Remove math expressions
        cleaned_text = text
        for math_expr in math_content:
            cleaned_text = cleaned_text.replace(math_expr, '')
        
        # Remove diagram blocks
        cleaned_text = re.sub(r'```mermaid\s*\n.*?\n```', '', cleaned_text, flags=re.DOTALL | re.IGNORECASE)
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
        
        return paragraphs
    
    def _extract_highlights(self, text: str) -> List[Dict[str, Any]]:
        """Extract highlight specifications from text"""
        highlights = []
        
        # Look for highlight markers
        highlight_pattern = r'<highlight target="([^"]*)" duration="([^"]*)" repeat="([^"]*)" delay="([^"]*)"'
        matches = re.findall(highlight_pattern, text)
        
        for match in matches:
            highlights.append({
                'target': match[0],
                'duration': float(match[1]),
                'repeat': int(match[2]),
                'delay': float(match[3])
            })
        
        return highlights
    
    def _generate_basic_diagram(self, text: str, keyword: str) -> Optional[str]:
        """Generate a basic Mermaid diagram based on context"""
        if keyword == 'flowchart':
            return """
            graph TD
                A[Start] --> B[Process]
                B --> C[Decision]
                C -->|Yes| D[End]
                C -->|No| B
            """
        elif keyword == 'venn':
            return """
            graph LR
                A[Set A] 
                B[Set B]
                C[Intersection]
                A -.-> C
                B -.-> C
            """
        return None
    
    def _generate_graph_config(self, text: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Generate graph configuration based on context"""
        if keyword == 'function':
            # Simple function plot
            return {
                'type': 'function',
                'function': 'x**2',
                'range': [-5, 5],
                'color': '#3498db',
                'title': 'Function Plot'
            }
        elif keyword == 'data':
            # Simple data plot
            x_data = np.linspace(0, 10, 50)
            y_data = np.sin(x_data) + np.random.normal(0, 0.1, 50)
            
            return {
                'type': 'scatter',
                'data': [{'x': x, 'y': y} for x, y in zip(x_data, y_data)],
                'color': '#e74c3c',
                'title': 'Data Plot'
            }
        
        return None
    
    def _generate_animation_config(self, text: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Generate animation configuration based on context"""
        if keyword == 'highlight':
            return {
                'type': 'highlight',
                'target': '.content-section',
                'duration': 2.0,
                'color': '#ffeb3b'
            }
        elif keyword == 'fade':
            return {
                'type': 'fade',
                'target': '.content-section',
                'duration': 1.5,
                'direction': 'in'
            }
        
        return None

class HybridVisualGenerator:
    """Main class for generating hybrid visual content"""
    
    def __init__(self, output_dir: str = "server/generated-scenes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader('server/templates'),
            autoescape=True
        )
        
        self.content_parser = ContentParser()
    
    async def generate_scene_html(self, scene_content: SceneContent, 
                                series_info: SeriesInfo) -> str:
        """Generate HTML file for a single scene"""
        
        # Load template
        template = self.jinja_env.get_template('scene-template.html')
        
        # Render template
        html_content = template.render(
            scene=asdict(scene_content),
            series=asdict(series_info)
        )
        
        # Save HTML file
        html_filename = f"scene-{scene_content.scene_number:02d}-{self._sanitize_filename(scene_content.title)}.html"
        html_path = self.output_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_path)
    
    async def generate_scene_video(self, html_path: str, duration: float, 
                                 output_path: str) -> str:
        """Generate video from HTML scene using Puppeteer"""
        
        # Create Puppeteer script
        puppeteer_script = f"""
        const puppeteer = require('puppeteer');
        
        async function captureScene() {{
            const browser = await puppeteer.launch({{
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            }});
            
            const page = await browser.newPage();
            
            // Set viewport to match video dimensions
            await page.setViewport({{
                width: 1920,
                height: 1080,
                deviceScaleFactor: 1
            }});
            
            // Load the HTML file
            await page.goto('file://{html_path}', {{
                waitUntil: 'networkidle0'
            }});
            
            // Wait for scene to be ready
            await page.waitForFunction(() => window.sceneReady === true, {{
                timeout: 30000
            }});
            
            // Capture video using page.screencast
            const outputPath = '{output_path}';
            await page.screencast({{
                path: outputPath,
                format: 'mp4',
                everyNthFrame: 1
            }});
            
            // Wait for the scene duration
            await page.waitForTimeout({int(duration * 1000)});
            
            await browser.close();
            console.log('Video captured:', outputPath);
        }}
        
        captureScene().catch(console.error);
        """
        
        # Write Puppeteer script to temporary file
        script_path = self.output_dir / f"capture-{Path(html_path).stem}.js"
        with open(script_path, 'w') as f:
            f.write(puppeteer_script)
        
        # Run Puppeteer
        try:
            result = subprocess.run([
                'node', str(script_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                raise Exception(f"Puppeteer failed: {result.stderr}")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Video capture timed out")
        except Exception as e:
            raise Exception(f"Video capture failed: {str(e)}")
        finally:
            # Clean up script file
            if script_path.exists():
                script_path.unlink()
    
    async def generate_matplotlib_graph(self, graph_config: Dict[str, Any], 
                                      output_path: str) -> str:
        """Generate matplotlib graph and save as image"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if graph_config['type'] == 'function':
            x = np.linspace(graph_config['range'][0], graph_config['range'][1], 1000)
            y = eval(graph_config['function'])
            ax.plot(x, y, color=graph_config.get('color', '#3498db'), linewidth=3)
            ax.set_title(graph_config.get('title', 'Function Plot'), fontsize=16)
            
        elif graph_config['type'] == 'scatter':
            data = graph_config['data']
            x_vals = [point['x'] for point in data]
            y_vals = [point['y'] for point in data]
            ax.scatter(x_vals, y_vals, color=graph_config.get('color', '#e74c3c'), s=50)
            ax.set_title(graph_config.get('title', 'Data Plot'), fontsize=16)
        
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        
        # Save as PNG
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        return re.sub(r'[^\w\s-]', '', filename).strip()
    
    async def process_scenes(self, scenes_data: List[Dict[str, Any]], 
                           series_info: SeriesInfo) -> List[str]:
        """Process multiple scenes and generate HTML files"""
        
        generated_files = []
        
        for scene_data in scenes_data:
            # Parse scene content
            scene_content = self.content_parser.parse_scene(
                scene_text=scene_data.get('narration', ''),
                scene_number=scene_data.get('sceneNumber', 0),
                title=scene_data.get('title', 'Untitled'),
                description=scene_data.get('description', ''),
                duration=scene_data.get('duration', 30.0)
            )
            
            # Generate HTML
            html_path = await self.generate_scene_html(scene_content, series_info)
            generated_files.append(html_path)
            
            print(f"Generated HTML for scene {scene_content.scene_number}: {scene_content.title}")
        
        return generated_files

# CLI usage
async def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python hybrid-visual-generator.py <scene-data.json> <series-data.json> <output-dir>")
        print("Example: python hybrid-visual-generator.py scene-data.json series-data.json ./output")
        sys.exit(1)
    
    scene_data_path = sys.argv[1]
    series_data_path = sys.argv[2]
    output_dir = sys.argv[3]
    
    # Load scene data
    with open(scene_data_path, 'r') as f:
        scene_data = json.load(f)
    
    # Load series data
    with open(series_data_path, 'r') as f:
        series_data = json.load(f)
    
    # Create series info
    series_info = SeriesInfo(**series_data)
    
    # Initialize generator
    generator = HybridVisualGenerator(output_dir)
    
    # Process single scene
    scene_content = generator.content_parser.parse_scene(
        scene_text=scene_data.get('narration', ''),
        scene_number=scene_data.get('sceneNumber', 0),
        title=scene_data.get('title', 'Untitled'),
        description=scene_data.get('description', ''),
        duration=scene_data.get('duration', 30.0)
    )
    
    # Generate HTML
    html_path = await generator.generate_scene_html(scene_content, series_info)
    
    print(f"Generated HTML: {html_path}")

# Example usage function
async def example():
    """Example usage of the HybridVisualGenerator"""
    
    # Sample scene data
    sample_scenes = [
        {
            "sceneNumber": 1,
            "title": "Introduction to Fractions",
            "description": "Understanding what fractions represent",
            "narration": "A fraction represents a part of a whole. When we have $\\frac{1}{4}$, we have one part out of four equal parts.",
            "duration": 15.5
        },
        {
            "sceneNumber": 2,
            "title": "Fraction Visualization",
            "description": "Visual representation of fractions",
            "narration": "Let's visualize fractions using a pie chart. ```mermaid\npie title Fraction Visualization\n    \"1/4\" : 1\n    \"3/4\" : 3\n```",
            "duration": 20.0
        }
    ]
    
    series_info = SeriesInfo(
        title="Understanding Fractions",
        subject="Mathematics",
        difficulty_level="Beginner",
        style="Visual and Demonstrative"
    )
    
    # Initialize generator
    generator = HybridVisualGenerator()
    
    # Process scenes
    html_files = await generator.process_scenes(sample_scenes, series_info)
    
    print(f"Generated {len(html_files)} HTML files:")
    for html_file in html_files:
        print(f"  - {html_file}")

if __name__ == "__main__":
    asyncio.run(main())
