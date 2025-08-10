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

IMPORTANT REQUIREMENTS:
1. Use ONLY valid Manim syntax and classes
2. Import statements must be correct and complete
3. Scene class must inherit from Scene
4. All methods must be properly defined
5. No undefined variables or functions
6. Use proper Python syntax throughout
7. Ensure all text rendering uses proper Manim text classes
8. Animation timing should be reasonable (not too fast or slow)

${previousFeedback ? `PREVIOUS FEEDBACK TO ADDRESS:\n${previousFeedback}\n\n` : ''}
Generate ONLY the Python code, no explanations or markdown formatting.`;

    const userPrompt = `Create a Manim scene for:
Series: ${seriesTitle}
Episode: ${episodeTitle}
Content: ${content}

The scene should:
- Start with a title showing the series and episode
- Present the content in an engaging way
- Use smooth animations and transitions
- End with a clean conclusion

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
    
    // If the response starts with "import" or "from", it's likely pure code
    if (code.startsWith('import') || code.startsWith('from') || code.startsWith('class')) {
      return code;
    }
    
    // Try to find code blocks in the response
    const codeBlockMatch = response.match(/```(?:python)?\n?([\s\S]*?)\n?```/);
    if (codeBlockMatch) {
      return codeBlockMatch[1].trim();
    }
    
    // If no clear code block, return the cleaned response
    return code;
  }
} 