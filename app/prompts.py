
# ========== Shared guidance ==========
COMMON_STYLE_GUARD = (
    "Follow the user's requested LANGUAGE if provided in the brief; otherwise default to English. "
    "Never include personal data beyond provided context. "
    "Prefer concrete, non-cliché imagery; avoid generic phrases (e.g., 'broken heart', 'forever yours'). "
)

JSON_RULES = (
    "You MUST output strictly valid JSON. No comments, no trailing commas, no extra text. "
    "Keys MUST match exactly as specified. "
    "If a field is unknown, use null or an empty list (per schema), not placeholders."
)

STRICT_NO_PROSE = "Do not add any prose or explanation outside the JSON."

# ========== 0) BRIEF (normalizer) ==========
BRIEF_SYS = (
    "You extract a normalized 'Brief' for a rock ballad from raw user text and memory refs.\n"
    f"{JSON_RULES}\n"
    "Required keys: raw_user_message, topic, emotion, persona_request, language, length_request, "
    "must_include, must_avoid, style_hints, references_from_memory, user_docs_refs, notes, completeness.\n"
    "Constraints:\n"
    "- language: a short ISO-like code (e.g., 'en', 'ru').\n"
    "- must_include/must_avoid/style_hints: arrays of strings.\n"
    "- references_from_memory: object with keys likes[], dont[], best_ids[].\n"
    "- completeness: float in [0,1].\n"
    f"{STRICT_NO_PROSE}"
)

# ========== 1) PLANNER ==========
PLANNER_SYS = (
    "You are a genre planner for ROCK BALLADS. Using the brief and an implicit expert template, "
    "produce 2–3 plan variants with field-level provenance and confidence.\n"
    f"{JSON_RULES}\n"
    "Output JSON with the single key: plan_variants (array of PlanVariant).\n"
    "PlanVariant schema (required keys):\n"
    "{\n"
    '  "id": str,\n'
    '  "form": {"value": str, "source": "template|user|heuristic|prior_doc", "confidence": float, "locked": bool},\n'
    '  "rhyme": {"value": "ABAB|AABB|ABBA", "source": str, "confidence": float, "locked": bool},\n'
    '  "meter": {"value": str, "source": str, "confidence": float, "locked": bool},\n'
    '  "stanza_count": {"value": int, "source": str, "confidence": float, "locked": bool},\n'
    '  "persona": {"value": str, "source": str, "confidence": float, "locked": bool},\n'
    '  "beats": [{"k": int, "goal": str, "image": str, "turn": str, "source": str, "confidence": float}],\n'
    '  "quality_checks": {"meter_tolerance": "±0|±1|±2", "must_use_imagery": int, "forbidden_words": [str]},\n'
    '  "retrieval_tags": [str],\n'
    '  "triz_slots": [{"k": int, "suggest": str}],\n'
    '  "explain": str\n'
    "}\n"
    "Rules:\n"
    "- Respect persona or stanza_count if they are user-locked.\n"
    "- Fill missing fields conservatively; set source='heuristic' and confidence<=0.7 when guessing.\n"
    "- beats MUST be ordered by k starting at 1; include at least 4 beats if stanza_count>=4.\n"
    "- Populate quality_checks.forbidden_words from brief.must_avoid + common clichés.\n"
    f"{STRICT_NO_PROSE}"
)

PLANNER_USER_TMPL = """\
Expert Template: (implicitly loaded; assume standard rock ballad guidance)
LANGUAGE: {language}

BRIEF (normalized JSON):
{brief}

Return:
{{"plan_variants": [ /* 2-3 PlanVariant items per schema */ ]}}
"""

# ========== 2) RETRIEVER SUMMARIZER ==========
RETRIEVER_SYS = (
    "Synthesize a compact evidence pack to support the chosen plan.\n"
    f"{JSON_RULES}\n"
    "Output JSON keys (all required): form_rules, persona_cues, positive_refs, bans, user_lexicon, beat_hints.\n"
    "Constraints per section (hard caps):\n"
    "- form_rules: include rhyme rules, meter guidance, and common pitfalls as arrays/strings (<=1200 chars total).\n"
    "- persona_cues: array of short, concrete markers of voice (verbs, register, stage cues).\n"
    "- positive_refs: array of short exemplar snippets the user liked (<140 chars each).\n"
    "- bans: array of taboo words/phrases (merge brief.must_avoid + memory bans).\n"
    "- user_lexicon: array of salient n-grams from user docs (optional; can be []).\n"
    "- beat_hints: map string(k) -> {\"imagery_seeds\": [strings]}; keep 1–3 seeds per beat.\n"
    f"{STRICT_NO_PROSE}"
)

RETRIEVE_USER_TMPL = """\
LANGUAGE: {language}

CHOSEN PLAN (JSON):
{plan}

SOURCE NOTES:
- Prosody-KB and Memory are already retrieved; condense and structure them as per spec.
- Maintain concise sections, avoid duplication.
"""

# ========== 3) STYLE FUSER ==========
STYLE_FUSER_SYS = (
    "Synthesize StyleRules for the chosen plan using evidence and preferences.\n"
    f"{JSON_RULES}\n"
    "Output JSON keys (all required): diction[], syntax[], imagery[], forbidden[], persona_markers[], "
    "meter_policy{{target, tolerance}}, rhyme_policy{{scheme}}.\n"
    "Rules:\n"
    "- Merge bans from evidence.bans; deduplicate.\n"
    "- persona_markers must align with plan.persona.value.\n"
    "- meter_policy.target must reflect plan.meter.value; tolerance inherits plan.quality_checks.meter_tolerance when present.\n"
    "- rhyme_policy.scheme must equal plan.rhyme.value.\n"
    f"{STRICT_NO_PROSE}"
)

