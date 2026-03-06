import os

import pandas as pd

# ============================================================
# ESTRAZIONE CORRETTA DEL prog_id
# ============================================================


def extract_prog_id(full_id):
    full_id = str(full_id).strip()

    if "_" not in full_id:
        return "unknown", full_id.replace(".c", "")

    left, right = full_id.split("_", 1)

    if right.endswith(".c"):
        right = right[:-2]

    return left, right  # (year, prog_id_clean)


# ============================================================
# STRATIFICAZIONE PER TOPIC SCORE
# ============================================================


def stratify_score(score):
    if score <= 3:
        return "low"
    if score <= 7:
        return "medium"
    return "high"


# ============================================================
# SELEZIONE PROGRAMMI: 3 PER TOPIC PER TEMA (NO DUPLICATI)
# ============================================================


def select_programs_topicwise(
    gold_scores_csv,
    target_per_topic=1,
    results_path="results/selected_programs_for_gold_evidences.csv",
):
    df = pd.read_csv(gold_scores_csv)

    # Estrai year e prog_id pulito
    years = []
    new_prog_ids = []

    for pid in df["prog_id"]:
        year, pure_id = extract_prog_id(pid)
        year = year.split("-")[0]  # mantieni solo l'anno
        years.append(year)
        new_prog_ids.append(pure_id)

    df["year"] = years
    df["prog_id_clean"] = new_prog_ids

    topic_cols = [c for c in df.columns if c.startswith("topic")]
    if not topic_cols:
        raise ValueError("Nessuna colonna 'topicX' trovata nel CSV.")

    unique_years = df["year"].unique()
    print(f"[INFO] Temi trovati: {unique_years}")

    selected_rows = []
    used_prog_ids = set()  # <-- evita ripetizioni

    # ============================================================
    # PER OGNI TEMA × PER OGNI TOPIC → LOW/MEDIUM/HIGH
    # ============================================================

    for year in unique_years:
        df_year = df[df["year"] == year]
        print(f"\n[INFO] Elaboro tema {year}…")

        for topic in topic_cols:
            print(f"  - Topic: {topic}")

            topic_scores = df_year[["prog_id_clean", "year", topic]].copy()
            topic_scores["stratum"] = topic_scores[topic].apply(stratify_score)

            chosen_for_topic = []

            # LOW → MEDIUM → HIGH
            for category in ["low", "medium", "high"]:
                # Filtra per fascia
                group = topic_scores[topic_scores["stratum"] == category]

                # Escludi quelli già scelti
                group = group[~group["prog_id_clean"].isin(used_prog_ids)]

                if group.empty:
                    print(
                        f"    [WARN] Nessun programma {category} disponibile per {topic} nel tema {year}"
                    )
                    continue

                n_take = min(target_per_topic, len(group))

                take = group.sample(n=n_take, random_state=42)

                # Aggiorna set
                for pid in take["prog_id_clean"]:
                    used_prog_ids.add(pid)

                chosen_for_topic.append(take)

            # Unisci low+med+high del topic del tema
            if chosen_for_topic:
                selected_rows.append(pd.concat(chosen_for_topic))

    # ============================================================
    # RISULTATO FINALE (ORA ZERO DUPLICATI SEMPRE)
    # ============================================================

    if not selected_rows:
        raise ValueError("Nessun programma è stato selezionato. Controllare i dati.")

    selected = pd.concat(selected_rows)
    selected = selected.sort_values(by=["year", "prog_id_clean"])

    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    selected.to_csv(results_path, index=False)

    print("\n[SUCCESS] Selezione completata.")
    print(
        f"[INFO] Programmi selezionati: {len(selected)} (attesi: {len(unique_years) * len(topic_cols) * 3})"
    )
    print(f"[INFO] Risultato salvato in: {results_path}")

    return selected


if __name__ == "__main__":
    select_programs_topicwise(
        gold_scores_csv="gold/human_scores.csv",
        target_per_topic=1,
        results_path="analysis/results/selected_programs_for_gold_evidences.csv",
    )
