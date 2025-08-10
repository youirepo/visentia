import { openai } from "./openai-client";

export interface ValidationResult {
  isValid: boolean;
  code: string;
  fixedCode?: string;
  feedback: string;
  errors: string[];
}

export class ManimCodeValidator {
  async validateAndFix(code: string): Promise<ValidationResult> {
    try {
      // First, try to validate the code structure
      const structuralValidation = this.validateCodeStructure(code);
      
      if (structuralValidation.isValid) {
        // If structure is good, try to run a basic syntax check
        const syntaxValidation = await this.validateSyntaxWithAI(code);
        return syntaxValidation;
      }
      
      // If structure has issues, try to fix them
      const fixedCode = await this.fixCodeWithAI(code, structuralValidation.feedback);
      const fixedValidation = await this.validateSyntaxWithAI(fixedCode);
      
      return {
        isValid: fixedValidation.isValid,
        code: code,
        fixedCode: fixedCode,
        feedback: structuralValidation.feedback,
        errors: structuralValidation.errors
      };
      
    } catch (error) {
      return {
        isValid: false,
        code: code,
        feedback: `Validation failed with error: ${error}`,
        errors: [`Validation error: ${error}`]
      };
    }
  }

  private validateCodeStructure(code: string): ValidationResult {
    const errors: string[] = [];
    
    // Check for basic structural requirements
    if (!code.includes('class')) {
      errors.push('Missing class definition');
    }
    
    if (!code.includes('Scene')) {
      errors.push('Missing Scene inheritance');
    }
    
    if (!code.includes('def construct')) {
      errors.push('Missing construct method');
    }
    
    if (!code.includes('from manim import')) {
      errors.push('Missing manim import');
    }
    
    // Check for common syntax issues
    if (code.includes('MathTex') && !code.includes('\\')) {
      errors.push('MathTex found but may have invalid LaTeX syntax');
    }
    
    if (code.includes('Text(') && code.includes('size=') && !code.includes('font_size=')) {
      errors.push('Text objects should use font_size parameter instead of size parameter for Manim v0.19.0');
    }
    
    const isValid = errors.length === 0;
    const feedback = isValid 
      ? 'Code structure appears valid'
      : `Structural issues found: ${errors.join(', ')}`;
    
    return {
      isValid,
      code,
      feedback,
      errors
    };
  }

  private async validateSyntaxWithAI(code: string): Promise<ValidationResult> {
    const systemPrompt = `You are a Python and Manim code validator. Analyze the provided Manim code and identify any syntax errors, import issues, or logical problems.

Your task is to:
1. Check for Python syntax errors
2. Verify Manim imports and class usage
3. Identify undefined variables or methods
4. Check for proper class inheritance
5. Validate method definitions
6. Ensure compatibility with Manim Community v0.19.0

MANIM v0.19.0 COMPATIBILITY CHECKS:
- Text objects must use 'font_size' parameter, not 'size'
- Shapes should use 'stroke_width' parameter
- Use 'animate' for animations (e.g., 'text.animate.shift(UP)')
- Proper positioning methods: 'shift()', 'move_to()', 'next_to()'

Respond with a JSON object containing:
{
  "isValid": boolean,
  "feedback": "detailed feedback about the code",
  "errors": ["list of specific errors found"],
  "suggestions": ["list of improvements"]
}`;

    const userPrompt = `Please validate this Manim code:

\`\`\`python
${code}
\`\`\`

Focus on syntax correctness, import validity, and Manim-specific requirements.`;

    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        temperature: 0.1,
        max_tokens: 1000
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new Error("No response from validation AI");
      }

      // Try to parse the JSON response
      try {
        const validation = JSON.parse(content);
        return {
          isValid: validation.isValid || false,
          code: code,
          feedback: validation.feedback || 'Validation completed',
          errors: validation.errors || []
        };
      } catch (parseError) {
        // If JSON parsing fails, analyze the text response
        const isValid = !content.toLowerCase().includes('error') && 
                       !content.toLowerCase().includes('invalid') &&
                       !content.toLowerCase().includes('problem');
        
        return {
          isValid,
          code: code,
          feedback: content,
          errors: isValid ? [] : ['AI validation found issues']
        };
      }

    } catch (error) {
      return {
        isValid: false,
        code: code,
        feedback: `AI validation failed: ${error}`,
        errors: [`AI validation error: ${error}`]
      };
    }
  }

  private async fixCodeWithAI(code: string, feedback: string): Promise<string> {
    const systemPrompt = `You are a Manim code fixer. Given code with issues and feedback about what's wrong, fix the code to make it valid and functional.

CRITICAL REQUIREMENTS:
1. Fix ALL syntax errors
2. Ensure proper imports
3. Fix class inheritance issues
4. Correct method definitions
5. Fix any undefined variables or functions
6. Maintain the original intent and structure
7. Use only valid Manim classes and methods
8. Return ONLY the fixed Python code - NO explanations, NO comments about what you fixed, NO markdown formatting
9. The response must be valid Python code that can be executed directly

IMPORTANT: Your response must contain ONLY the corrected Python code. Do not add any explanatory text, comments about your changes, or any other non-code content.`;

    const userPrompt = `Please fix this Manim code based on the feedback:

FEEDBACK: ${feedback}

CODE TO FIX:
\`\`\`python
${code}
\`\`\`

Fix all issues and return only the corrected Python code:`;

    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        temperature: 0.1,
        max_tokens: 2000
      });

      const fixedCode = response.choices[0]?.message?.content;
      if (!fixedCode) {
        throw new Error("No response from code fixer AI");
      }

      // Extract the code from the response
      return this.extractCodeFromResponse(fixedCode);

    } catch (error) {
      console.error('Failed to fix code with AI:', error);
      return code; // Return original code if fixing fails
    }
  }

  private extractCodeFromResponse(response: string): string {
    // Remove markdown code blocks if present
    let code = response.replace(/```python\n?/g, '').replace(/```\n?/g, '');
    
    // Remove any leading/trailing whitespace
    code = code.trim();
    
    // If the response starts with "import" or "from", it's likely pure code
    if (code.startsWith('import') || code.startsWith('from') || code.startsWith('class')) {
      // Find the last occurrence of a class definition and extract everything from there
      const classMatch = code.match(/class\s+\w+\s*\([^)]*\):[\s\S]*$/);
      if (classMatch) {
        return classMatch[0];
      }
      return code;
    }
    
    // Try to find code blocks in the response
    const codeBlockMatch = response.match(/```(?:python)?\n?([\s\S]*?)\n?```/);
    if (codeBlockMatch) {
      let extractedCode = codeBlockMatch[1].trim();
      // Find the last occurrence of a class definition and extract everything from there
      const classMatch = extractedCode.match(/class\s+\w+\s*\([^)]*\):[\s\S]*$/);
      if (classMatch) {
        return classMatch[0];
      }
      return extractedCode;
    }
    
    // If no clear code block, try to extract just the class definition
    const classMatch = response.match(/class\s+\w+\s*\([^)]*\):[\s\S]*$/);
    if (classMatch) {
      return classMatch[0];
    }
    
    // If no clear code block, return the cleaned response
    return code;
  }
}
