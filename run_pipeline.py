import argparse
import json
import time
import zipfile
from dataclasses import asdict
from pathlib import Path

from src.parser_cleaner import ingest_and_resolve_corpus
from src.chunker_splitter import chunk_document_by_headers, assign_splits_anti_leakage
from src.synthesizer import build_cpt_dataset, build_sft_and_eval_datasets
from src.validator import validate_datasets, tokenize_ngrams, jaccard_similarity


def save_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def decontaminate_eval_split(train_rows: list, eval_rows: list, threshold: float = 0.80) -> list:
    train_ngrams = [tokenize_ngrams(r["question"], n=3) for r in train_rows]
    clean = []
    for erow in eval_rows:
        eq = tokenize_ngrams(erow["question"], n=3)
        max_sim = max((jaccard_similarity(eq, tq) for tq in train_ngrams), default=0.0)
        if max_sim <= threshold:
            clean.append(erow)
    return clean


def ensure_docs_raw(docs_dir: Path, zip_fallback: Path = Path("docs_raw.zip")) -> None:
    if docs_dir.exists() and any(docs_dir.iterdir()):
        return
    if zip_fallback.exists():
        print(f"📦 Extrayendo {zip_fallback} en {docs_dir}...")
        with zipfile.ZipFile(zip_fallback, "r") as z:
            top_dirs = {p.split("/")[0] for p in z.namelist() if "/" in p and not p.startswith("__MACOSX")}
            if "docs_raw" in top_dirs:
                z.extractall(Path("."))
            else:
                docs_dir.mkdir(parents=True, exist_ok=True)
                z.extractall(docs_dir)
    else:
        raise FileNotFoundError(f"No se encontró la carpeta {docs_dir} ni el archivo {zip_fallback}.")


def main():
    parser = argparse.ArgumentParser(description="End-to-End Data Pipeline for Technical LLM Training & Evaluation")
    parser.add_argument("--docs-dir", type=str, default=str(Path(__file__).resolve().parent / "docs_raw"), help="Ruta a la carpeta docs_raw/")
    parser.add_argument("--output-dir", type=str, default=str(Path(__file__).resolve().parent / "data_output"), help="Carpeta de salida para los datasets .jsonl")
    parser.add_argument("--provider", type=str, choices=["vertex", "heuristic"], default="vertex",
                        help="Proveedor para síntesis Q&A ('vertex' usa Gemini / caché local; 'heuristic' es 100% offline)")
    parser.add_argument("--ood-service", type=str, default="zenith-keeper",
                        help="Servicio retenido al 100% para evaluación Out-of-Domain (Holdout)")
    parser.add_argument("--ignore-cache", action="store_true", help="Forzar re-generación ignorando caché local")
    args = parser.parse_args()

    t0 = time.time()
    docs_dir = Path(args.docs_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ensure_docs_raw(docs_dir)

    print("1️⃣ [Ingesta & Limpieza Semántica] Escaneando corpus crudo y resolviendo versiones SemVer...")
    records, ingest_summary = ingest_and_resolve_corpus(docs_dir)
    canonical_docs = [r for r in records if r.status == "kept_canonical"]
    print(f"   -> Escaneados: {ingest_summary['total_files_scanned']} archivos | Canónicos retenidos: {len(canonical_docs)}")

    print("2️⃣ [Chunking Jerárquico & Split Anti-Leakage] Segmentando por estructura Markdown/OpenAPI...")
    all_chunks = []
    for doc in canonical_docs:
        all_chunks.extend(chunk_document_by_headers(doc))
    all_chunks = assign_splits_anti_leakage(all_chunks, ood_service=args.ood_service)
    print(f"   -> Total chunks trazables: {len(all_chunks)}")

    print("3️⃣ [Síntesis de Datasets CPT + SFT + Evaluación] Construyendo conjuntos de datos...")
    cpt_data = build_cpt_dataset(all_chunks)
    cache_file = out_dir / "llm_synthesis_cache.json"
    if args.ignore_cache and cache_file.exists():
        cache_file.unlink()

    train_sft, eval_in, eval_ood = build_sft_and_eval_datasets(
        all_chunks, provider=args.provider, cache_path=cache_file
    )

    eval_in = decontaminate_eval_split(train_sft, eval_in, threshold=0.80)
    eval_ood = decontaminate_eval_split(train_sft, eval_ood, threshold=0.80)

    save_jsonl(out_dir / "audit_file_decisions.jsonl", [asdict(r) for r in records])
    save_jsonl(out_dir / "canonical_chunks.jsonl", [asdict(c) for c in all_chunks])
    save_jsonl(out_dir / "train_cpt.jsonl", cpt_data)
    save_jsonl(out_dir / "train_sft.jsonl", train_sft)
    save_jsonl(out_dir / "eval_in_domain.jsonl", eval_in)
    save_jsonl(out_dir / "eval_out_of_domain.jsonl", eval_ood)

    print("4️⃣ [Quality Gate & Auditoría] Validando trazabilidad, fidelidad y ausencia de Data Leakage...")
    chunks_by_id = {c.chunk_id: c for c in all_chunks}
    report = validate_datasets(docs_dir, chunks_by_id, cpt_data, train_sft, eval_in, eval_ood)
    report["ingestion_summary"] = ingest_summary
    (out_dir / "quality_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    elapsed = time.time() - t0
    print(f"\n✅ Pipeline ejecutado exitosamente en {elapsed:.2f}s | Estado Quality Gate: {report['status']}")
    print(f"   📁 Datasets generados en: {out_dir.resolve()}")
    for k, v in report["dataset_counts"].items():
        print(f"      - {k:<25}: {v}")


if __name__ == "__main__":
    main()
