import os
import re
import json
import time
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
from src.chunker_splitter import DocChunk

SYSTEM_PROMPT_SFT = (
    "You are a Senior Technical Assistant specialized in backend microservices, APIs, and data workflows. "
    "Answer technical questions accurately based strictly on the official service documentation. "
    "Always cite the specific service, endpoint, table, or configuration parameter. "
    "If the documentation does not contain the information needed to answer, state clearly what is not specified "
    "instead of guessing or hallucinating."
)

def build_generation_prompt(chunk: DocChunk) -> str:
    return (
        "You are an expert LLM Data Engineer building Supervised Fine-Tuning (SFT) and Evaluation data from technical documentation.\n"
        "Generate exactly 3 concise question-answer pairs in the SAME LANGUAGE as the documentation chunk (Spanish if doc is Spanish, English if English):\n"
        "1. 'factual_qa': A specific technical question about an endpoint, database column, cronjob, parameter, or rule explicitly in the chunk.\n"
        "2. 'troubleshooting_or_usage': A practical developer/operations scenario based on the chunk.\n"
        f"3. 'abstention_unanswerable': A plausible technical question about `{chunk.service}` whose answer is NOT in the chunk, where the answer explicitly states that the documentation for `{chunk.service}` (`{chunk.source_file}`) does not specify that detail, mentioning what it DOES cover instead.\n\n"
        "RULES:\n"
        f"- Mention `{chunk.service}` in every question.\n"
        "- Keep answers concise (2-4 sentences) and 100% grounded in the chunk. Include a verbatim short substring from the chunk in `evidence_quote`.\n"
        "- Output ONLY a valid JSON array of 3 objects:\n"
        '[{"category": "factual_qa", "language": "es", "question": "...", "answer": "...", "evidence_quote": "..."}]\n\n'
        f"METADATA: Service=`{chunk.service}` | Version=`{chunk.version}` | File=`{chunk.source_file}` (lines {chunk.line_start}-{chunk.line_end}) | Section=`{chunk.section_hierarchy}`\n"
        f"CHUNK:\n{chunk.content[:2200]}\n"
    )

def detect_language(text: str) -> str:
    es_words = len(re.findall(r"\b(el|la|los|las|de|del|para|con|por|una|este|configuración|flujo|tabla|servicio)\b", text.lower()))
    en_words = len(re.findall(r"\b(the|and|for|with|from|this|that|table|service|application|configuration|endpoint)\b", text.lower()))
    return "es" if es_words > en_words else "en"

