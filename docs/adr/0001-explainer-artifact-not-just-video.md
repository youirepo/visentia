# Explainer Artifact, not just Video

Visentia generates **Explainer Artifacts** — visual aids for math concepts — and *video* is one possible form, not the canonical output.

## Context

The project was originally framed as an "AI-generated explainer video" tool, in the style of 3Blue1Brown or Khan Academy. During grilling, the dominant use case sharpened to "the Tutor needs a quick visual aid mid-tutoring-session." In that context:

- Video has high generation latency (Manim renders take 30s–5min; the previous attempt at this project failed largely on rendering-pipeline fragility — see commits `5a86803`..`d63008c` on `mattpocock/skills` predecessors)
- A live tutoring session can't tolerate that latency
- Many math concepts are better served by an *interactive* visual (e.g. a parametric diagram with a slider) than by a passive video — the Tutor manipulates it live as they explain
- Static visuals + structured text suffice for many "refresher" cases

## Decision

The system produces **Explainer Artifacts**, of which video is one form. Two operating modes:

- **Quick Mode** (default for in-session use): interactive diagrams, static visuals, or short animated SVG — generation latency budget < 5s
- **Deep Mode** (default for at-home prep): polished video, typically Manim-rendered — generation latency in the minutes is acceptable

## Consequences

- The architecture supports multiple rendering pipelines, not one
- Video stops being the load-bearing technical challenge; the interesting AI engineering shifts toward prompt → structured artifact selection + parameterization
- The previous attempt's rendering-pipeline failure mode (Puppeteer + FFmpeg fragility) is sidestepped — in-session Quick artifacts never need video rendering
