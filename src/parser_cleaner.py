import re
import json
import yaml
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional

@dataclass
class RawDocRecord:
    service: str
    version: str
    rel_doc_path: str          # Ruta relativa dentro de la versión (ej. guide/api.md)
    original_rel_path: str     # Ruta completa dentro de docs_raw/
    file_type: str             # 'markdown' | 'openapi_yaml'
    raw_size_bytes: int
    content_hash: str
    cleaned_content: str
    semantic_word_count: int
    status: str                # 'kept_canonical' | 'dropped_artifact' | 'dropped_stub_or_todo' | 'dropped_exact_dup' | 'dropped_older_version'
    status_reason: str
    superseded_versions: List[str]

def parse_semver(ver_str: str) -> Tuple[int, int, int, int, str]:
    """
    Convierte strings como '0.0.10-stock-consumer', 'v0.0.2', '5.6.2-hotfix-1', 'latest'
    en una tupla ordenable semánticamente: (major, minor, patch, is_latest_flag, raw).
    Nota: '0.0.10' > '0.0.6' > '0.0.3'.
    """
    v = ver_str.strip().lstrip("vV")
    if v.lower() == "latest":
        # latest tiene prioridad base alta, pero se contrasta con contenido real
        return (9999, 9999, 9999, 1, ver_str)
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", v)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)), 0, ver_str)
    return (0, 0, 0, 0, ver_str)

def swagger_to_markdown(yaml_text: str, service: str, source_path: str) -> str:
    """
    Convierte especificaciones OpenAPI/Swagger (YAML) en Markdown técnico estructurado
    para no perder la documentación crítica de servicios como price-engine-api o zenith-keeper.
    """
    try:
        spec = yaml.safe_load(yaml_text)
    except Exception as e:
        return f"Error parsing YAML: {e}"
    
    if not isinstance(spec, dict):
        return ""
    
    info = spec.get("info", {})
    title = info.get("title", service)
    version = info.get("version", "unknown")
    desc = info.get("description", f"OpenAPI specification for {service}.")
    base_path = spec.get("basePath", "/")
    
    md_lines = [
        f"# {title} - OpenAPI Specification (v{version})",
        f"**Service**: `{service}` | **Base Path**: `{base_path}` | **Source**: `{source_path}`",
        f"\n{desc}\n",
        "## Endpoints Reference"
    ]
    
    paths = spec.get("paths", {})
    for endpoint, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, details in methods.items():
            if method.lower() not in {"get", "post", "put", "delete", "patch", "options", "head"}:
                continue
            if not isinstance(details, dict):
                continue
            summary = details.get("summary", "")
            op_desc = details.get("description", "")
            op_id = details.get("operationId", "")
            tags = ", ".join(details.get("tags", []))
            
            md_lines.append(f"\n### `{method.upper()} {endpoint}` — {summary}")
            if tags:
                md_lines.append(f"- **Tags**: {tags}")
            if op_id:
                md_lines.append(f"- **Operation ID**: `{op_id}`")
            if op_desc and op_desc != summary:
                md_lines.append(f"- **Description**: {op_desc.strip()}")
            
            # Parámetros
            params = details.get("parameters", [])
            if params:
                md_lines.append("\n#### Parameters")
                md_lines.append("| Name | In | Type/Schema | Required | Description |")
                md_lines.append("| --- | --- | --- | --- | --- |")
                for p in params:
                    if not isinstance(p, dict):
                        continue
                    p_name = p.get("name", "")
                    p_in = p.get("in", "")
                    p_req = str(p.get("required", False))
                    p_desc = str(p.get("description", "")).replace("\n", " ")
                    p_type = p.get("type", "")
                    if not p_type and "schema" in p and isinstance(p["schema"], dict):
                        p_type = p["schema"].get("$ref", p["schema"].get("type", "object")).split("/")[-1]
                    md_lines.append(f"| `{p_name}` | {p_in} | `{p_type}` | {p_req} | {p_desc} |")
            
            # Respuestas
            responses = details.get("responses", {})
            if responses:
                md_lines.append("\n#### HTTP Responses")
                for code, r_info in responses.items():
                    if isinstance(r_info, dict):
                        r_desc = str(r_info.get("description", "")).replace("\n", " ")
                        schema_ref = ""
                        if "schema" in r_info and isinstance(r_info["schema"], dict):
                            schema_ref = r_info["schema"].get("$ref", r_info["schema"].get("type", "")).split("/")[-1]
                        suffix = f" (Schema: `{schema_ref}`)" if schema_ref else ""
                        md_lines.append(f"- **HTTP {code}**: {r_desc}{suffix}")
                        
    # Definiciones / Modelos de Datos
    defs = spec.get("definitions", spec.get("components", {}).get("schemas", {}))
    if defs and isinstance(defs, dict):
        md_lines.append("\n## Data Models / Schemas")
        for model_name, model_spec in defs.items():
            if not isinstance(model_spec, dict):
                continue
            md_lines.append(f"\n### Model `{model_name}`")
            props = model_spec.get("properties", {})
            req_fields = set(model_spec.get("required", []))
            if props and isinstance(props, dict):
                md_lines.append("| Property | Type | Required | Description / Example |")
                md_lines.append("| --- | --- | --- | --- |")
                for prop_name, prop_info in props.items():
                    if not isinstance(prop_info, dict):
                        continue
                    p_type = prop_info.get("type", prop_info.get("$ref", "object").split("/")[-1])
                    if p_type == "array" and "items" in prop_info and isinstance(prop_info["items"], dict):
                        item_t = prop_info["items"].get("type", prop_info["items"].get("$ref", "").split("/")[-1])
                        p_type = f"array<{item_t}>"
                    is_req = "Yes" if prop_name in req_fields else "No"
                    p_desc = str(prop_info.get("description", prop_info.get("example", ""))).replace("\n", " ")
                    md_lines.append(f"| `{prop_name}` | `{p_type}` | {is_req} | {p_desc} |")
                    
    return "\n".join(md_lines)

