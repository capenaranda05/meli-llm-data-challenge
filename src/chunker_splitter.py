import re
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from src.parser_cleaner import RawDocRecord

@dataclass
class DocChunk:
    chunk_id: str
    service: str
    version: str
    source_file: str          # Trazabilidad exacta al archivo original en docs_raw/
    file_type: str
    section_hierarchy: str    # Ej. "Brand Endpoints > Search Brands > GET /"
    line_start: int           # Línea inicial en el documento original/transpilado
    line_end: int             # Línea final
    char_length: int
    word_count: int
    is_boilerplate: bool      # Marca plantillas genéricas (ej. VendorFlow Spring Boot README)
    split: str                # 'train' | 'eval_in_domain' | 'eval_out_of_domain'
    content: str
    superseded_versions: List[str]

def is_generic_boilerplate(text: str) -> bool:
    """Detecta si el bloque pertenece a la plantilla genérica de Spring Boot / VendorFlow."""
    markers = ["Spring Boot App model for Java 17", "VendorFlow Issue Tracker", "spring-boot-starter-tomcat"]
    return sum(1 for m in markers if m in text) >= 2

def chunk_document_by_headers(doc: RawDocRecord, max_chars: int = 2600, min_chars: int = 180) -> List[DocChunk]:
    """
    Divide un documento Markdown respetando su árbol de encabezados (#, ##, ###)
    y nunca rompe bloques de código (```) ni tablas Markdown a la mitad.
    Mantiene trazabilidad exacta de line_start y line_end.
    """
    lines = doc.cleaned_content.splitlines()
    raw_sections = []
    
    h_stack: Dict[int, str] = {}
    curr_lines: List[str] = []
    curr_start_line = 1
    curr_hierarchy = doc.rel_doc_path
    in_code_block = False
    
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            
        header_match = re.match(r"^(#{1,3})\s+(.+)$", stripped) if not in_code_block else None
        if header_match:
            # Guardar sección acumulada si tiene texto real
            if curr_lines:
                sec_text = "\n".join(curr_lines).strip()
                if sec_text:
                    raw_sections.append((curr_hierarchy, curr_start_line, idx - 1, sec_text))
            
            level = len(header_match.group(1))
            title = header_match.group(2).strip().strip("#").strip()
            h_stack[level] = title
            # Limpiar niveles inferiores
            for l in list(h_stack.keys()):
                if l > level:
                    del h_stack[l]
            curr_hierarchy = " > ".join(h_stack[k] for k in sorted(h_stack.keys()))
            curr_lines = [line]
            curr_start_line = idx
        else:
            curr_lines.append(line)
            
    if curr_lines:
        sec_text = "\n".join(curr_lines).strip()
        if sec_text:
            raw_sections.append((curr_hierarchy, curr_start_line, len(lines), sec_text))
            
    # Fusionar secciones muy cortas (ej. un H1 seguido inmediatamente de un H2) y subdividir las gigantes (> max_chars)
    merged_sections = []
    buffer = None
    
    for hier, l_start, l_end, text in raw_sections:
        if buffer is None:
            buffer = [hier, l_start, l_end, text]
        else:
            # Si el buffer actual es muy corto o solo tiene un título, fusionarlo con la siguiente sección
            if len(buffer[3]) < min_chars or len(buffer[3]) + len(text) <= max_chars:
                buffer[0] = f"{buffer[0]} | {hier}" if hier not in buffer[0] else buffer[0]
                buffer[2] = l_end
                buffer[3] = buffer[3] + "\n\n" + text
            else:
                merged_sections.append(tuple(buffer))
                buffer = [hier, l_start, l_end, text]
                
    if buffer is not None:
        merged_sections.append(tuple(buffer))
        
    # Si alguna sección sigue superando max_chars (ej. tablas largas o overview.md), dividir por párrafos sin cortar bloques
    final_chunks: List[DocChunk] = []
    for hier, l_start, l_end, text in merged_sections:
        sub_blocks = split_large_section(text, max_chars=max_chars)
        for sub_idx, sub_text in enumerate(sub_blocks):
            words = re.findall(r"\S+", sub_text)
            if len(words) < 10:
                continue
            sub_hier = f"{hier} (Part {sub_idx+1})" if len(sub_blocks) > 1 else hier
            raw_id = f"{doc.original_rel_path}::{sub_hier}::{l_start}-{l_end}::{sub_idx}"
            chunk_id = f"chk_{hashlib.sha256(raw_id.encode('utf-8')).hexdigest()[:12]}"
            
            final_chunks.append(DocChunk(
                chunk_id=chunk_id,
                service=doc.service,
                version=doc.version,
                source_file=doc.original_rel_path,
                file_type=doc.file_type,
                section_hierarchy=sub_hier,
                line_start=l_start,
                line_end=l_end,
                char_length=len(sub_text),
                word_count=len(words),
                is_boilerplate=is_generic_boilerplate(sub_text),
                split="unassigned",
                content=sub_text,
                superseded_versions=doc.superseded_versions
            ))
            
    return final_chunks

def split_large_section(text: str, max_chars: int = 2600) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    paragraphs = text.split("\n\n")
    blocks = []
    curr = []
    curr_len = 0
    in_fence = False
    for p in paragraphs:
        if p.count("```") % 2 == 1:
            in_fence = not in_fence
        if curr_len + len(p) > max_chars and curr and not in_fence:
            blocks.append("\n\n".join(curr))
            curr = [p]
            curr_len = len(p)
        else:
            curr.append(p)
            curr_len += len(p) + 2
    if curr:
        blocks.append("\n\n".join(curr))
    return blocks

def assign_splits_anti_leakage(chunks: List[DocChunk], ood_service: str = "zenith-keeper") -> List[DocChunk]:
    """
    Estrategia de Split a nivel de Chunk/Servicio ANTES de generar preguntas (Cero Data Leakage):
    1. 'eval_out_of_domain': Todo el servicio holdout (`zenith-keeper`) va íntegro a OOD Eval
       para medir capacidad del modelo de razonar en frío sobre un servicio nunca visto en SFT.
    2. 'eval_in_domain' vs 'train': Para los otros 9 servicios, separamos ~20% de los chunks
       (al menos 1 chunk representativo por servicio con suficientes chunks) exclusivamente para
       evaluar preguntas sobre secciones no memorizadas textualmente en SFT, manteniendo el 80% en Train.
    """
    by_service: Dict[str, List[DocChunk]] = {}
    for c in chunks:
        by_service.setdefault(c.service, []).append(c)
        
    for service, s_chunks in by_service.items():
        if service == ood_service:
            for c in s_chunks:
                c.split = "eval_out_of_domain"
            continue
            
        # Filtrar chunks no boilerplate para elegir un buen representante de evaluación
        non_bp = [c for c in s_chunks if not c.is_boilerplate]
        if len(non_bp) >= 3:
            # Cada 5to chunk (empezando por el índice 1) va a eval_in_domain (estratificado y determinista)
            for idx, c in enumerate(s_chunks):
                if not c.is_boilerplate and idx % 5 == 1:
                    c.split = "eval_in_domain"
                else:
                    c.split = "train"
        else:
            for c in s_chunks:
                c.split = "train"
                
    return chunks
