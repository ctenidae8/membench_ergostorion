#!/usr/bin/env python3
"""
convert_membench.py
Converts membench seed_data.json biography and project records
into ergastorion ergon format (membench schema).

Generates per biography:
  erg-MEM-{id:04d}-IDN-V1  identity (who, where, what)
  erg-MEM-{id:04d}-CHR-V1  character (personality, lifestyle, preferences)
  erg-MEM-{id:04d}-LIF-V1  life events (history, fears, turning points)

Generates per project:
  erg-MEM-{2000+id:04d}-PRJ-V1  project spec
  erg-MEM-{2000+id:04d}-TME-V1  team composition

Usage:
  python3 convert_membench.py --bios membench_bios.json --projects membench_projects.json --out ./facts
"""

import json, re, os, hashlib, argparse
from datetime import date

TODAY = date.today().isoformat()

CLAN_COLORS = {
    "Vasquez-Okafor":   "vasquez-okafor",
    "Blackwood-Diallo": "blackwood-diallo",
    "Kowalski-Nair":    "kowalski-nair",
    "Lindqvist-Tanaka": "lindqvist-tanaka",
    "Mahmoud-Reyes":    "mahmoud-reyes",
}

def slugify(text, max_words=4):
    """Normalize text to a seed token."""
    if not text:
        return None
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text.strip())
    words = text.split("_")[:max_words]
    result = "_".join(w for w in words if w)
    return result if result else None

def extract_seeds(*items, max_words=3):
    """Extract and deduplicate seeds from a list of text values."""
    seeds = []
    seen = set()
    for item in items:
        if not item:
            continue
        # Multi-word items: split and slug each meaningful phrase
        for chunk in str(item).split("—"):
            s = slugify(chunk.strip(), max_words)
            if s and s not in seen and len(s) > 2:
                seeds.append(s)
                seen.add(s)
    return seeds

def fingerprint(subject, relationship, obj):
    raw = f"{subject}|{relationship}|{obj}"
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()[:16]

