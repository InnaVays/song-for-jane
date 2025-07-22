# Jane – Personal AI Co-Author

Jane is a AI assistant designed as a deeply personalized writing co-author.
Unlike generic assistants, Jane adapts to your voice, keeps memory across sessions, and supports creative brainstorming, rewriting, and fact-finding — all in one place.

## ✨ Core Modules

Jane routes every input into one of four modes:

- Brainstorm (jane/brainstorm/). Creative idea engine powered by multi-persona prompting and step-by-step reasoning. TRIZ principles (40 inventive patterns) will be plugged in later. Output: multiple fresh angles, hooks, and analogies for your draft or topic.

- Rewrite (jane/rewrite/). Learns your style from previous drafts stored in memory. Two outputs per draft:

 - v1_style_mine – rewritten strictly in your personal style.

 - v2_style_improved – rewritten with recommended improvements.

 Style retrieval: MongoDB Atlas Vector Search + LangChain.

 Future: LoRA fine-tuning (PEFT / Unsloth) via lorafy() hook.

- Research (jane/research/). Hybrid fact-gathering pipeline: First checks personal memory (vector DB). Then expands to web search (Tavily / SerpAPI). Combines results into bullet points with clear source labels: history (from your past notes) found (from the web). Uses LangChain RetrievalQA for orchestration.

- Other (jane/other/) / Lightweight free-chat mode. Replies conversationally while nudging you back toward one of the three main modules.

## 🚀 Quickstart

```
git clone https://github.com/InnaVays/song-for-jane.git
cd song-for-jane
pip install -r requirements.txt
```