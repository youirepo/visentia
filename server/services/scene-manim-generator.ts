import { openai } from "./openai-client";
import { ManimCodeValidator } from "./manim-validator.js";
import type { Scene } from "./scene-generator.js";

export class SceneManimGenerator {
  private validator: ManimCodeValidator;

  constructor() {
    this.validator = new ManimCodeValidator();
  }

  async generateSceneManimCode(
    scene: Scene,
    seriesTitle: string,
    episodeTitle: string,
    maxRetries: number = 3
  ): Promise<string> {
    console.log(`Generating Manim code for scene ${scene.sceneNumber}: ${scene.title}`);
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const generatedCode = await this.generateCodeWithChatGPT(scene, seriesTitle, episodeTitle);
        console.log(`Attempt ${attempt}: Generated scene Manim code`);

        const validationResult = await this.validator.validateAndFix(generatedCode);
        
        console.log(`Attempt ${attempt}: Scene validation result:`, {
          isValid: validationResult.isValid,
          hasFixedCode: !!validationResult.fixedCode,
          errors: validationResult.errors,
          feedback: validationResult.feedback
        });
        
        if (validationResult.isValid) {
          console.log(`Attempt ${attempt}: Scene code validation successful`);
          return validationResult.code;
        }

        if (validationResult.fixedCode) {
          console.log(`Attempt ${attempt}: Trying fixed scene code from validator`);
          const retryValidation = await this.validator.validateAndFix(validationResult.fixedCode);
          
          if (retryValidation.isValid) {
            console.log(`Attempt ${attempt}: Fixed scene code validation successful`);
            return retryValidation.code;
          }
        }

        if (attempt < maxRetries) {
          console.log(`Attempt ${attempt}: Scene validation failed, regenerating with feedback`);
          const improvedCode = await this.generateCodeWithChatGPT(
            scene,
            seriesTitle,
            episodeTitle,
            validationResult.feedback
          );
          
          const improvedValidation = await this.validator.validateAndFix(improvedCode);
          if (improvedValidation.isValid) {
            console.log(`Attempt ${attempt}: Improved scene code validation successful`);
            return improvedValidation.code;
          }
        }

      } catch (error) {
        console.error(`Scene attempt ${attempt} failed:`, error);
        if (attempt === maxRetries) {
          throw new Error(`Failed to generate valid Manim code for scene ${scene.sceneNumber} after ${maxRetries} attempts: ${error}`);
        }
      }
    }

    throw new Error(`Failed to generate valid Manim code for scene ${scene.sceneNumber} after ${maxRetries} attempts`);
  }

  private async generateCodeWithChatGPT(
    scene: Scene,
    seriesTitle: string,
    episodeTitle: string,
    previousFeedback?: string
  ): Promise<string> {
    const systemPrompt = `You are an expert Manim developer creating individual educational video scenes. Generate clean, valid Manim code for a single scene.

CRITICAL: You must output ONLY valid Python code. Do NOT include:
- Explanations
- Comments about what the code does
- Markdown formatting
- Any text that is not Python code

Start your response with 'import' and end with the last line of Python code. Nothing else.

MANIM v0.19.0 SPECIFIC REQUIREMENTS:
- Use 'font_size' parameter instead of 'size' for Text objects
- ALWAYS use font_size=48 or larger for visibility
- Use 'stroke_width' parameter instead of 'stroke_width'
- Use 'fill_opacity' and 'stroke_opacity' parameters
- Use 'shift()', 'move_to()', 'next_to()' for positioning
- Use 'animate' for animations

SCENE REQUIREMENTS:
- Scene duration: ${scene.duration} seconds
- Visual elements: ${scene.visualElements.join(', ')}
- Animation type: ${scene.animationType}
- Scene description: ${scene.description}

TIMING REQUIREMENTS (CRITICAL FOR AUDIO-VIDEO SYNC):
- Scene must last EXACTLY ${scene.duration} seconds (calculated from actual TTS audio duration)
- Use self.wait(${scene.duration}) as the main timing mechanism at the end
- Include FadeIn() and FadeOut() for smooth transitions
- Add intermediate animations within the scene duration, but ensure total scene time = ${scene.duration}s
- DO NOT exceed ${scene.duration} seconds - this will cause desynchronization

VISUAL REQUIREMENTS (PRIORITIZE DIAGRAMS AND VISUALS):
- MINIMIZE TEXT: Use diagrams, shapes, and visual representations instead of text
- MANDATORY VISUALS: This scene must focus on the specified visual elements: ${scene.visualElements.join(', ')}
- Use Axes/NumberPlane for mathematical concepts and graphs
- Use Shapes extensively: Circle, Square, Rectangle, Arrow, Line, Polygon
- Use VGroup to combine related visual elements into cohesive diagrams
- Use SurroundingRectangle, Brace, and highlights to emphasize key parts
- Use Create(), Write(), Transform(), MoveAlongPath(), DrawBorderThenFill() animations
- Text should be MINIMAL: only 1-2 words per concept, use visual metaphors instead
- Prefer visual storytelling over text explanations

DIAGRAM EXAMPLES TO INCLUDE:
- Flowcharts: Use Rectangle() + Arrow() to show process flows
- Venn diagrams: Use Circle() with different fill_opacity for overlaps
- Timelines: Use Line() + Rectangle() + Text() for chronological events
- Mathematical graphs: Use Axes() + get_graph() then .set_color() for functions and data
- Molecular diagrams: Use Circle() + Line() for atomic structures
- Force diagrams: Use Arrow() with different colors for different forces
- Geometric proofs: Use shapes that transform to show relationships

CRITICAL MANIM SYNTAX RULES:
- For graph colors: axes.get_graph(func).set_color(RED) NOT get_graph(func, color=RED)
- For text colors: Text("Hello").set_color(BLUE) NOT Text("Hello", color=BLUE)
- For shape colors: Circle().set_color(GREEN) NOT Circle(color=GREEN)
- For frame dimensions: Use config.frame_width and config.frame_height NOT FRAME_WIDTH or FRAME_HEIGHT
- For scaling: obj.scale_to_fit_width(config.frame_width*0.90) NOT scale_to_fit_width(FRAME_WIDTH*0.90)
- NEVER use ImageMobject with external files - create visual elements with shapes, text, and geometric objects
- Do NOT use ShowCreation; use Create instead (ShowCreation is removed in v0.19)
- Prefer MathTex over Tex for LaTeX; ensure valid LaTeX
- Always use .set_color() method instead of color parameter in constructors

CRITICAL: Text must be clearly visible with font_size=48 or larger!
ALWAYS scale text to fit the frame width (90%) and height (85% if needed) using scale_to_fit_width/scale_to_fit_height immediately after creation.

${previousFeedback ? `PREVIOUS FEEDBACK TO ADDRESS:\n${previousFeedback}\n\n` : ''}

CRITICAL OUTPUT FORMAT:
Your response must be complete, executable Python code that includes:
1. from manim import *
2. class YourSceneName(Scene):
3. def construct(self): with all animations
4. Proper indentation and syntax

Start your response with 'from manim import *' and end with the last line of Python code. Nothing else.`;

    const userPrompt = `Create a Manim scene for this specific educational video segment.

Series: ${seriesTitle}
Episode: ${scene.sceneNumber}: ${scene.title}
Scene Description: ${scene.description}
Visual Elements: ${scene.visualElements.join(', ')}
Animation Type: ${scene.animationType}
Duration: ${scene.duration} seconds

This scene should:
- Focus on the specified visual elements and animation type
- Last exactly ${scene.duration} seconds
- Use visual storytelling with minimal text
- Include smooth animations and transitions
- Build upon the scene description provided

Generate ONLY the Python code for this single scene:`;

    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 1500
      });

      const generatedCode = response.choices[0]?.message?.content;
      if (!generatedCode) {
        throw new Error("Failed to generate scene code from ChatGPT");
      }

      return this.extractCodeFromResponse(generatedCode);
    } catch (error) {
      console.error('Failed to generate scene code:', error);
      throw error;
    }
  }

  private extractCodeFromResponse(response: string): string {
    // Remove markdown code blocks if present
    let code = response.replace(/```python\n?/g, '').replace(/```\n?/g, '');
    
    // Remove any leading/trailing whitespace
    code = code.trim();
    
    // Find the first line that starts with 'import' or 'from' or 'class'
    const lines = code.split('\n');
    let startIndex = -1;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith('import') || line.startsWith('from') || line.startsWith('class')) {
        startIndex = i;
        break;
      }
    }
    
    if (startIndex === -1) {
      throw new Error('No valid Python code found in response');
    }
    
    // Find the last line that contains valid Python code (not explanatory text)
    let endIndex = lines.length - 1;
    for (let i = lines.length - 1; i >= startIndex; i--) {
      const line = lines[i].trim();
      // Skip empty lines and lines that look like explanatory text
      if (line && !line.startsWith('#') && !line.match(/^[A-Z][a-z]/)) {
        endIndex = i;
        break;
      }
    }
    
    // Extract only the valid Python code
    const validLines = lines.slice(startIndex, endIndex + 1);
    return validLines.join('\n');
  }
}
