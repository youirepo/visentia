import { ManimCodeValidator, ValidationResult } from '../services/manim-validator';

// Mock OpenAI client
jest.mock('../services/openai-client', () => ({
  openai: {
    chat: {
      completions: {
        create: jest.fn(),
      },
    },
  },
}));

describe('ManimCodeValidator', () => {
  let validator: ManimCodeValidator;

  beforeEach(() => {
    validator = new ManimCodeValidator();
  });

  describe('validateCodeStructure', () => {
    test('should pass valid Manim code structure', () => {
      const validCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Hello", font_size=48, color=WHITE)
                self.play(FadeIn(title))
                self.wait(2)
                self.play(FadeOut(title))
                self.wait(1)
      `;

      const result = validator['validateCodeStructure'](validCode);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should fail when missing class definition', () => {
      const invalidCode = `
        from manim import *
        
        def construct(self):
            title = Text("Hello", font_size=48, color=WHITE)
            self.play(FadeIn(title))
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Missing class definition');
    });

    test('should fail when missing Scene inheritance', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene:
            def construct(self):
                title = Text("Hello", font_size=48, color=WHITE)
                self.play(FadeIn(title))
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Missing Scene inheritance');
    });

    test('should fail when missing construct method', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene(Scene):
            def other_method(self):
                title = Text("Hello", font_size=48, color=WHITE)
                self.play(FadeIn(title))
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Missing construct method');
    });

    test('should fail when missing manim import', () => {
      const invalidCode = `
        class TestScene(Scene):
            def construct(self):
                title = Text("Hello", font_size=48, color=WHITE)
                self.play(FadeIn(title))
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Missing manim import');
    });
  });

  describe('font size validation', () => {
    test('should pass when all text uses font_size >= 48', () => {
      const validCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                subtitle = Text("Subtitle", font_size=60, color=WHITE)
                body = Text("Body text", font_size=48, color=WHITE)
                self.play(FadeIn(title))
                self.wait(2)
                self.play(FadeIn(subtitle))
                self.wait(2)
                self.play(FadeIn(body))
                self.wait(2)
      `;

      const result = validator['validateCodeStructure'](validCode);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should fail when text uses font_size < 48', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                small_text = Text("Too small", font_size=24, color=WHITE)
                tiny_text = Text("Tiny", font_size=12, color=WHITE)
                self.play(FadeIn(title))
                self.wait(2)
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Text font_size should be 48 or larger for visibility. Found font sizes that are too small.');
    });

    test('should fail when text uses deprecated size parameter', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", size=72, color=WHITE)
                subtitle = Text("Subtitle", size=60, color=WHITE)
                self.play(FadeIn(title))
                self.wait(2)
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Text objects should use font_size parameter instead of size parameter for Manim v0.19.0');
    });

    test('should pass when text uses font_size parameter correctly', () => {
      const validCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                subtitle = Text("Subtitle", font_size=60, color=WHITE)
                body = Text("Body text", font_size=48, color=WHITE)
                self.play(FadeIn(title))
                self.wait(2)
                self.play(FadeIn(subtitle))
                self.wait(2)
                self.play(FadeIn(body))
                self.wait(2)
      `;

      const result = validator['validateCodeStructure'](validCode);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('timing and animation validation', () => {
    test('should pass when code includes proper timing and animations', () => {
      const validCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                self.play(FadeIn(title))
                self.wait(4)
                self.play(FadeOut(title))
                self.wait(1)
      `;

      const result = validator['validateCodeStructure'](validCode);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should fail when missing timing and animations', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                # Missing animations and timing
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Scene should include proper timing with Wait(), FadeIn(), and FadeOut() for smooth transitions');
    });

    test('should fail when total wait time is too short', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                self.play(FadeIn(title))
                self.wait(5)
                self.play(FadeOut(title))
                self.wait(1)
                # Total wait time: 6 seconds (too short for 2-3 minute episode)
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Total wait time (6s) is too short for a 2-3 minute episode');
    });

    test('should pass when total wait time is sufficient', () => {
      const validCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                title = Text("Title", font_size=72, color=WHITE)
                self.play(FadeIn(title))
                self.wait(5)
                self.play(FadeOut(title))
                self.wait(1)
                
                section1 = Text("Section 1", font_size=60, color=WHITE)
                self.play(FadeIn(section1))
                self.wait(4)
                self.play(FadeOut(section1))
                self.wait(1)
                
                section2 = Text("Section 2", font_size=60, color=WHITE)
                self.play(FadeIn(section2))
                self.wait(4)
                self.play(FadeOut(section2))
                self.wait(1)
                
                # Total wait time: 20 seconds (reasonable for 2-3 minute episode)
      `;

      const result = validator['validateCodeStructure'](validCode);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('MathTex validation', () => {
    test('should warn about MathTex without proper LaTeX syntax', () => {
      const invalidCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                formula = MathTex("invalid latex")
                self.play(FadeIn(formula))
      `;

      const result = validator['validateCodeStructure'](invalidCode);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('MathTex found but may have invalid LaTeX syntax');
    });

    test('should pass when MathTex has proper LaTeX syntax', () => {
      const validCode = `
        from manim import *
        
        class TestScene(Scene):
            def construct(self):
                formula = MathTex("x^2 + y^2 = r^2")
                self.play(FadeIn(formula))
                self.wait(4)
                self.play(FadeOut(formula))
                self.wait(1)
      `;

      const result = validator['validateCodeStructure'](validCode);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });
});
