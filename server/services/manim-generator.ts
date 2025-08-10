import OpenAI from "openai";

const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY || "default_key" 
});

export interface ManimScene {
  sceneName: string;
  code: string;
  duration: number;
}

export interface ManimFile {
  fileName: string;
  filePath: string;
  fullCode: string;
}

// Fallback function to create simple, working Manim code
function createFallbackManimCode(script: string, episodeTitle: string): ManimScene {
  // Clean and split the script into manageable chunks
  const cleanScript = script.replace(/[^\w\s.,!?-]/g, '').trim();
  const sentences = cleanScript.split(/[.!?]+/).filter(s => s.trim().length > 10);
  
  // Use more sentences for longer content - take up to 12 sentences
  const selectedSentences = sentences.slice(0, Math.min(12, sentences.length));
  const chunks = selectedSentences.map(s => s.trim());
  
  const sceneCode = `class ${episodeTitle.replace(/[^a-zA-Z0-9]/g, '')}Scene(Scene):
    def construct(self):
        # Title
        title = Text("${episodeTitle}", font_size=36, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)
        
        # Content sections
        ${chunks.map((chunk, index) => {
          const text = chunk.replace(/"/g, '\\"').replace(/\n/g, '\\n');
          if (index === 0) {
            return `# Section ${index + 1}
        section${index + 1} = Text("${text}", font_size=18, color=YELLOW, line_spacing=0.8)
        section${index + 1}.move_to(ORIGIN)
        section${index + 1}.scale_to_fit_width(12)  # Scale to fit screen width
        self.play(FadeIn(section${index + 1}), FadeOut(title))
        self.wait(8)
        self.play(FadeOut(section${index + 1}))`;
          } else {
            return `# Section ${index + 1}
        section${index + 1} = Text("${text}", font_size=18, color=YELLOW, line_spacing=0.8)
        section${index + 1}.move_to(ORIGIN)
        section${index + 1}.scale_to_fit_width(12)  # Scale to fit screen width
        self.play(FadeIn(section${index + 1}))
        self.wait(8)
        self.play(FadeOut(section${index + 1}))`;
          }
        }).join('\n        ')}
        
        # Conclusion
        conclusion = Text("Thank you for learning about ${episodeTitle.split(':')[0]}!", font_size=28, color=GREEN)
        conclusion.move_to(ORIGIN)
        self.play(FadeIn(conclusion))
        self.wait(3)
        
        # Fade out conclusion at the end
        self.play(FadeOut(conclusion))`;
  
  return {
    sceneName: `${episodeTitle.replace(/[^a-zA-Z0-9]/g, '')}Scene`,
    code: sceneCode,
    duration: chunks.length * 8 + 5 // 8 seconds per chunk + 5 seconds for title and conclusion
  };
}

export async function generateManimCode(
  script: string,
  episodeTitle: string,
  targetDuration: string
): Promise<ManimScene> {
  // For now, always use fallback to ensure working videos
  console.log(`Using fallback Manim code for "${episodeTitle}" to avoid MathTex issues`);
  return createFallbackManimCode(script, episodeTitle);
}

export function createManimFile(scene: ManimScene, seriesId: number, episodeNumber: number): ManimFile {
  const fileName = `series-${seriesId}-episode-${episodeNumber}-${Date.now()}.py`;
  const filePath = `server/manim/${fileName}`;
  
  const fullCode = `from manim import *
import numpy as np

${scene.code}

if __name__ == "__main__":
    scene = ${scene.sceneName}()
    scene.render()
`;
  
  return { fileName, filePath, fullCode };
} 