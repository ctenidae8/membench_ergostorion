# membench — Ergastorion Conversion

**Source:** [chalie-ai/membench](https://github.com/chalie-ai/membench/tree/main/eval/step_1/seeds)  
**Converted:** 2026-04-25  
**Schema:** `fact_schema_membench.json`

---

## What this is

A conversion of the membench synthetic character benchmark dataset into ergastorion ergon format.

membench generates 475 richly-detailed fictional documents — biographical profiles, technical project specs, and first-person essays — to benchmark an AI system's ability to identify and recall specific characters from partial information. The task is: given a fragment ("the person who starts every sentence with 'Listen' and sends emails without greetings"), retrieve the correct character from the store.

The ergastorion architecture is structurally identical to this task. The conversion maps membench's character data to ergon facts, with family clans serving as the retrieval clustering axis — the direct analog of biological guilds in the main Aeris store.

---

## Coverage

| Source | Records | Erga generated | Notes |
|--------|--------:|---------------:|-------|
| Biographies | 150 | 450 (3 per character) | All 150 complete |
| Project specs | 17 | 34 (2 per project) | Partial — seed_data.json truncated |
| Articles | 25 | — | Not yet converted (no structured seed data) |
| **Total** | **192** | **484** | |

To extend project coverage: download `eval/step_1/seed_data.json` locally, run `convert_membench.py --projects your_full_projects.json`.

---

## Clan structure (= guilds)

All 150 characters belong to one of five family clans. Each clan has exactly 30 members. Clans serve as the retrieval clustering axis — the same role biological guilds play in the Aeris store.

| Clan | Members | Ergon count |
|------|--------:|------------:|
| `vasquez-okafor` | 30 | 90 |
| `blackwood-diallo` | 30 | 90 |
| `kowalski-nair` | 30 | 90 |
| `lindqvist-tanaka` | 30 | 90 |
| `mahmoud-reyes` | 30 | 90 |

Cross-clan connections exist through project specs: `linked_bio_ids` on each project record names characters from different clans who collaborate on the same project. These are encoded in `chain_hints`.

---

## Ergon types per character

Each of the 150 biography records produces three erga:

**IDN — Identity**  
`desk: identity` | `relationship: resides_in`  
Who they are, where they live, what they look like, what they do. High-density seed coverage of distinguishing physical and demographic attributes.  
*Seeds include:* name slug, family slug, profession, current city, origin city, height, build, eye color, distinguishing feature.

**CHR — Character**  
`desk: character` | `relationship: exhibits`  
Personality, lifestyle, preferences, verbal tics, humor style. These are the retrieval targets for "voice-based" identification — the kind of clue that appears in article_* files.  
*Seeds include:* catchphrase/verbal tic, humor style, communication style, nervous habit, favorite color, cuisine, comfort food, drink, book, movie, music, guilty pleasure, controversial opinion.

**LIF — Life events**  
`desk: biography` | `relationship: experienced`  
Background, education, career history, life events, turning point, fears, regrets, proudest moment. These are the retrieval targets for "backstory-based" identification.  
*Seeds include:* first job, career change, school type, degree, three life events, turning point, proudest moment, biggest regret, fear, medical condition, diet, exercise, pet, vehicle, prized possession.

---

## Ergon types per project

**PRJ — Project specification**  
`desk: technical` | `relationship: belongs_to`  
Project name, type, company, description, budget, team size, tech stack, architecture, current blocker, technical debt.

**TME — Team composition**  
`desk: organization` | `relationship: leads`  
Lead character, team members, roles, team dynamic. Cross-references to linked bio IDs via `chain_hints`.

---

## Benchmark usage

The benchmark task is character identification: given a fragment from a bio or article, return the correct character's ergon(s).

**Step 1 — Seed extraction from query fragment**  
Extract candidate seed terms from the test query. Example: "the technician who starts emails without greetings and can solve a Rubik's cube in under 90 seconds" → candidate seeds: `renewable_energy_technician`, `curt_emails_no`, `can_solve_a`.

**Step 2 — Seed lookup against fact_index_membench.json**  
Match candidate seeds against the index. Seeds are designed to be distinctive — most clue sets should return ≤5 candidate erga.

**Step 3 — Character identification**  
The matching ergon's `membench_ref.id` identifies the character. Cross-check IDN + CHR + LIF erga for the same id to confirm.

**Step 4 — Recall test**  
Once identified, the full ergon set for that character provides ground-truth facts for recall testing.

---

## Files

```
membench/
  README.md                     this file
  fact_schema_membench.json     schema for all MEM-namespace erga
  convert_membench.py           conversion script (re-runnable for full dataset)
  membench_bios.json            structured seed data for 150 characters
  membench_projects.json        structured seed data for 17 projects (partial)
  facts/
    erg-MEM-0000-IDN-V1.json   Wyatt Vasquez-Okafor — identity
    erg-MEM-0000-CHR-V1.json   Wyatt Vasquez-Okafor — character
    erg-MEM-0000-LIF-V1.json   Wyatt Vasquez-Okafor — life events
    erg-MEM-0001-IDN-V1.json   bio_1 — identity
    ...
    erg-MEM-2000-PRJ-V1.json   Project Aqueduct — spec
    erg-MEM-2000-TME-V1.json   Project Aqueduct — team
    ...
    fact_index_membench.json    flat lookup index (id, desk, seeds, clans, assertion)
```

---

## Extending to full dataset

```bash
# 1. Download the full seed_data.json from membench
curl -o seed_data.json https://raw.githubusercontent.com/chalie-ai/membench/main/eval/step_1/seed_data.json

# 2. Extract bios and projects
python3 -c "
import json
with open('seed_data.json') as f: d = json.load(f)
with open('membench_bios.json', 'w') as f: json.dump(d['biographies'], f, indent=2)
with open('membench_projects.json', 'w') as f: json.dump(d['project_specs'], f, indent=2)
print(f'Bios: {len(d[\"biographies\"])}, Projects: {len(d[\"project_specs\"])}')
"

# 3. Run converter
python3 convert_membench.py --bios membench_bios.json --projects membench_projects.json --out facts/
```

For articles: each `article_*.md` has no structured seed record. Erga can be extracted via LLM (prompt: extract voice markers and key claims as seeds) or by adding an article section to the conversion script.