def heuristic_fallback_generator(chunk: DocChunk) -> List[Dict[str, str]]:
    lang = detect_language(chunk.content)
    lines = [l.strip() for l in chunk.content.splitlines() if l.strip() and not l.strip().startswith("#")]
    snippet = " ".join(lines[:3])[:220] if lines else chunk.section_hierarchy
    if lang == "es":
        return [
            {
                "category": "factual_qa",
                "language": "es",
                "question": f"En el servicio `{chunk.service}`, ¿qué especifica la documentación en la sección '{chunk.section_hierarchy}'?",
                "answer": f"Según la documentación de `{chunk.service}` (`{chunk.source_file}`, líneas {chunk.line_start}-{chunk.line_end}), en la sección '{chunk.section_hierarchy}' se detalla lo siguiente:\n\n{chunk.content[:500]}",
                "evidence_quote": snippet[:100]
            },
            {
                "category": "troubleshooting_or_usage",
                "language": "es",
                "question": f"¿Cómo debe un desarrollador aplicar o consultar la configuración descrita en '{chunk.section_hierarchy}' para el servicio `{chunk.service}`?",
                "answer": f"Para trabajar con `{chunk.service}` respecto a '{chunk.section_hierarchy}', se deben seguir las especificaciones de `{chunk.source_file}`: {snippet}",
                "evidence_quote": snippet[:100]
            },
            {
                "category": "abstention_unanswerable",
                "language": "es",
                "question": f"¿Cuál es el SLA de latencia p99 y el límite máximo de reintentos automáticos en Kafka para '{chunk.section_hierarchy}' en `{chunk.service}`?",
                "answer": f"La documentación oficial de `{chunk.service}` (`{chunk.source_file}`, sección '{chunk.section_hierarchy}') no especifica un SLA de latencia p99 ni políticas de reintentos en Kafka. Únicamente documenta: {snippet}",
                "evidence_quote": snippet[:80]
            }
        ]
    else:
        return [
            {
                "category": "factual_qa",
                "language": "en",
                "question": f"In the `{chunk.service}` service, what are the technical specifications described under '{chunk.section_hierarchy}'?",
                "answer": f"According to the `{chunk.service}` documentation (`{chunk.source_file}`, lines {chunk.line_start}-{chunk.line_end}), the '{chunk.section_hierarchy}' section specifies:\n\n{chunk.content[:500]}",
                "evidence_quote": snippet[:100]
            },
            {
                "category": "troubleshooting_or_usage",
                "language": "en",
                "question": f"How should an engineer use or troubleshoot the components in '{chunk.section_hierarchy}' for `{chunk.service}`?",
                "answer": f"Based on `{chunk.source_file}` for `{chunk.service}`, engineers should follow the details in '{chunk.section_hierarchy}': {snippet}",
                "evidence_quote": snippet[:100]
            },
            {
                "category": "abstention_unanswerable",
                "language": "en",
                "question": f"What is the multi-region failover RTO and GraphQL mutation rate limit for '{chunk.section_hierarchy}' in `{chunk.service}`?",
                "answer": f"The provided documentation for `{chunk.service}` (`{chunk.source_file}`, section '{chunk.section_hierarchy}') does not specify multi-region failover RTOs or GraphQL rate limits. It only covers: {snippet}",
                "evidence_quote": snippet[:80]
            }
        ]

def parse_json_safely(raw_text: str) -> Optional[List[Dict[str, Any]]]:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end+1]
    try:
        data = json.loads(cleaned)
        if isinstance(data, list) and len(data) >= 1:
            return data
    except Exception:
        pass
    return None

def synthesize_for_chunk_vertex(chunk: DocChunk, model_name: str = "gemini-2.5-flash") -> Tuple[List[Dict[str, Any]], str]:
    try:
        from vertexai.generative_models import GenerativeModel, GenerationConfig
        prompt = build_generation_prompt(chunk)
        config = GenerationConfig(temperature=0.2, response_mime_type="application/json")
        for attempt in range(2):
            try:
                model = GenerativeModel(model_name)
                resp = model.generate_content(prompt, generation_config=config)
                parsed = parse_json_safely(resp.text)
                if parsed:
                    return parsed, f"vertex_{model_name.replace('-', '_')}"
            except Exception:
                time.sleep(0.8)
    except Exception:
        pass
    return heuristic_fallback_generator(chunk), "heuristic_fallback"

def build_cpt_dataset(chunks: List[DocChunk]) -> List[Dict[str, Any]]:
    cpt_rows = []
    for c in chunks:
        if c.split != "train" or c.is_boilerplate:
            continue
        formatted_text = (
            f"<|doc_start|>\n"
            f"[SERVICE: {c.service} | VERSION: {c.version} | SOURCE: {c.source_file} | SECTION: {c.section_hierarchy}]\n\n"
            f"{c.content}\n"
            f"<|doc_end|>"
        )
        cpt_rows.append({
            "id": f"cpt_{c.chunk_id}",
            "split": c.split,
            "text": formatted_text,
            "service": c.service,
            "version": c.version,
            "source_file": c.source_file,
            "section_hierarchy": c.section_hierarchy,
            "line_start": c.line_start,
            "line_end": c.line_end,
            "chunk_id": c.chunk_id,
            "word_count": c.word_count,
            "traceability": {
                "service": c.service,
                "version": c.version,
                "source_file": c.source_file,
                "file_type": c.file_type,
                "section_hierarchy": c.section_hierarchy,
                "line_start": c.line_start,
                "line_end": c.line_end,
                "chunk_id": c.chunk_id,
                "superseded_versions": c.superseded_versions
            }
        })
    return cpt_rows

