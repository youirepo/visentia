import { openai } from "./openai-client";
import { ManimCodeValidator } from "./manim-validator.js";

export class ManimGenerator {
  private validator: ManimCodeValidator;

  constructor() {
    this.validator = new ManimCodeValidator();
  }

  async generateManimCode(
    seriesTitle: string,
    episodeTitle: string,
    content: string,
    maxRetries: number = 3
  ): Promise<string> {
    console.log(`Generating Manim code for: ${seriesTitle} - ${episodeTitle}`);
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        // Generate initial code with ChatGPT
        const generatedCode = await this.generateCodeWithChatGPT(
          seriesTitle,
          episodeTitle,
          content
        );

        console.log(`Attempt ${attempt}: Generated initial Manim code`);

        // Validate and potentially fix the code
        const validationResult = await this.validator.validateAndFix(generatedCode);
        
        if (validationResult.isValid) {
          console.log(`Attempt ${attempt}: Code validation successful`);
          return validationResult.code;
        }

        // If validation failed but we have a fixed version, try that
        if (validationResult.fixedCode) {
          console.log(`Attempt ${attempt}: Trying fixed code from validator`);
          const retryValidation = await this.validator.validateAndFix(validationResult.fixedCode);
          
          if (retryValidation.isValid) {
            console.log(`Attempt ${attempt}: Fixed code validation successful`);
            return retryValidation.code;
          }
        }

        // If we still have issues and this isn't the last attempt, try to regenerate
        if (attempt < maxRetries) {
          console.log(`Attempt ${attempt}: Validation failed, regenerating with feedback`);
          // Use the validation feedback to improve the next generation
          const improvedCode = await this.generateCodeWithChatGPT(
            seriesTitle,
            episodeTitle,
            content,
            validationResult.feedback
          );
          
          // Try the improved code
          const improvedValidation = await this.validator.validateAndFix(improvedCode);
          if (improvedValidation.isValid) {
            console.log(`Attempt ${attempt}: Improved code validation successful`);
            return improvedValidation.code;
          }
        }

      } catch (error) {
        console.error(`Attempt ${attempt} failed:`, error);
        if (attempt === maxRetries) {
          throw new Error(`Failed to generate valid Manim code after ${maxRetries} attempts: ${error}`);
        }
      }
    }

    throw new Error(`Failed to generate valid Manim code after ${maxRetries} attempts`);
  }

  private async generateCodeWithChatGPT(
    seriesTitle: string,
    episodeTitle: string,
    content: string,
    previousFeedback?: string
  ): Promise<string> {
    const systemPrompt = `You are an expert Manim developer. Generate clean, valid Manim code for educational videos.

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
- Use proper timing: Wait(seconds), FadeIn(), FadeOut()

CRITICAL TIMING REQUIREMENTS - YOU MUST FOLLOW THESE EXACTLY:
- Each text element must appear for 3-5 seconds using Wait()
- Use FadeIn() and FadeOut() for ALL text elements
- Total scene duration MUST be 2-3 minutes (120-180 seconds)
- Add Wait(3) between each content section
- Use this exact pattern: FadeIn(text), Wait(4), FadeOut(text), Wait(1)

EXAMPLE STRUCTURE:
- Introduction text: FadeIn, Wait(4), FadeOut, Wait(1)
- Main concept 1: FadeIn, Wait(4), FadeOut, Wait(1)
- Main concept 2: FadeIn, Wait(4), FadeOut, Wait(1)
- Main concept 3: FadeIn, Wait(4), FadeOut, Wait(1)
- Conclusion: FadeIn, Wait(4), FadeOut, Wait(1)

TEXT SIZE EXAMPLES (use these exact sizes):
- Title: Text("Title", font_size=72, color=WHITE)
- Headings: Text("Heading", font_size=60, color=WHITE)
- Main text: Text("Content", font_size=48, color=WHITE)
- NEVER use font_size less than 48!

IMPORTANT: Use Manim Community v0.19.0 syntax:
- Text("Hello", font_size=48)
- Circle(stroke_width=2)
- Square(fill_opacity=0.5)
- text.animate.shift(UP)

CRITICAL: Text must be clearly visible with font_size=48 or larger!
NEVER use font_size less than 48 - this makes text invisible!

MANIM v0.19.0 SPECIFIC REQUIREMENTS:
- Use 'font_size' parameter instead of 'size' for Text objects
- Use 'stroke_width' parameter instead of 'stroke_width' for shapes
- Use 'fill_opacity' and 'stroke_opacity' for transparency
- Use 'shift()', 'move_to()', 'next_to()' for positioning
- Use 'animate' for animations (e.g., 'text.animate.shift(UP)')
- Use proper timing: Wait(seconds), FadeIn(), FadeOut()
- Ensure total scene duration is 2-3 minutes (120-180 seconds)
- Each text element should have appropriate display time with fade effects

TIMING PATTERN EXAMPLE:
- Title sequence: FadeIn(title), Wait(5), FadeOut(title), Wait(1)
- Content sections: FadeIn(content), Wait(4), FadeOut(content), Wait(1)
- Repeat pattern to reach 2-3 minutes total duration

${previousFeedback ? `PREVIOUS FEEDBACK TO ADDRESS:\n${previousFeedback}\n\n` : ''}
Start your response with 'import' and end with the last line of Python code. Nothing else.`;

    const userPrompt = `Create a Manim scene for a COMPLETE, STANDALONE educational video:
Series: ${seriesTitle}
Episode: ${episodeTitle}
Content: ${content}

CRITICAL: This must be a COMPLETE lesson that teaches the entire topic, NOT an introduction to a series. The content should cover everything from basic concepts to advanced understanding in one video.

The scene should:
- Start with a title showing the series and episode
- Present the COMPLETE content comprehensively with proper timing
- Use smooth animations and transitions
- Include fade in/out effects for text elements
- Cover ALL aspects of the topic thoroughly
- End with a complete conclusion that summarizes everything learned

CRITICAL TIMING REQUIREMENTS - YOU MUST FOLLOW THESE EXACTLY:
- Each text element must appear for 3-5 seconds using Wait()
- Use FadeIn() and FadeOut() for ALL text elements
- Total scene duration MUST be 2-3 minutes (120-180 seconds)
- Add Wait(3) between each content section
- Use this exact pattern: FadeIn(text), Wait(4), FadeOut(text), Wait(1)

EXAMPLE STRUCTURE:
1. Title appears with FadeIn, stays for 5 seconds, fades out
2. Content section 1: FadeIn, Wait(4), FadeOut, Wait(1)
3. Content section 2: FadeIn, Wait(4), FadeOut, Wait(1)
4. Continue pattern to reach 2-3 minutes total

IMPORTANT: Use Manim Community v0.19.0 syntax:
- Text objects: Text("Hello", font_size=48, color=WHITE)
- Shapes: Circle(radius=1, stroke_width=2, fill_opacity=0.5)
- Animations: text.animate.shift(UP), circle.animate.scale(2)
- Timing: Wait(3), FadeIn(text), FadeOut(text)

CRITICAL: Text must be clearly visible with font_size=48 or larger!
NEVER use font_size less than 48 - this makes text invisible!

Generate ONLY the Python code:`;

    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    const generatedCode = response.choices[0]?.message?.content;
    if (!generatedCode) {
      throw new Error("Failed to generate code from ChatGPT");
    }

    // Clean up the response to extract just the code
    return this.extractCodeFromResponse(generatedCode);
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