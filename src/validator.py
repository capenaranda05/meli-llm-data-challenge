import re
from pathlib import Path
from typing import List, Dict, Any, Set

def tokenize_ngrams(text: str, n: int = 3) -> Set[str]:
    words = re.findall(r"[a-z0-9áéíóúñ_]{2,}", text.lower())
    if len(words) < n:
        return set(words)
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}

def jaccard_similarity(s1: Set[str], s2: Set[str]) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

def compute_lexical_grounding(answer: str, chunk_content: str) -> float:
    stopwords = {
        "the", "and", "for", "that", "this", "with", "from", "are", "was", "not", "does", "specify",
        "documentation", "service", "according", "section", "para", "con", "los", "las", "del", "una",
        "por", "que", "como", "según", "documentación", "servicio", "especifica", "sección", "está"
    }
    ans_tokens = {
        t for t in re.findall(r"[a-z0-9áéíóúñ_/-]{3,}", answer.lower())
        if t not in stopwords
    }
    if not ans_tokens:
        return 1.0
    chunk_lower = chunk_content.lower()
    matched = sum(1 for t in ans_tokens if t in chunk_lower)
    return round(matched / len(ans_tokens), 4)

def validate_datasets(
    docs_raw_dir: Path,
    chunks_by_id: Dict[str, Any],
    cpt_data: List[Dict[str, Any]],
    train_sft: List[Dict[str, Any]],
    eval_in: List[Dict[str, Any]],
    eval_ood: List[Dict[str, Any]]
) -> Dict[str, Any]:
    all_sft = train_sft + eval_in + eval_ood
    
    missing_files = 0
    invalid_lines = 0
    for row in all_sft:
        tr = row.get("traceability", {})
        sf = docs_raw_dir / tr.get("source_file", "")
        if not sf.exists():
            missing_files += 1
        if tr.get("line_start", 0) < 1 or tr.get("line_end", 0) < tr.get("line_start", 0):
            invalid_lines += 1
            
    train_chunks = {r["traceability"]["chunk_id"] for r in train_sft}
    eval_in_chunks = {r["traceability"]["chunk_id"] for r in eval_in}
    eval_ood_chunks = {r["traceability"]["chunk_id"] for r in eval_ood}
    
    train_services = {r["traceability"]["service"] for r in train_sft}
    ood_services = {r["traceability"]["service"] for r in eval_ood}
    
    chunk_overlap_in = len(train_chunks & eval_in_chunks)
    chunk_overlap_ood = len(train_chunks & eval_ood_chunks)
    service_overlap_ood = len(train_services & ood_services)
    
    train_q_ngrams = [tokenize_ngrams(r["question"], n=3) for r in train_sft]
    max_sims = []
    contaminated_count = 0
    for erow in (eval_in + eval_ood):
        eq = tokenize_ngrams(erow["question"], n=3)
        max_sim = max((jaccard_similarity(eq, tq) for tq in train_q_ngrams), default=0.0)
        max_sims.append(max_sim)
        if max_sim > 0.85:
            contaminated_count += 1
            
    grounding_scores = []
    for row in all_sft:
        cid = row["traceability"]["chunk_id"]
        if cid in chunks_by_id:
            score = compute_lexical_grounding(row["answer"], chunks_by_id[cid].content)
            grounding_scores.append(score)
            
    cat_dist = {}
    lang_dist = {}
    gen_dist = {}
    for row in all_sft:
        cat_dist[row["category"]] = cat_dist.get(row["category"], 0) + 1
        lang_dist[row["language"]] = lang_dist.get(row["language"], 0) + 1
        g = row["traceability"]["generator"]
        gen_dist[g] = gen_dist.get(g, 0) + 1
        
    report = {
        "dataset_counts": {
            "train_cpt_rows": len(cpt_data),
            "train_sft_rows": len(train_sft),
            "eval_in_domain_rows": len(eval_in),
            "eval_out_of_domain_rows": len(eval_ood),
            "total_sft_eval_rows": len(all_sft)
        },
        "traceability_audit": {
            "traceability_coverage_pct": round(100.0 * (len(all_sft) - missing_files) / max(len(all_sft), 1), 2),
            "missing_source_files": missing_files,
            "invalid_line_ranges": invalid_lines
        },
        "data_leakage_audit": {
            "train_vs_eval_in_chunk_overlap": chunk_overlap_in,
            "train_vs_eval_ood_chunk_overlap": chunk_overlap_ood,
            "train_vs_eval_ood_service_overlap": service_overlap_ood,
            "near_duplicate_questions_gt_085_jaccard": contaminated_count,
            "mean_max_question_jaccard_train_vs_eval": round(sum(max_sims) / max(len(max_sims), 1), 4)
        },
        "quality_and_grounding": {
            "mean_lexical_grounding_score": round(sum(grounding_scores) / max(len(grounding_scores), 1), 4),
            "category_distribution": cat_dist,
            "language_distribution": lang_dist,
            "generator_distribution": gen_dist
        },
        "status": "PASSED" if (missing_files == 0 and chunk_overlap_in == 0 and chunk_overlap_ood == 0 and service_overlap_ood == 0) else "WARNING"
    }
    return report
