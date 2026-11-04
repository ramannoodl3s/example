# StudyForge: Design Plan (DRAFT, awaiting approval)

## 1. Goal

You type in a certification, tool or skill (for example "AWS Certified AI Practitioner", "Azure AI-900", "PyTorch" or "LangChain"). StudyForge then:

1. **Compares** the top 5 free tutorial sites for that topic and ranks them.
2. **Pulls** the relevant lessons from each site.
3. **Organizes** them into one merged, de-duplicated curriculum.
4. **Generates** study material in three modes: **Reading Path**, **Flashcards with spaced repetition** and **Practice Quizzes / Mock Exams**.

Everything runs locally: a Python web app in your browser, with AI from a **local model through Ollama**. There are no API costs and your data stays on your machine.

---

## 2. Architecture

```
 Browser UI (localhost:8000)
   │  Topic search · Site comparison · Reading Path · Flashcards · Quizzes · Progress
   ▼
 FastAPI backend ───────────────────────────────────────────────┐
   │                                                            │
   ├─ Source Registry   curated list of free sites + adapters   │
   ├─ Ranker            scores sites per topic → top 5          │
   ├─ Collector         fetch → extract → cache (polite)        │
   ├─ Organizer         chunk → embed → dedupe → map to         │
   │                    exam objectives / topic outline         │
   ├─ Generator         Ollama: summaries, flashcards, quizzes  │
   └─ Study Engine      FSRS scheduling, quiz scoring, progress │
   ▼                                                            │
 SQLite (+ sqlite-vec for embeddings)   ◄───────────────────────┘
 Ollama (local LLM + embedding model)
```

### Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.12, FastAPI | Best fit for scraping and AI work, async |
| Frontend | Jinja2 templates + HTMX + Tailwind | Interactive with no separate JS build step; easy to maintain |
| Storage | SQLite + `sqlite-vec` | One file, nothing extra to install |
| Fetching | `httpx` + `trafilatura`; Playwright only when a site needs JavaScript | Clean article/lesson text extraction |
| LLM | Ollama: **`qwen3:14b`** (Q4_K_M, about 9.3 GB), context `num_ctx=32768`, with `OLLAMA_FLASH_ATTENTION=1` and `OLLAMA_KV_CACHE_TYPE=q8_0` | Strongest model that fits on an RTX 5070 Ti (16 GB) with room for a 32K context, about 14 GB in total. Configurable in `config.py`. |
| Embeddings | Ollama `nomic-embed-text` | Fast, local, good for de-duplication and topic mapping |
| Spaced repetition | `fsrs` (Free Spaced Repetition Scheduler) | Modern algorithm, better than Anki's older SM-2 |
| Packaging | `uv` for dependencies; `start.ps1` one-click launcher | Simple Windows setup |

---

## 3. Components

### 3.1 Source Registry (curated list)
A YAML file (`sources.yaml`) of vetted free sites. Each site gets a small **adapter** that knows how to search its catalog and extract a lesson. Starting candidates:

| Site | Strength | Access method |
|---|---|---|
| Microsoft Learn | Azure AI certs (AI-900, AI-102) | Official public Learn Catalog API |
| Google Cloud Skills Boost / Google ML Crash Course | GCP ML, general ML | Public course pages |
| AWS Skill Builder (free tier) / AWS docs | AWS AI and ML certs | Public pages and docs |
| freeCodeCamp | Programming, ML with Python | Public curriculum and news articles |
| Kaggle Learn | Hands-on ML and data science | Public course pages |
| Hugging Face Learn | LLMs, NLP, transformers | Public course pages (open source) |
| DeepLearning.AI short courses | GenAI topics | Catalog metadata and links only |
| Official project docs/tutorials (PyTorch, TensorFlow, LangChain…) | Tool-specific learning | Public docs |
| YouTube | Video lessons | Metadata, plus **uploader-created captions only**. Auto-generated (ASR) captions are always rejected, and videos without manual captions are listed as links only. |

**Adding a site** means writing one adapter class and adding one YAML entry. A generic fallback adapter covers simple sites.

### 3.1a Manual Site Utility
You can add sites yourself, outside the automatic top 5:
- **UI:** a "My Sites" page to add, edit, enable or disable, and delete sites (name, base URL, optional search URL pattern, and tags such as `aws` or `ml`). You can also **pin** a site to a topic so it's always included next to the top 5, or **exclude** a site from a topic.
- **CLI:** `studyforge sites add <url> --name ... --tags ... [--pin-topic ...]`, plus `sites list`, `sites remove` and `sites pin`.
- Manual sites use the generic adapter. They're still scored, and the score is shown on the comparison page, but pinned sites are always included.
- They're stored in the DB with `origin=manual`. The curated `sources.yaml` entries have `origin=curated`.

### 3.2 Ranker: choosing the top 5 for a topic
Each candidate site gets a score of 0–100 per topic:

- **Coverage (35%)**: share of the topic outline or exam objectives its content covers
- **Depth (20%)**: amount and length of relevant lessons
- **Cert alignment (15%)**: official or exam-mapped content scores higher
- **Freshness (15%)**: last-updated dates
- **Free completeness (10%)**: fully free, or partly paywalled
- **Hands-on (5%)**: labs and exercises available

The **Site Comparison** page shows a side-by-side table with the score breakdown, and you can override the picks manually.