def clean_markdown_noise(text: str) -> str:
    """Limpia comentarios de Docsify, banners de signos '#' decorativos y exceso de líneas vacías."""
    # Eliminar comentarios HTML como <!-- {docsify-ignore} -->
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Eliminar líneas de puros '#' decorativos (ej. ############## en demand-forecast-docs)
    text = re.sub(r"^#{7,}\s*$", "", text, flags=re.MULTILINE)
    # Normalizar saltos de línea excesivos
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def compute_semantic_density(text: str) -> Tuple[int, str]:
    """
    Calcula cuántas palabras con valor semántico real tiene el documento
    después de quitar imágenes, links vacíos, encabezados y placeholders ('TO DO').
    Retorna (word_count, reason_if_low).
    """
    without_imgs = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    without_html = re.sub(r"<[^>]+>", "", without_imgs)
    # Quitar links cuyo texto es genérico
    without_links = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", without_html)
    # Quitar líneas que son solo encabezados (# Titulo)
    body_lines = [
        line.strip() for line in without_links.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    body_text = " ".join(body_lines)
    
    # Detectar plantillas TO DO o placeholders obvios
    todo_Removed = re.sub(r"\b(TO\s*DO|TBD|WIP|Flujo\s*\d+|Funcionamiento\s*\d+|Flujos\.)\b", "", body_text, flags=re.IGNORECASE)
    words = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúñÑ0-9_/-]{2,}", todo_Removed)
    
    if len(words) < 12:
        return len(words), f"Densidad semántica insuficiente ({len(words)} palabras útiles sin contar títulos/imágenes/TODOs)"
    return len(words), "OK"

def ingest_and_resolve_corpus(docs_raw_dir: Path) -> Tuple[List[RawDocRecord], Dict]:
    """
    Recorre docs_raw/, filtra artefactos de Docsify y stubs sin contenido,
    convierte Swagger YAML a Markdown técnico, y resuelve conflictos entre versiones.
    """
    all_files = sorted([
        f for f in docs_raw_dir.rglob("*")
        if f.is_file() and not f.name.startswith(".") and "__MACOSX" not in str(f)
    ])
    
    records: List[RawDocRecord] = []
    grouped_candidates: Dict[Tuple[str, str], List[RawDocRecord]] = {}
    
    for f in all_files:
        rel_path = f.relative_to(docs_raw_dir)
        parts = rel_path.parts
        service = parts[0]
        version = parts[1] if len(parts) > 2 else "default"
        rel_doc_path = "/".join(parts[2:]) if len(parts) > 2 else f.name
        
        raw_bytes = f.read_bytes()
        content_hash = hashlib.sha256(raw_bytes).hexdigest()[:12]
        raw_text = raw_bytes.decode("utf-8", errors="replace")
        
        # 1. Filtrar artefactos de configuración/navegación Docsify
        if f.name == "documentationTypes.json" or f.name in {"_sidebar.md", "_coverpage.md", "coverpage.md"}:
            records.append(RawDocRecord(
                service=service, version=version, rel_doc_path=rel_doc_path,
                original_rel_path=str(rel_path), file_type="artifact",
                raw_size_bytes=len(raw_bytes), content_hash=content_hash,
                cleaned_content="", semantic_word_count=0,
                status="dropped_artifact",
                status_reason=f"Artefacto de navegación/infraestructura Docsify ({f.name})",
                superseded_versions=[]
            ))
            continue
            
        # 2. Procesar OpenAPI / Swagger YAML o Markdown
        if f.suffix in {".yaml", ".yml"}:
            file_type = "openapi_yaml"
            cleaned = swagger_to_markdown(raw_text, service, str(rel_path))
        else:
            file_type = "markdown"
            cleaned = clean_markdown_noise(raw_text)
            
        # 3. Evaluar densidad semántica (filtrar stubs, solo-imágenes y TO DOs)
        sem_words, reason = compute_semantic_density(cleaned)
        if sem_words < 12:
            records.append(RawDocRecord(
                service=service, version=version, rel_doc_path=rel_doc_path,
                original_rel_path=str(rel_path), file_type=file_type,
                raw_size_bytes=len(raw_bytes), content_hash=content_hash,
                cleaned_content=cleaned, semantic_word_count=sem_words,
                status="dropped_stub_or_todo",
                status_reason=reason,
                superseded_versions=[]
            ))
            continue
            
        rec = RawDocRecord(
            service=service, version=version, rel_doc_path=rel_doc_path,
            original_rel_path=str(rel_path), file_type=file_type,
            raw_size_bytes=len(raw_bytes), content_hash=content_hash,
            cleaned_content=cleaned, semantic_word_count=sem_words,
            status="candidate", status_reason="Valid semantic document",
            superseded_versions=[]
        )
        grouped_candidates.setdefault((service, rel_doc_path), []).append(rec)
        
    # 4. Resolución Canónica de Versiones por (service, rel_doc_path)
    for (service, rel_doc_path), group in grouped_candidates.items():
        if len(group) == 1:
            group[0].status = "kept_canonical"
            group[0].status_reason = "Única versión activa del documento"
            records.append(group[0])
            continue
            
        # Ordenar versiones numéricas (excluyendo 'latest' primero para detectar si 'latest' quedó congelado en una versión vieja)
        non_latest = [g for g in group if g.version.lower() != "latest"]
        latest_recs = [g for g in group if g.version.lower() == "latest"]
        
        non_latest_sorted = sorted(non_latest, key=lambda r: parse_semver(r.version), reverse=True)
        highest_semver_rec = non_latest_sorted[0] if non_latest_sorted else None
        latest_rec = latest_recs[0] if latest_recs else None
        
        # Caso especial detectado en EDA (ej. vendor-stockkeeper-api):
        # Si 'latest' tiene exactamente el mismo hash que una versión antigua (ej. 0.0.3),
        # pero existe una versión SemVer superior (ej. 0.0.10) con más contenido técnico,
        # la fuente canónica más reciente y completa es highest_semver_rec (0.0.10).
        chosen: RawDocRecord
        if latest_rec and highest_semver_rec:
            older_hashes = {r.content_hash for r in non_latest_sorted[1:]}
            if (latest_rec.content_hash in older_hashes and 
                highest_semver_rec.content_hash != latest_rec.content_hash and
                highest_semver_rec.semantic_word_count > latest_rec.semantic_word_count):
                chosen = highest_semver_rec
                chosen.status_reason = (
                    f"Elegida versión SemVer superior ({chosen.version}) porque 'latest' "
                    f"apuntaba a un snapshot antiguo ({latest_rec.semantic_word_count} vs {chosen.semantic_word_count} palabras)"
                )
            else:
                chosen = latest_rec
                chosen.status_reason = (
                    f"Elegida versión canónica 'latest' (reemplaza versiones previas)"
                )
        elif latest_rec:
            chosen = latest_rec
            chosen.status_reason = "Elegida versión 'latest'"
        else:
            chosen = highest_semver_rec
            chosen.status_reason = f"Elegida versión SemVer más reciente ({chosen.version})"
            
        chosen.status = "kept_canonical"
        superseded = []
        for other in group:
            if other is chosen:
                continue
            superseded.append(f"{other.version} ({other.original_rel_path})")
            if other.content_hash == chosen.content_hash:
                other.status = "dropped_exact_dup"
                other.status_reason = f"Duplicado exacto (hash {other.content_hash}) de la versión canónica {chosen.original_rel_path}"
            else:
                other.status = "dropped_older_version"
                other.status_reason = f"Versión superada/contradictoria frente a la canónica {chosen.original_rel_path}"
            records.append(other)
            
        chosen.superseded_versions = superseded
        records.append(chosen)
        
    # Resumen estadístico
    summary = {
        "total_files_scanned": len(records),
        "by_status": {},
        "services_covered": sorted(list({r.service for r in records if r.status == "kept_canonical"}))
    }
    for r in records:
        summary["by_status"][r.status] = summary["by_status"].get(r.status, 0) + 1
        
    return sorted(records, key=lambda x: x.original_rel_path), summary