def build_sft_and_eval_datasets(
    chunks: List[DocChunk],
    provider: str = "vertex",
    max_workers: int = 8,
    cache_path: Path = Path("data_output/llm_synthesis_cache.json")
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    eligible_chunks = [c for c in chunks if not c.is_boilerplate]
    results_by_chunk: Dict[str, Tuple[List[Dict[str, Any]], str]] = {}

    cache_data: Dict[str, Any] = {}
    if cache_path and cache_path.exists():
        try:
            cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache_data = {}

    pending_chunks = []
    for c in eligible_chunks:
        if c.chunk_id in cache_data:
            entry = cache_data[c.chunk_id]
            results_by_chunk[c.chunk_id] = (entry["qa_list"], entry["generator"])
        else:
            pending_chunks.append(c)

    if pending_chunks:
        if provider == "vertex":
            try:
                import vertexai
                project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                if project:
                    vertexai.init(project=project, location="us-central1")
            except Exception:
                provider = "heuristic"

        if provider == "vertex":
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_chunk = {executor.submit(synthesize_for_chunk_vertex, c): c for c in pending_chunks}
                for fut in as_completed(future_to_chunk):
                    c = future_to_chunk[fut]
                    qa_list, gen_source = fut.result()
                    results_by_chunk[c.chunk_id] = (qa_list, gen_source)
                    cache_data[c.chunk_id] = {"qa_list": qa_list, "generator": gen_source}
            if cache_path:
                cache_path.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            for c in pending_chunks:
                results_by_chunk[c.chunk_id] = (heuristic_fallback_generator(c), "heuristic_fallback")
    else:
        print(f"   -> Cargados {len(eligible_chunks)} chunks desde caché determinista ({cache_path}).")

    train_sft, eval_in, eval_ood = [], [], []
    for idx, c in enumerate(eligible_chunks):
        qa_list, gen_source = results_by_chunk[c.chunk_id]
        for q_idx, qa in enumerate(qa_list):
            q_text = str(qa.get("question", "")).strip()
            a_text = str(qa.get("answer", "")).strip()
            cat = str(qa.get("category", "factual_qa")).strip()
            lang = str(qa.get("language", detect_language(c.content))).strip()
            quote = str(qa.get("evidence_quote", "")).strip()
            if not q_text or not a_text:
                continue

            include_context = (cat == "abstention_unanswerable") or ((idx + q_idx) % 3 != 0)
            if include_context:
                user_content = (
                    f"### Reference Documentation (`{c.service}` - `{c.source_file}`)\n"
                    f"Section: {c.section_hierarchy}\n"
                    f"```\n{c.content}\n```\n\n"
                    f"### Question\n{q_text}"
                )
                prompt_mode = "raft_with_context"
            else:
                user_content = q_text
                prompt_mode = "closed_book_direct"

            row_id = hashlib.sha256(f"{c.chunk_id}::{cat}::{q_text}".encode("utf-8")).hexdigest()[:12]
            record = {
                "id": f"sft_{row_id}",
                "split": c.split,
                "service": c.service,
                "version": c.version,
                "source_file": c.source_file,
                "line_start": c.line_start,
                "line_end": c.line_end,
                "chunk_id": c.chunk_id,
                "category": cat,
                "prompt_mode": prompt_mode,
                "language": lang,
                "question": q_text,
                "answer": a_text,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_SFT},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": a_text}
                ],
                "traceability": {
                    "service": c.service,
                    "version": c.version,
                    "source_file": c.source_file,
                    "file_type": c.file_type,
                    "section_hierarchy": c.section_hierarchy,
                    "line_start": c.line_start,
                    "line_end": c.line_end,
                    "chunk_id": c.chunk_id,
                    "evidence_quote": quote,
                    "superseded_versions": c.superseded_versions,
                    "generator": gen_source
                }
            }
            if c.split == "train":
                train_sft.append(record)
            elif c.split == "eval_in_domain":
                eval_in.append(record)
            elif c.split == "eval_out_of_domain":
                eval_ood.append(record)

    return train_sft, eval_in, eval_ood
