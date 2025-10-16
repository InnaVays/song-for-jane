# Song-for-Jane — Memory-Fueled PaE (Branch the Context, Not the Plan)

A DIY lyric writer demo that builds rock-ballad stanzas with human-in-the-loop feedback, personal memory, and a single upfront plan.
Key idea:

PaE skeleton; the fuel at every step is personal memory, not a static plan.

We branch the context, not the plan — cheap, adaptive, and easy to steer.

## What it does

1. Normalize your brief.

2. Call a Large model once to produce a Master Plan (form, meter/rhyme, persona, beats), a Style Policy, and a Toolcard (how to use tools).

3. For each stanza, build two tiny A/B contexts (exploit vs. explore) from:

- user Memory (likes, taboos, exemplars),

- User Docs (lexicon & imagery),

- Prosody KB (rules/pitfalls).

4. Pick A or B (cheap selector), write with a Medium model, apply zero-token guards (taboo/rhyme/length), optionally a Small patch.

5. Show to user → take feedback → ingest → embed → upsert → refresh preferences → next stanza.

6. Finalize when stanza_count is reached.

**One good plan supports many generations. Variety comes from context diversification, not costly re-planning.**

## Requirements

Python 3.10+ (3.11 recommended)

An OpenAI API key (.env)

## Quickstart (local)
```
# install deps & ensure indexes
make install
make ensure-stores

# start a session (will pause after showing stanza)
make run-mf THREAD=mf-demo-001 BRIEF="Write a night-train rock ballad with wet asphalt and a hard choice."

# continue same session with feedback (A/B or notes)
make run-mf THREAD=mf-demo-001 FEEDBACK="A; faster tempo; add image: neon puddles; ban: 'forever yours'"
make run-mf THREAD=mf-demo-001 FEEDBACK="ACCEPT"
```

The loop repeats until stanza_count → the final text prints.

** Add your data**

User Docs: put .txt / .md (≥ few hundred words recommended) in user_docs/.

Rebuild or auto-build on first run:

```
make ensure-stores
# or explicitly:
python app/indexing/build_kb_index.py --source kb/prosody_corpus --persist vectorstores/prosody --collection prosody
python app/indexing/build_memory_index.py --memory memory --persist vectorstores/memory --collection memory
```

## Configuration & model budget

- Large: used once at master_planner.

- Medium: writer drafts.

- Small: brief/context compression, A/B, feedback, patches.


## Why this approach

- Cheap: one Large call; the rest small/medium + guards.

- Personal: every step uses fresh memory/docs context.

- Controllable: user is the critic; immediate ingestion reshapes the very next step.

- Robust: plan is stable; we branch the context, not the plan.