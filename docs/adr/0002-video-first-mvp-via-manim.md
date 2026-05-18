# Video-First MVP via Manim

Visentia's MVP v0.1 produces **video** as its primary Explainer Artifact, rendered with Manim. Interactive and static-card forms are deferred to v0.2.

## Context

The project was originally framed around AI-generated math videos in the style of 3Blue1Brown or Khan Academy. During grilling, an intermediate hypothesis emerged that interactive parametric diagrams would be a better MVP target than video, on three assumed grounds:

1. **Latency**: in-session use seemed to require < 5s generation
2. **Cognitive load**: interactive seemed lower cognitive load than passive video
3. **Failure-mode avoidance**: the prior attempt died on a video-rendering pipeline

All three assumptions were tested and rejected by the Tutor:

1. **Latency budget is actually ~5 minutes**, even mid-session. The Tutor is willing to explain to the Student what's coming while a video generates. Latency is not a primary constraint.
2. **Video is *lower* cognitive load**, not higher. Driving an interactive widget while learning is harder than receiving a narrated walkthrough. The Tutor's stated learning preference is video, and that preference is stable.
3. **Interactive math widgets are commoditized.** General-purpose AI tools (Claude Artifacts, GPT-5 Canvas, etc.) already produce parametric-diagram React components on demand, free. Building this in Visentia adds no differentiation.

The actual differentiator — math-explainer video quality — is *not* commoditized by general AI tools. That's where Visentia has to play.

The prior attempt's failure was the wrong tool (Puppeteer + FFmpeg trying to capture HTML/CSS animations) rather than the wrong category (video). **Manim — the tool 3Blue1Brown literally uses** — is purpose-built for declarative mathematical animation, eats Python and produces MP4, no browser involved. The lesson from the prior attempt's `d63008c..85f40ac` arc is "stop fighting the rendering pipeline; use a tool actually designed for math animation."

## Decision

MVP v0.1 supports exactly one Explainer Artifact form:

- **Video**: Manim-rendered animation, up to ~5 minutes, optionally narrated. All Math Content Types (Relationship / Procedure / Derivation) default to Video.

v0.2 adds:

- **Interactive Parametric Diagram**: on-demand supplement generated *after* a video, for live discussion with a Student
- **Visual Answer Card**: cheaper fallback for the simplest procedural prompts

## Consequences

- The video-rendering tech stack is **Manim**, not Puppeteer/FFmpeg. The prior attempt's specific failure mode (HTML/CSS screencap fragility) is not just sidestepped, it's structurally avoided.
- The interesting AI engineering work concentrates on **LLM → Manim code generation, code-correctness + render-correctness + pedagogical-correctness eval, and library composition vs free-form codegen** — all real, substantive AI eng challenges.
- The MVP scope is *smaller* than the previous interactive-first plan in terms of artifact-type count (one, not three), but *larger* in technical depth (Manim codegen is non-trivial). This is a net win for the "learn AI engineering rigorously" goal.
- Voiceover synthesis + scene-timing alignment is in scope but can be added incrementally (silent video first, narration second).
- Risk: Manim code-gen quality is unproven for Year 7–10 content. Mitigation: build a scene-template library for common primitives (number line, triangle, area-derivation transformation) so the LLM composes rather than freehand-codes when possible.