def bio_to_erga(b):
    erga = []
    bio_id = b["id"]
    name = b["name"]
    family = b.get("family", "")
    clan = CLAN_COLORS.get(family, slugify(family))

    # ── IDN ergon: identity / demographics / physical ───────────────────
    id_idn = f"erg-MEM-{bio_id:04d}-IDN-V1"
    age = b.get("age", "unknown")
    profession = b.get("profession", "")
    current_city = b.get("current_city", "")
    origin = b.get("origin", "")
    height = b.get("height", "")
    build = b.get("build", "")
    eye_color = b.get("eye_color", "")
    hair = b.get("hair", "")
    dist_feat = b.get("distinguishing_feature", "")
    style = b.get("clothing_style", "")
    nationality = b.get("nationality", "")
    ethnicity = b.get("ethnicity", "")
    pronouns = b.get("pronouns", "")

    idn_assertion = (
        f"{name} is a {age}-year-old {profession} "
        f"based in {current_city}, originally from {origin}. "
        f"Physical: {height}, {build}, {eye_color} eyes, {hair} hair. "
        f"Distinguishing: {dist_feat}."
    )

    idn_seeds = extract_seeds(
        name, family,
        profession, current_city, origin,
        height, build, eye_color, dist_feat,
        nationality, ethnicity, style
    )

    erga.append({
        "ergon_id": id_idn,
        "type": "fact",
        "desk": "identity",
        "assertion": idn_assertion,
        "subject": {"type": "person", "name": name, "aliases": [name.split()[0]]},
        "object": {"type": "location", "name": current_city},
        "relationship": "resides_in",
        "qualifiers": {
            "conditions": f"age {age}, origin: {origin}",
            "population": f"fictional synthetic character — membench bio {bio_id}"
        },
        "provenance": {
            "source_type": "gray_literature",
            "source_tier": "gray",
            "ref": f"membench/eval/step_1/seeds/bio_{bio_id}.md",
            "location": "section I — identification",
            "data_origin": "primary",
            "original_text": idn_assertion
        },
        "confidence": "strong",
        "clans": [clan],
        "seeds": idn_seeds,
        "integrity": {
            "claim_fingerprint": fingerprint(name, "resides_in", current_city),
            "corroborations": 0, "corroboration_refs": [], "conflicts": [],
            "slop_score": 0.0, "coi_flag": False
        },
        "chain_hints": [],
        "membench_ref": {"type": "bio", "id": bio_id},
        "version": 1,
        "created_at": TODAY,
        "producer": "MEMBENCH-CONVERTER-V1",
        "status": "draft"
    })

    # ── CHR ergon: character / personality / lifestyle / preferences ─────
    id_chr = f"erg-MEM-{bio_id:04d}-CHR-V1"
    personality = b.get("personality_core", "")
    personality2 = b.get("personality_secondary", "")
    humor = b.get("humor_style", "")
    catchphrase = b.get("catchphrase", "")
    comm_style = b.get("comm_style", "")
    nervous = b.get("nervous_habit", "")
    hidden = b.get("hidden_talent", "")
    fav_color = b.get("fav_color", "")
    fav_cuisine = b.get("fav_cuisine", "")
    comfort_food = b.get("comfort_food", "")
    go_to_drink = b.get("go_to_drink", "")
    fav_book = b.get("fav_book", "")
    fav_movie = b.get("fav_movie", "")
    fav_music = b.get("fav_music", "")
    guilty = b.get("guilty_pleasure", "")
    opinion = b.get("controversial_opinion", "")

    chr_assertion = (
        f"{name} is {personality}, {personality2}. "
        f"Humor: {humor}. Catchphrase: '{catchphrase}'. "
        f"Communication: {comm_style}. Nervous habit: {nervous}. "
        f"Favorites — color: {fav_color}, cuisine: {fav_cuisine}, "
        f"comfort food: {comfort_food}, drink: {go_to_drink}."
    )

    chr_seeds = extract_seeds(
        name, family, personality, catchphrase,
        humor, comm_style, nervous, hidden,
        fav_color, fav_cuisine, comfort_food, go_to_drink,
        fav_book, fav_movie, fav_music, guilty, opinion
    )

    erga.append({
        "ergon_id": id_chr,
        "type": "fact",
        "desk": "character",
        "assertion": chr_assertion,
        "subject": {"type": "person", "name": name},
        "object": {"type": "trait", "name": personality},
        "relationship": "exhibits",
        "qualifiers": {
            "conditions": f"lifestyle and personality profile",
            "population": f"fictional — membench bio {bio_id}"
        },
        "provenance": {
            "source_type": "gray_literature",
            "source_tier": "gray",
            "ref": f"membench/eval/step_1/seeds/bio_{bio_id}.md",
            "location": "sections VI, IX — personal identity, supplementary",
            "data_origin": "primary",
            "original_text": chr_assertion
        },
        "confidence": "strong",
        "clans": [clan],
        "seeds": chr_seeds,
        "integrity": {
            "claim_fingerprint": fingerprint(name, "exhibits", personality),
            "corroborations": 0, "corroboration_refs": [], "conflicts": [],
            "slop_score": 0.0, "coi_flag": False
        },
        "chain_hints": [{"from_desk": "identity", "to_desk": "character",
                         "via_seed": slugify(name), "target_ergon": id_idn,
                         "note": f"Same character — {name}"}],
        "membench_ref": {"type": "bio", "id": bio_id},
        "version": 1,
        "created_at": TODAY,
        "producer": "MEMBENCH-CONVERTER-V1",
        "status": "draft"
    })

    # ── LIF ergon: life events / history / psychology ────────────────────
    id_lif = f"erg-MEM-{bio_id:04d}-LIF-V1"
    first_job = b.get("first_job", "")
    career_change = b.get("career_change", "")
    school_type = b.get("school_type", "")
    degree = b.get("degree", "")
    event1 = b.get("life_event_1", "")
    event2 = b.get("life_event_2", "")
    event3 = b.get("life_event_3", "")
    turning = b.get("turning_point", "")
    regret = b.get("biggest_regret", "")
    proudest = b.get("proudest_moment", "")
    fear = b.get("fear", "")
    dream = b.get("recurring_dream", "")
    medical = b.get("medical_condition", "")
    diet = b.get("diet_type", "")
    exercise = b.get("exercise_routine", "")
    pet = b.get("pet", "")
    vehicle = b.get("vehicle", "")
    prized = b.get("prized_possession", "")
    financial = b.get("financial", "")
    salary = b.get("salary_range", "")
    achievement = b.get("professional_achievement", "")

    lif_assertion = (
        f"{name} — background: {school_type}, {degree}. "
        f"Career: started as {first_job}, pivoted via {career_change}. "
        f"Key events: {event1}; {event2}; {event3}. "
        f"Turning point: {turning}. "
        f"Proudest: {proudest}. Biggest regret: {regret}. "
        f"Fear: {fear}. Professional achievement: {achievement}."
    )

    lif_seeds = extract_seeds(
        name, family,
        first_job, career_change, school_type, degree,
        event1, event2, event3, turning,
        proudest, regret, fear, dream,
        medical, diet, exercise, pet, vehicle, prized, financial, salary
    )

    erga.append({
        "ergon_id": id_lif,
        "type": "fact",
        "desk": "biography",
        "assertion": lif_assertion,
        "subject": {"type": "person", "name": name},
        "object": {"type": "event", "name": turning},
        "relationship": "experienced",
        "qualifiers": {
            "conditions": "biographical history and psychological profile",
            "population": f"fictional — membench bio {bio_id}"
        },
        "provenance": {
            "source_type": "gray_literature",
            "source_tier": "gray",
            "ref": f"membench/eval/step_1/seeds/bio_{bio_id}.md",
            "location": "sections III, IV, VIII — early life, career, psychological",
            "data_origin": "primary",
            "original_text": lif_assertion
        },
        "confidence": "strong",
        "clans": [clan],
        "seeds": lif_seeds,
        "integrity": {
            "claim_fingerprint": fingerprint(name, "experienced", turning),
            "corroborations": 0, "corroboration_refs": [], "conflicts": [],
            "slop_score": 0.0, "coi_flag": False
        },
        "chain_hints": [
            {"from_desk": "identity", "to_desk": "biography",
             "via_seed": slugify(name), "target_ergon": id_idn,
             "note": f"Same character — {name}"},
            {"from_desk": "character", "to_desk": "biography",
             "via_seed": slugify(family), "target_ergon": id_chr,
             "note": f"{family} clan cross-reference"}
        ],
        "membench_ref": {"type": "bio", "id": bio_id},
        "version": 1,
        "created_at": TODAY,
        "producer": "MEMBENCH-CONVERTER-V1",
        "status": "draft"
    })

    return erga


