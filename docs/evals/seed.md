# Visentia — Seed Eval Set

Real prompts from actual Year 8 tutoring sessions, captured during the initial `/grill-with-docs` session. Each entry is a regression test: every release should run against these and produce graded output.

This is the **seed** eval set. Add new entries as new prompts emerge from real sessions. Never delete; mark entries as deprecated if behaviour changes.

## Entry format

```yaml
id: unique short identifier (EV-NNN)
date_captured: when this came up in a real session (approximate)
year_level: Australian year level
prompt: the actual ask, as the Tutor would type it
math_content_type: Relationship | Procedure | Derivation
expected_artifact_form: Video | Interactive | Visual Answer Card
mathematical_facts: what the system must get factually right
pedagogical_target: what makes the explanation actually good (subjective but specific)
success_10: what a 10/10 artifact looks like
success_5: what a 5/10 artifact looks like (the floor for "usable")
failure_modes: specific things to check the output doesn't do
notes: anything else
```

---

## EV-001 — Converse of Pythagoras

```yaml
id: EV-001
date_captured: ~May 2026
year_level: 8
prompt: |
  "If you have a triangle not to scale with the 3 sides given, how to know if it
  is right angle or acute or obtuse?"
math_content_type: Relationship
expected_artifact_form: Video (with parameter-sweep animation showing the third side varying)
```

### Mathematical facts

Given sides $a, b, c$ with $c$ being the longest:

- $a^2 + b^2 = c^2$ → **right** triangle (Pythagoras' theorem, equality case)
- $a^2 + b^2 > c^2$ → **acute** triangle (third side too short for the angle to be 90°)
- $a^2 + b^2 < c^2$ → **obtuse** triangle (third side too long; opposite angle exceeds 90°)

This is the *converse* of Pythagoras, not Pythagoras itself. The longest side is always opposite the largest angle.

### Pedagogical target

The student should understand *why* the inequality direction maps to angle type, not just memorise the rule. A parameter sweep showing the angle morph as the third side changes is more revealing than three static examples.

### Success criteria

**10/10**:
- Triangle drawn live to the three side lengths
- Live readout of $a^2 + b^2$ vs $c^2$ with the current comparison
- Colour-coded angle classification (right / acute / obtuse)
- Animation sweeps the third side from "short" to "long" and the student can see the angle morph continuously through acute → right → obtuse
- Examples called out at key moments: $(3,4,5)$, $(5,5,6)$, $(5,5,7)$
- Voiceover paces the visual reveal
- Captions match the voiceover

**5/10** (floor for usable):
- Three static example triangles (right, acute, obtuse) drawn correctly
- Formulas stated correctly: $a^2 + b^2 \mathrel{?} c^2$
- No motion or sweep — the *why* is left to text
- Pythagoras stated but converse not explicitly framed

### Failure modes to check

- Confuses Pythagoras and its converse
- Inverts the inequality direction (puts $a^2 + b^2 > c^2$ for obtuse)
- Doesn't sort sides by length (treats $a, b, c$ by input order)
- Renders an invalid triangle (e.g. doesn't check the triangle inequality on inputs)

---

## EV-002 — Rate conversion with unit change

```yaml
id: EV-002
date_captured: ~May 2026
year_level: 8
prompt: |
  "What do you do if you want to calculate a total amount given a rate?
  For example, if apples cost $5/100g how much is 4.5kg?"
math_content_type: Procedure
expected_artifact_form: Video walking through the worked example with animated unit cancellation (Visual Answer Card is the cheaper fallback for v0.2)
note: |
  The Tutor explicitly framed this as a refresher for *themselves*, not for showing a student:
  "Felt I needed revision in rate conversion and finding out amounts given a rate
  and also converting rates to different units."
```

### Mathematical facts

- Rate = price per unit quantity: $\$5/100\text{g} = \$0.05/\text{g}$
- Convert units to match: $4.5\text{ kg} = 4500\text{ g}$
- Multiply: $4500\text{g} \times \frac{\$5}{100\text{g}} = \$225$
- The "g" units physically cancel in the multiplication (dimensional analysis)
- General form: $\text{total} = \text{quantity} \times \text{rate}$, with units matched first

### Pedagogical target

The dimensional-analysis insight: units cancel like algebraic terms. Once seen visually, the procedure generalises immediately to any rate conversion.

### Success criteria

**10/10**:
- Worked example laid out as a fraction multiplication: $\frac{\$5}{100\text{g}} \times 4500\text{g} = \$225$
- "g" units visibly cancel on screen (strike-through animation or colour-fade)
- Unit conversion (kg → g) shown explicitly with the $\times 1000$ factor
- General procedure stated in plain English: "scale the rate by the quantity, with units matched first"
- Voiceover walks through each step

**5/10**:
- Correct arithmetic ($225 final answer)
- Step-by-step listing of operations
- No visual unit cancellation
- Conversion step shown but not visualised

### Failure modes to check

- Forgets to convert kg → g (gets \$0.225 instead of \$225)
- Computes $\frac{4.5\text{kg} \times \$5}{100\text{g}}$ without unit conversion, producing nonsense units
- Loses units entirely partway through
- Inverts the rate (divides instead of multiplies)

---

## EV-003 — Area derivations for rhombus and trapezium

```yaml
id: EV-003
date_captured: ~May 2026
year_level: 8
prompt: |
  "Year 8, areas of different rhombuses and also trapezium, specifically how
  the formulas for these shapes are derived"
math_content_type: Derivation
expected_artifact_form: Video showing both visual derivations sequentially
```

### Mathematical facts

- **Rhombus area** = $\tfrac{1}{2} \cdot d_1 \cdot d_2$ where $d_1, d_2$ are the diagonals
- **Trapezium area** = $\tfrac{1}{2}(a + b) h$ where $a, b$ are parallel sides and $h$ is the perpendicular height

Classic visual proofs:

- **Rhombus**: the diagonals divide it into 4 congruent right triangles. Rearrange the four triangles into a rectangle of $d_1 \times d_2$. Halve the result because the original only filled half the bounding rectangle.
- **Trapezium**: duplicate the trapezium, rotate the copy 180°, abut it along the slanted side. The result is a parallelogram of base $(a+b)$ and height $h$. Halve because the original was one of the two.

Alternative rhombus formula: base × height (treating it as a parallelogram). The diagonal formula is the more elegant derivation and worth the focus.

### Pedagogical target

Area formulas aren't arbitrary — they come from rearranging shapes into ones whose area is already known (rectangles, parallelograms). The motion *is* the proof. The student should be able to predict the next move at each step.

### Success criteria

**10/10**:
- Two scenes, ~30 seconds each
- **Rhombus scene**: starts as a rhombus with diagonals drawn → splits into 4 right triangles → triangles slide/rotate into a rectangle of $d_1 \times d_2$ → formula appears with the halving step highlighted
- **Trapezium scene**: starts as a trapezium → duplicate fades in → rotates 180° → glides into place along the slanted side → forms a parallelogram of base $(a+b)$ and height $h$ → formula appears with halving step
- Smooth, predictable motion (student can guess the next move from the previous frame)
- Voiceover paces each transformation
- Both formulas stated explicitly at the end with the halving step emphasised

**5/10**:
- Static before/after diagrams correctly drawn
- Formulas stated correctly
- No actual motion
- Verbal-only explanation of the rearrangement

### Failure modes to check

- Inverts the formulas (forgets the $\tfrac{1}{2}$ factor)
- Treats rhombus area as base × side instead of base × height (or the diagonal formula)
- Trapezium duplicate doesn't rotate exactly 180° (e.g. translates instead)
- Animation doesn't preserve shape congruence during transformations
- Uses base × height for the rhombus and skips the more elegant diagonal-rectangle derivation entirely

---

## Notes for future expansion

- Add new entries from real sessions, not invented prompts
- Each entry should be testable: the failure modes and success criteria should be specific enough that a human grader could mark a run consistently
- The Math Content Type field is also part of the eval: does the classifier put it in the right bucket?
- The Expected Artifact Form field is the *suggestion* the classifier should make in v0.1; the Tutor's override (when one happens) is itself a data point worth capturing
- When the same concept appears at different year levels, create a new entry — the right artifact form often changes with year level