### 3.3 Collector
- Fetch, extract the main text and code blocks, and save them with their source URL.
- **Polite by default:** follows `robots.txt`, makes at most 1 request every few seconds per site, uses a local cache (re-fetches only when stale) and a clear User-Agent.
- Uses official APIs or catalogs where they exist (for example Microsoft Learn).
- Content is stored for **personal study use**. The UI always links back to the original source, and excerpts and summaries are shown rather than republished copies.
- Some sites (Coursera, DeepLearning.AI) don't allow scraping. Their adapters store only catalog metadata and links.

### 3.4 Organizer
1. **Builds a backbone outline.** For a certification, this is the official exam skills outline or objectives. For a tool or skill, the LLM drafts an outline and you can edit it.
2. **Chunks** the collected content into sections and **embeds** each one.
3. **Maps** each chunk to the closest outline node.
4. **De-duplicates** near-identical explanations across sites, keeping the best one and listing the others as alternate sources.
5. **Orders** content from beginner to advanced within each module.

### 3.5 Generator (local LLM)
- **Summaries**: a short explanation for each outline node, with citations to the source chunks.
- **Flashcards**: term/definition, concept/question and code-snippet cards.
- **Quiz questions**: multiple choice in exam style, with an explanation and a source link for each answer.
- Prompts are grounded only in the collected content, which reduces made-up facts.
- Outputs are cached, so nothing is regenerated unless you ask.

### 3.6 Study Engine: the three study modes
1. **Reading Path**: an ordered, module-by-module curriculum. Each node has a summary, the best source excerpt, links to alternate sources and a "mark complete" control.
2. **Flashcards**: FSRS scheduling, with Again/Hard/Good/Easy grading, a daily review queue, and filters by module.
3. **Practice Quizzes / Mock Exams**: quick quizzes per module, a full mock exam (timed, weighted by exam objective), review of wrong answers, and an automatic flashcard for each question you miss.

**Progress dashboard**: completion per module, flashcard retention, quiz scores over time, and a list of weak areas.

---

## 4. Data model (SQLite)

```
topics(id, name, kind[cert|tool|skill], created_at)
outline_nodes(id, topic_id, parent_id, title, weight, order)
sources(id, name, base_url, search_url_pattern, adapter, origin[curated|manual], tags_json, enabled)
topic_source_overrides(topic_id, source_id, mode[pin|exclude])
site_scores(topic_id, source_id, score, breakdown_json, selected)
documents(id, source_id, url, title, fetched_at, content_hash, text)
chunks(id, document_id, outline_node_id, text, embedding, is_canonical)
summaries(outline_node_id, text, citations_json)
flashcards(id, topic_id, outline_node_id, front, back, source_chunk_id, fsrs_state_json, due_at)
quiz_questions(id, topic_id, outline_node_id, stem, choices_json, answer, explanation, source_chunk_id)
quiz_attempts(id, topic_id, mode, started_at, score, answers_json)
progress(outline_node_id, completed_at)
```

---

## 5. Project layout

```
example/
├─ studyforge/
│  ├─ app.py              FastAPI entry point
│  ├─ config.py           settings (model names, rate limits)
│  ├─ db.py / models.py
│  ├─ sources/            registry + one adapter per site
│  ├─ ranker.py
│  ├─ collector.py
│  ├─ organizer.py
│  ├─ generator/          prompts + Ollama client
│  ├─ study/              fsrs scheduling, quizzes, progress
│  └─ web/                templates/ + static/
├─ sources.yaml
├─ tests/
├─ start.ps1
├─ pyproject.toml
└─ README.md
```

---

## 6. Build phases

| Phase | Deliverable |
|---|---|
| **0. Skeleton** | Repo, FastAPI app, DB, Ollama health check, `start.ps1` |
| **1. Sources + Collector** | Registry, 3 adapters (MS Learn, freeCodeCamp, Hugging Face), caching and politeness |
| **2. Ranker + Comparison page** | Score and compare sites for a topic; manual override |
| **3. Organizer + Reading Path** | Outline, embedding, de-duplication, mapping; first usable study mode |
| **4. Flashcards** | Generation and FSRS review UI |
| **5. Quizzes / Mock exams** | Generation, timed mock exam, review of wrong answers |
| **6. Remaining adapters + dashboard** | Other sites, progress dashboard, polish |

Each phase ends with tests and a commit pushed to `origin/main`, or to a feature branch with a PR if you prefer.

---

## 7. Risks and mitigations

- **Site layouts change or block scrapers.** Adapters are isolated, prefer official APIs, use the generic fallback adapter, and keep cached copies.
- **Terms of service.** Personal use only, robots.txt respected, metadata-only adapters for restrictive sites, and every item links back to its source.
- **Local model quality.** Prompts stay grounded in source text, every claim cites its source, and you can edit or flag bad cards and questions.
- **Slow generation on smaller GPUs.** Generation runs as a background job with a progress bar, and results are cached.

---

## 8. Decisions (approved 2026-11-03)

1. **GPU:** RTX 5070 Ti, 16 GB → `qwen3:14b` plus a 32K context (see the stack table).
2. **First target:** **AWS Certified AI Practitioner (AIF-C01)**. The exam guide's 5 domains are the outline backbone and the first end-to-end test case.
3. **Git workflow:** feature branches (`feature/phase-N-...`) with PRs into `main`.
4. **Sites:** curated list plus the Manual Site Utility (3.1a).
5. **YouTube:** only uploader-created captions; auto-generated ones are rejected.
6. **Who builds what:** Kimi Code writes the code in a visible terminal window. Claude supervises, reviews the diffs, runs the tests, and handles git and PRs.