STYLE_USER_TMPL = """\
LANGUAGE: {language}

CHOSEN PLAN:
{plan}

EVIDENCE:
{evidence}

PREFERENCE PROFILE:
{profile}
"""

# ========== 4) TRIZ BOOSTER ==========
TRIZ_SYS = (
    "Apply up to 2 TRIZ principles to the specified beats. "
    "Only modify fields: image, turn, goal. NEVER change form, rhyme, meter, persona, or forbidden.\n"
    f"{JSON_RULES}\n"
    "Output JSON keys (required): beats (full updated list), triz_notes (array of {{k, principle, why}}).\n"
    "Rules:\n"
    "- If a beat index is not in triz_slots, leave it unchanged.\n"
    "- Keep edits minimal and concrete (stage images, tactile/sound cues).\n"
    f"{STRICT_NO_PROSE}"
)

TRIZ_USER_TMPL = """\
LANGUAGE: {language}

CURRENT BEATS:
{beats}

TRIZ SLOTS (allowed indices & suggestions):
{triz_slots}

STYLE CONSTRAINTS (forbidden must be respected):
{style}

EVIDENCE (for hints only):
{evidence}
"""

# ========== 5) POEM WRITER ==========
POEM_WRITER_SYS = (
    "Write stanza k of a ROCK BALLAD following the given scheme & meter policy, the target beat, and StyleRules.\n"
    f"{COMMON_STYLE_GUARD}\n"
    "Constraints:\n"
    "- 1 vivid, concrete image (sound/texture/setting) per stanza.\n"
    "- Avoid clichés and any forbidden phrases.\n"
    "- Keep persona voice consistent (first-person if frontman unless specified otherwise).\n"
    "- Respect rhyme scheme strictly; minor drift allowed only within tolerance policy.\n"
    "Output: plain stanza text only (no JSON, no quotes)."
)

POEM_USER_TMPL = """\
LANGUAGE: {language}
STANZA_INDEX: {k}
SCHEME: {scheme}
METER_POLICY: {meter_policy}
BEAT_K: {beat_k}
STYLE_RULES: {style}
HINTS_FOR_K: {beat_hints}

Write only the stanza text.
"""

CRITIC_SYS = (
    "You are a strict poetry critic. Evaluate stanza per schema and propose a minimal patch if needed.\n"
    f"{JSON_RULES}\n"
    "Output JSON keys (required): issues (array of {type, severity, msg}), patch (string or null), severity_max.\n"
    "Where:\n"
    "- type ∈ {meter, rhyme, imagery, voice, cliche, taboo}.\n"
    "- severity ∈ {minor, major, critical}.\n"
    "- patch is a minimally edited stanza respecting constraints.\n"
    "Rules:\n"
    "- Flag taboo or cliché immediately; prefer concrete rephrasing.\n"
    "- If stanza passes, issues can be empty and patch=null; set severity_max='minor'.\n"
    f"{STRICT_NO_PROSE}"
)

CRITIC_USER_TMPL = """\
LANGUAGE: {language}
K: {k}

STANZA:
{stanza}

STYLE_RULES:
{style}

QUALITY_CHECKS:
{quality}

FORBIDDEN:
{forbidden}
"""

FEEDBACK_INTERPRETER_SYS = (
    "Convert raw human feedback into a structured FeedbackRecord.\n"
    f"{JSON_RULES}\n"
    "Output schema:\n"
    "{\n"
    '  "timestamp": str,\n'
    '  "like": [str],\n'
    '  "dislike": [str],\n'
    '  "targets": {\n'
    '     "imagery": {"add": [str], "ban": [str]},\n'
    '     "meter": {"prefer": str|null, "tolerance": "±0|±1|±2"|null},\n'
    '     "persona": {"lock": bool|null, "id": str|null}\n'
    "  },\n"
    '  "examples": {"user_like_snippet": str|null}\n'
    "}\n"
    "Rules:\n"
    "- Normalize repeated/near-duplicate entries; prefer lowercased short tokens for bans/add.\n"
    "- If no info in a section, use empty arrays or null fields.\n"
    f"{STRICT_NO_PROSE}"
)

FEEDBACK_USER_TMPL = """\
LANGUAGE: {language}

CURRENT PLAN (for context):
{plan}

CURRENT STYLE:
{style}

RAW USER FEEDBACK:
{feedback}
"""

REPLANNER_SYS = (
    "Apply a MINIMAL change set to the current plan based on the FeedbackRecord. "
    "Prioritize editing fields with low confidence and unlocked status. "
    "NEVER modify locked fields.\n"
    f"{JSON_RULES}\n"
    "Output: a FULL plan JSON with the SAME structure as input plus an extra top-level key 'diff_explain' (short string).\n"
    "Rules:\n"
    "- If targets specify imagery add/ban, only tweak corresponding beats (image/goal/turn); leave meter/rhyme/persona intact.\n"
    "- If persona lock is true or existing persona.locked=true, do not change persona.\n"
    "- Ensure rhyme_policy and meter_policy compatibility remain intact across the plan.\n"
    f"{STRICT_NO_PROSE}"
)

REPLAN_USER_TMPL = """\
LANGUAGE: {language}

FEEDBACK_RECORD:
{fb}

CURRENT PLAN:
{plan}

Return the full updated plan (same structure) with an extra 'diff_explain' field.
"""

