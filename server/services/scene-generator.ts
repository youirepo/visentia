import { openai } from "./openai-client";

export interface Scene {
  sceneNumber: number;
  title: string;
  description: string;
  narration: string;
  duration: number; // in seconds
  visualElements: string[];
  animationType: string;
  mode: 'math' | 'diagram' | 'html'; // Rendering mode
}

export interface SceneBasedScript {
  title: string;
  totalDuration: number;
  scenes: Scene[];
}

export async function generateSceneBasedScript(
  topic: string,
  subject: string,
  difficultyLevel: string,
  style: string,
  targetDuration: string
): Promise<SceneBasedScript> {
  const systemPrompt = `You are an expert educational content creator specializing in scene-based video production. Break down educational content into timed scenes that can be animated and narrated separately.

CRITICAL REQUIREMENTS:
- Split content into 3-6 scenes, each 15-45 seconds long
- Each scene must have a clear visual focus and specific narration
- Scenes should build upon each other progressively
- Include specific visual elements and animation types for each scene
- Total duration should match the requested target (${targetDuration})

SCENE STRUCTURE:
Each scene should include:
1. Clear title (2-4 words)
2. Brief description of what happens
3. Exact narration text (1-2 sentences, 15-45 seconds when spoken)
4. Duration in seconds (15-45)
5. Visual elements (specific shapes, diagrams, animations)
6. Animation type (Create, Transform, MoveAlongPath, etc.)
7. Mode: Choose the appropriate rendering mode:
   - "math": For advanced mathematical concepts requiring Manim animations
   - "diagram": For flowcharts, process diagrams, or visual representations
   - "html": For styled text, formulas, or simple visual content

VISUAL FOCUS:
- Prioritize diagrams, charts, graphs, and geometric shapes
- Use mathematical concepts, flowcharts, Venn diagrams, timelines
- Include interactive elements that can be animated
- Each scene should have a distinct visual theme

Return a JSON object with the complete scene breakdown.`;

  const userPrompt = `Create a scene-based script for an educational video about:

Topic: ${topic}
Subject: ${subject}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Target Duration: ${targetDuration}

Break this into 3-6 scenes, each with clear visual elements and narration. Focus on visual storytelling with minimal text overlays.

Return JSON in this exact format:
{
  "title": "Video Title",
  "totalDuration": 180,
  "scenes": [
    {
      "sceneNumber": 1,
      "title": "Scene Title",
      "description": "What happens in this scene",
      "narration": "Exact text to be narrated (15-45 seconds when spoken)",
      "duration": 30,
      "visualElements": ["Circle", "Arrow", "Mathematical graph"],
      "animationType": "Create",
      "mode": "math"
    }
  ]
}`;

  try {
    console.log('[SceneGenerator] Generating scene-based script...');
    
    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    const content = response.choices[0]?.message?.content;
    if (!content) {
      throw new Error("Failed to generate scene-based script");
    }

    // Extract JSON from response
    let jsonContent = content;
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      jsonContent = jsonMatch[1];
    }

    const script = JSON.parse(jsonContent);
    console.log(`[SceneGenerator] Generated ${script.scenes?.length || 0} scenes`);
    
    return script;
  } catch (error) {
    console.error('Failed to generate scene-based script:', error);
    throw new Error(`Failed to generate scene-based script: ${error instanceof Error ? error.message : String(error)}`);
  }
}