def project_to_erga(p):
    erga = []
    proj_id = p["id"]
    base_id = 2000 + proj_id
    pname = p.get("project_name", f"Project-{proj_id}")
    ptype = p.get("project_type", "")
    company = p.get("company_name", "")
    desc = p.get("project_description", "")
    budget = p.get("budget", "")
    team_size = p.get("team_size", "")
    lead = p.get("lead_name", "")
    lead_role = p.get("lead_role", "")
    m1 = p.get("member_1_name", "")
    m1r = p.get("member_1_role", "")
    m2 = p.get("member_2_name", "")
    m2r = p.get("member_2_role", "")
    m3 = p.get("member_3_name", "")
    m3r = p.get("member_3_role", "")
    tech = p.get("tech_stack", "")
    arch = p.get("architecture_pattern", "")
    deploy = p.get("deployment_method", "")
    industry = p.get("industry", "")
    blocker = p.get("current_blocker", "")
    debt = p.get("technical_debt", "")
    linked_ids = p.get("linked_bio_ids") or []

    # ── PRJ ergon: project specification ─────────────────────────────────
    id_prj = f"erg-MEM-{base_id:04d}-PRJ-V1"
    prj_assertion = (
        f"Project {pname} ({ptype}) at {company}: {desc}. "
        f"Budget: {budget}. Team: {team_size}. "
        f"Tech stack: {tech}. Architecture: {arch}. "
        f"Current blocker: {blocker}. Technical debt: {debt}."
    )

    prj_seeds = extract_seeds(
        pname, company, ptype, industry,
        tech, arch, deploy, budget, blocker, debt,
        lead
    )

    # Clans from linked bio IDs (need to look up — pass as string refs for now)
    clans = []
    for lid in linked_ids:
        clans.append(f"linked_bio_{lid}")

    erga.append({
        "ergon_id": id_prj,
        "type": "fact",
        "desk": "technical",
        "assertion": prj_assertion,
        "subject": {"type": "project", "name": pname},
        "object": {"type": "organization", "name": company},
        "relationship": "belongs_to",
        "qualifiers": {
            "conditions": f"industry: {industry}",
            "population": f"fictional — membench project {proj_id}"
        },
        "provenance": {
            "source_type": "gray_literature",
            "source_tier": "gray",
            "ref": f"membench/eval/step_1/seeds/project_{proj_id}.md",
            "location": "executive summary, technical architecture",
            "data_origin": "primary",
            "original_text": prj_assertion
        },
        "confidence": "strong",
        "clans": clans,
        "seeds": prj_seeds,
        "integrity": {
            "claim_fingerprint": fingerprint(pname, "belongs_to", company),
            "corroborations": 0, "corroboration_refs": [], "conflicts": [],
            "slop_score": 0.0, "coi_flag": False
        },
        "chain_hints": [
            {"from_desk": "technical", "to_desk": "organization",
             "via_seed": slugify(lead), "target_ergon": f"erg-MEM-{2000+proj_id:04d}-TME-V1",
             "note": f"Lead: {lead}"}
        ],
        "membench_ref": {"type": "project", "id": proj_id, "linked_bio_ids": linked_ids},
        "version": 1,
        "created_at": TODAY,
        "producer": "MEMBENCH-CONVERTER-V1",
        "status": "draft"
    })

    # ── TME ergon: team composition ───────────────────────────────────────
    id_tme = f"erg-MEM-{base_id:04d}-TME-V1"
    tme_assertion = (
        f"{lead} ({lead_role}) leads {pname} at {company} with: "
        f"{m1} ({m1r}), {m2} ({m2r}), {m3} ({m3r}). "
        f"Team dynamic: {p.get('team_dynamic', '')}."
    )

    tme_seeds = extract_seeds(
        pname, company, lead, m1, m2, m3,
        p.get("team_dynamic", "")
    )

    erga.append({
        "ergon_id": id_tme,
        "type": "fact",
        "desk": "organization",
        "assertion": tme_assertion,
        "subject": {"type": "person", "name": lead},
        "object": {"type": "project", "name": pname},
        "relationship": "leads",
        "qualifiers": {
            "conditions": f"team of {team_size}",
            "population": f"fictional — membench project {proj_id}"
        },
        "provenance": {
            "source_type": "gray_literature",
            "source_tier": "gray",
            "ref": f"membench/eval/step_1/seeds/project_{proj_id}.md",
            "location": "meeting notes, budget breakdown",
            "data_origin": "primary",
            "original_text": tme_assertion
        },
        "confidence": "strong",
        "clans": clans,
        "seeds": tme_seeds,
        "integrity": {
            "claim_fingerprint": fingerprint(lead, "leads", pname),
            "corroborations": 0, "corroboration_refs": [], "conflicts": [],
            "slop_score": 0.0, "coi_flag": False
        },
        "chain_hints": [
            {"from_desk": "organization", "to_desk": "technical",
             "via_seed": slugify(pname), "target_ergon": id_prj,
             "note": f"Team for project {pname}"}
        ],
        "membench_ref": {"type": "project", "id": proj_id, "linked_bio_ids": linked_ids},
        "version": 1,
        "created_at": TODAY,
        "producer": "MEMBENCH-CONVERTER-V1",
        "status": "draft"
    })

    return erga


