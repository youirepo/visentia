# Visentia

**Visentia helps a Tutor understand a math concept well enough to teach it.** The **Tutor** issues a natural-language **Prompt**, and Visentia produces an **Explainer Artifact** — a visual aid (interactive diagram, video, or static visual) the Tutor can use to learn the concept themselves, or to show a **Student** mid-session.

The Tutor's own understanding is the system's optimization target. The system improves Student outcomes *indirectly*, by helping the Tutor teach better — not by interacting with Students directly.

**Curriculum scope (MVP):** Australian Year 7–10 mathematics — algebra (linear and basic quadratics), number (fractions, decimals, percentages, indices), geometry (Pythagoras, congruence, similar triangles, basic 3D), measurement, basic trigonometry (SOHCAHTOA, intro unit circle), probability, statistics, and coordinate geometry. Content beyond this level is explicitly out of scope until the MVP works well within it.

**Build phasing:**
- **v0.1**: CLI + minimal localhost web UI. Engine is the priority — LLM → Manim Python → rendered MP4 with synchronized voiceover. Hybrid codegen (scene-template library first, free-form Manim fallback later).
- **v0.2**: Electron desktop shell wrapping the v0.1 engine. Add Interactive Parametric Diagrams and Visual Answer Cards as supplementary artifact forms.

**Tech stack (v0.1):** all free. LLM = Google AI Studio's Gemini 2.5 Flash (with Claude Sonnet 4.5 as the documented upgrade path). TTS = `edge-tts` (Microsoft neural voices via Python package; no key, no quota). Rendering = Manim (open source). The provider-swapping abstraction is treated as a first-class concern from day one.

## Language

**Tutor**:
The primary user of the system — someone whose role is to teach math (tutor, teacher, lecturer, or self-directed educator) and who issues Prompts to understand a concept well enough to teach it. In this project, the Tutor is also the developer.
_Avoid_: User (too generic; the Student is also a "user" in the everyday sense), Customer, Operator. Note: "Teacher" is acceptable as a synonym in informal use, but Tutor is canonical in code and docs.

**Student**:
A person being tutored by the Tutor who may be shown an Explainer Artifact during a session. Not a User of the system — has no direct interaction with it.
_Avoid_: Learner (the Tutor is also a learner), Pupil, End-user.

**Prompt**:
A natural-language request from the Tutor describing the math concept or question they want an Explainer Artifact for.
_Avoid_: Query, Question (less precise), Request.

**Explainer Artifact**:
A generated visual aid for a specific math concept. Three forms exist, with **Video** as the primary form in MVP v0.1:
- **Video** (MVP v0.1, primary): a Manim-rendered animation, up to ~5 minutes, with synchronized voiceover narration (TTS) and on-screen captions. The default response to any Prompt. Generation latency in the minutes is acceptable even mid-session.
- **Interactive Parametric Diagram** (MVP v0.2, supplement): a live-rendered figure with parameters the Tutor manipulates (sliders, draggable points). Generated on demand *after* a Video, when the Tutor wants to drive parameters live during a discussion with a Student.
- **Visual Answer Card** (MVP v0.2, fallback): a structured single-page artifact combining worked arithmetic, unit-cancellation visuals, and a one-sentence general procedure. Used for *procedure/refresh* prompts where a video would be overkill.

_Avoid_: Lesson (too broad — an artifact answers one question, not a curriculum), Output, Content. Note: "Video" was deferred in an earlier draft of this glossary on flawed cognitive-load assumptions; that direction was reverted — see ADR-0002.

**Math Content Type**:
The category of mathematical content a Prompt is asking about. Used by the system to suggest which form of Explainer Artifact best fits. Three categories:
- **Relationship**: prompts about "when is X true?" or "how does X depend on Y?" → **Video** with parameter-sweep animation (default); Interactive Parametric Diagram available as supplement
- **Procedure**: prompts about "how do I do X?" or refresh-style "remind me how X works" → **Video** walking through a worked example (default); Visual Answer Card available as a cheaper fallback for the simplest cases
- **Derivation**: prompts about "why is X true?" or "show me where X comes from" → **Video** showing the visual transformation (default)

The mapping is a default suggestion, not a hard rule; the Tutor can override it via Suggest-and-Confirm.

**Mode**:
A generation profile that determines artifact length and depth, *not* latency (the Tutor tolerates up to ~5 minutes of generation time even mid-session).
- **Quick Mode**: short artifact (< 2 min video, or Visual Answer Card) for refresher/top-up prompts.
- **Deep Mode**: longer artifact (up to ~5 min video) for thorough relearning of a concept.

## Relationships

- A **Tutor** issues a **Prompt** → the system classifies its **Math Content Type** → suggests a form of **Explainer Artifact** → the Tutor confirms or overrides (Suggest-and-Confirm) → the artifact is generated in **Quick Mode** or **Deep Mode**
- The **Tutor** may show an **Explainer Artifact** to a **Student** during a session, but the system does not interact with Students directly
- The **Math Content Type → Explainer Artifact form** mapping is the system's *default suggestion*; the Tutor's overrides are a signal the system can learn from

## Example dialogue

> **Tutor (mid-session, 4:15pm Tuesday):** "Quick artifact — show me how a ladder sliding down a wall illustrates related rates."
> **Visentia:** Returns in 3s with an interactive diagram: a ladder against a wall, draggable bottom position, height and rate-of-change displayed live. Tutor drags the slider as they explain to the Student.
>
> **Tutor (Sunday afternoon, prepping for the week):** "Deep artifact — I want to actually understand again why integration by parts works, not just remember the formula."
> **Visentia:** Returns in 3 minutes with a 6-minute narrated Manim video deriving IBP from the product rule, with visual interpretation.

## Flagged ambiguities

- **"Video" — the back-and-forth**: the project was originally framed around video; an intermediate draft deferred video in favour of interactive output on cognitive-load and latency assumptions; that was reversed once the Tutor clarified that (a) up to 5-minute generation is acceptable even mid-session, (b) video is *lower* cognitive load to consume, not higher, and (c) interactive math widgets are already commoditized by general-purpose AI tools (Claude Artifacts, etc.) so are not a differentiator. Resolved: **Video is the primary Explainer Artifact form in MVP v0.1**. See ADR-0001 (initial broadening) and ADR-0002 (the reversal back to video-first).
- **"User" ambiguity**: was used to mean both the Tutor and the Student. Resolved: only the **Tutor** is a User of the system. The Student is an audience.
- **"Learning" ambiguity**: was used for both the Tutor's learning (the system's optimization target) and the Student's learning (a downstream effect). Resolved: the system optimizes for the **Tutor's** learning; better Student outcomes follow from better teaching, not from direct Student interaction.
- **"Refresh" vs "Explain"**: the Tutor sometimes wants their own understanding revived (for them), sometimes wants something showable to the Student (for them). Resolved: both are valid Prompts; the consumer is implicit in the Math Content Type and the Mode rather than asked explicitly.
- **Latency budget**: an intermediate draft assumed in-session use required < 5s generation. Resolved: the Tutor tolerates up to 5 minutes mid-session. Latency is *not* a primary architectural driver; output quality is.
