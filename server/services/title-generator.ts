import { openai } from "./openai-client.js";

export interface TitleContext {
  topic: string;
  subject?: string;
  style?: string;
  difficultyLevel?: string;
  scriptExcerpt?: string;
}

export async function generateUniqueTitle(context: TitleContext): Promise<string> {
  const { topic, subject, style, difficultyLevel, scriptExcerpt } = context;

  const systemPrompt = `You are a world-class educational copywriter creating concise, compelling video titles.

Rules:
- Output ONE title only, no quotes, no backticks, no extra text
- 5–12 words; clear, accurate, engaging
- Avoid clichés: "Complete Guide", "Everything You Need to Know", "Introduction to", "Understanding", "How X Works"
- Prefer specificity over hype; feel trustworthy, not clickbait
- Use correct capitalization; colon subtitles allowed (e.g., "Limits in Calculus: From Intuition to Proof")
- Tailor to the user's prompt and level; reflect what will actually be covered
`;

  const userPrompt = `Create a unique title for an educational video.

Context:
- Topic: ${topic}
- Subject: ${subject || "(unspecified)"}
- Difficulty: ${difficultyLevel || "(unspecified)"}
- Style: ${style || "(unspecified)"}
- Script excerpt (optional): ${scriptExcerpt ? truncate(scriptExcerpt, 800) : "(none)"}

Return only the title line.`;

  try {
    try {
      console.log('[TitleGenerator] systemPrompt:\n', systemPrompt);
      console.log('[TitleGenerator] userPrompt:\n', userPrompt);
    } catch {}

    const resp = await openai.chat.completions.create({
      model: "gpt-4",
      temperature: 0.8,
      max_tokens: 40,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ]
    });

    const raw = resp.choices?.[0]?.message?.content?.trim() || '';
    const title = sanitizeTitle(raw);
    if (title) return title;
  } catch (err) {
    console.warn('[TitleGenerator] Falling back due to error:', err);
  }

  // Fallback deterministic title
  return fallbackTitle(topic);
}

function sanitizeTitle(text: string): string {
  if (!text) return '';
  // Take first non-empty line
  const line = text.split('\n').map(s => s.trim()).find(Boolean) || '';
  // Strip wrapping quotes/backticks
  const cleaned = line.replace(/^`+|`+$/g, '').replace(/^"+|"+$/g, '').replace(/^'+|'+$/g, '').trim();
  return cleaned;
}

function truncate(s: string, n: number): string {
  return s.length <= n ? s : s.slice(0, n - 1) + '…';
}

function fallbackTitle(topic: string): string {
  const patterns = [
    `${topic}: Key Ideas Brought to Life`,
    `${topic}: From Intuition to Mastery`,
    `${topic}: Concepts, Methods, and Pitfalls`,
    `${topic}: A Practical Exploration`,
    `${topic}: Insights and Applications`,
  ];
  // Simple deterministic pick
  return patterns[(topic.length + 3) % patterns.length];
}