def build_fact_index(erga):
    """Build a fact_index.json compatible with ergastorion tooling."""
    index = {"version": "membench-v1", "generated_at": TODAY, "erga": []}
    for e in erga:
        index["erga"].append({
            "ergon_id": e["ergon_id"],
            "desk": e["desk"],
            "assertion": e["assertion"][:120],
            "seeds": e["seeds"],
            "clans": e.get("clans", []),
            "confidence": e["confidence"],
            "status": e["status"],
            "membench_ref": e.get("membench_ref", {})
        })
    return index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bios", default="/tmp/membench_bios.json")
    parser.add_argument("--projects", default="/tmp/membench_projects.json")
    parser.add_argument("--out", default="/tmp/membench_facts")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    with open(args.bios) as f:
        bios = json.load(f)
    with open(args.projects) as f:
        projects = json.load(f)

    print(f"Converting {len(bios)} biographies and {len(projects)} projects...")

    all_erga = []

    # Biographies
    for b in bios:
        erga = bio_to_erga(b)
        all_erga.extend(erga)
        for e in erga:
            path = os.path.join(args.out, f"{e['ergon_id']}.json")
            with open(path, "w") as f:
                json.dump(e, f, indent=2)

    # Projects
    for p in projects:
        erga = project_to_erga(p)
        all_erga.extend(erga)
        for e in erga:
            path = os.path.join(args.out, f"{e['ergon_id']}.json")
            with open(path, "w") as f:
                json.dump(e, f, indent=2)

    # Fact index
    index = build_fact_index(all_erga)
    with open(os.path.join(args.out, "fact_index_membench.json"), "w") as f:
        json.dump(index, f, indent=2)

    print(f"Generated {len(all_erga)} erga → {args.out}")
    print(f"  Bio erga:     {len(bios) * 3}")
    print(f"  Project erga: {len(projects) * 2}")

    # Clan summary
    from collections import Counter
    clan_counts = Counter()
    for e in all_erga:
        for c in e.get("clans", []):
            clan_counts[c] += 1
    print(f"\nClan distribution:")
    for clan, count in clan_counts.most_common():
        if not clan.startswith("linked_bio"):
            print(f"  {clan}: {count} erga")

if __name__ == "__main__":
    main()
