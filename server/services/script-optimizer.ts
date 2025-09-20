import { openai } from "./openai-client.js";

export async function optimizeScript(topic: string, rawScript: string): Promise<string> {
  const systemPrompt = `You are an expert educational script editor. Rewrite scripts to be direct, engaging, and instructional.

Rules:
- Remove meta-intros like "Welcome to", "In this video", "We will discuss", "This is a complete guide".
- Do NOT repeat the user's prompt verbatim.
- Start immediately with the core explanation or a concise hook.
- Keep the content comprehensive and step-by-step.
- Maintain factual accuracy; do not invent details that contradict the original.
- Use clear headings or transitions only if needed; no filler.
- Keep the length comparable to the original (within ±10%).
- Output only the rewritten script text, no extra commentary.
`;

  const userPrompt = `Topic: ${topic}

Rewrite the following script to follow the rules. Keep all important teaching points, but remove formulaic openings and prompt echoing.

Original Script:\n\n${rawScript}`;

  try {
    try {
      console.log('[ScriptOptimizer] systemPrompt:\n', systemPrompt);
      console.log('[ScriptOptimizer] userPrompt (truncated):\n', userPrompt.slice(0, 1000));
    } catch {}

    const resp = await openai.chat.completions.create({
      model: 'gpt-4',
      temperature: 0.6,
      max_tokens: 3000,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
    });

    const text = resp.choices?.[0]?.message?.content?.trim();
    if (text && text.length > 0) return text;
  } catch (err) {
    console.warn('[ScriptOptimizer] Failed, returning original script. Error:', err);
  }

  return rawScript;
}



