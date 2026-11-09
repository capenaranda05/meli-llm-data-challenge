# Technical Documentation LLM Data Pipeline & Experiment Design

Solucion end-to-end para transformar documentacion tecnica cruda, heterogenea y desordenada (`docs_raw/`) en conjuntos de datos trazables y auditados para entrenar y evaluar un **Small Language Model (SLM)** abierto capaz de responder preguntas tecnicas con precision y sin alucinar.

---

## 1. Diagnostico del Corpus Crudo (EDA Forense)

Auditamos los **107 archivos** distribuidos en **10 servicios/proyectos** dentro de `docs_raw/`. Identificamos **6 patologias reales** que degradarian severamente a un LLM pequeno si se ingirieran sin control:

| Patologia Detectada | Evidencia Real en `docs_raw/` | Impacto en el Modelo si NO se resuelve | Solucion Implementada en el Pipeline |
| :--- | :--- | :--- | :--- |
| **1. Contradiccion de esquemas entre versiones** | En `2p-revenue-optimizer-api`, la tabla `rule_header.md` en `0.2.2` define las columnas `created_date` y `productive_date`, pero en `latest` cambiaron a `date` y `version (int)`. | **Alucinacion por conflicto de memoria:** el modelo aprende dos esquemas contradictorios para la misma tabla. | **Resolucion Canonica de Versiones** por `(service, rel_doc_path)` con registro de `superseded_versions`. |
| **2. Puntero `latest` desactualizado frente a SemVer** | En `vendor-stockkeeper-api`, `latest/guide/api.md` (1.7 KB) e `important.md` (8.7 KB) son clones exactos de la version antigua `0.0.3`, mientras que `0.0.10-stock-consumer` contiene la documentacion extendida (3.5 KB y 10.9 KB). | **Perdida del 50% de cobertura tecnica** si se toma `latest` a ciegas, o sobre-representacion x4 si se dejan todas las carpetas. | **Parser SemVer real** (`0.0.10 > 0.0.6 > 0.0.3`) que promueve la version semantica superior cuando `latest` apunta a un snapshot viejo. |
| **3. Fuga de documentacion hacia OpenAPI (`swagger.yaml`)** | En `price-engine-api` y `zenith-keeper`, los Markdown estan casi vacios, pero `specs/swagger.yaml` (3.9 KB a 13.5 KB) contiene todos los endpoints, parametros y modelos. | **Ceguera funcional** sobre los endpoints de 3 de los 10 servicios si solo se filtran archivos `.md`. | **Transpilador determinista OpenAPI -> Markdown** que convierte endpoints, tablas de parametros, codigos HTTP y esquemas en texto estructurado. |
| **4. Archivos Stub, `TO DO` y Solo-Imagen** | `price-engine-api/latest/guide/general.md` contiene solo `TO DO.`; `architecture.md` solo tiene links a `.png` sin texto; `zenith-keeper/.../README.md` tiene 33 bytes. En cambio, `jobs.md` pesa solo 225 bytes pero tiene los cronjobs reales de produccion (`0 12 * * *`). | Un filtro ingenuo por bytes descartaria `jobs.md` (valioso) y dejaria pasar `general.md` (basura). | **Filtro de Densidad Semantica**: mide palabras utiles excluyendo imagenes, links vacios, headers y tokens `TO DO`/`TBD` (umbral >= 12 palabras). |
| **5. Artefactos de navegacion Docsify** | **34 archivos** son `documentationTypes.json` (links a S3), `_sidebar.md` o `_coverpage.md`. | Ensucian la distribucion de tokens sin aportar conocimiento tecnico. | Descarte explicito y trazable en la etapa 1 (`dropped_artifact`). |
| **6. Boilerplate transversal de plantilla** | `2p-revenue-optimizer-api/.../README.md` contiene la plantilla por defecto del arquetipo *Spring Boot Java 17 / VendorFlow*. | El modelo sobre-ajusta a instrucciones genericas de Java en lugar de reglas de negocio propias del servicio. | Deteccion de boilerplate (`is_boilerplate=True`) para excluirlo de la sintesis de preguntas especificas de dominio. |

### Embudo de Limpieza y Trazabilidad
* **107 archivos crudos escaneados** -> **40 documentos canonicos limpios** (descartados con auditoria en `audit_file_decisions.jsonl`: 34 artefactos Docsify, 16 duplicados exactos, 11 versiones obsoletas/contradictorias, 6 stubs/TODOs).
* **40 documentos canonicos** -> **100 chunks jerarquicos** (segmentados respetando el arbol `# / ## / ###`, sin romper tablas ni bloques de codigo, con trazabilidad exacta a `source_file`, `line_start` y `line_end`).

---

## 2. Decision de Arquitectura de Datos: Que datos necesita el modelo y por que?

En un entorno de ingenieria de software donde las APIs evolucionan rapidamente, entrenar un modelo pequeno *unicamente* para que memorice hechos en sus pesos (Closed-Book puro) es fragil ante cambios de version. Por ello, adoptamos un enfoque **RAFT (Retrieval-Augmented Fine-Tuning) combinado con Conocimiento de Dominio**, produciendo **4 conjuntos de datos complementarios**:

1. **`data_output/train_cpt.jsonl` (71 filas - Continued Pre-Training):**
   * Chunks limpios del split de entrenamiento precedidos por cabeceras de anclaje contextual (`[SERVICE: ... | VERSION: ... | SOURCE: ...]`). Ideal para adaptacion ligera de vocabulario antes de SFT.
2. **`data_output/train_sft.jsonl` (213 filas - Supervised Fine-Tuning):**
   * Formato conversacional estandar `messages` (`system`, `user`, `assistant`) compatible con HuggingFace `TRL / SFTTrainer`.
   * Combina **70% prompts `raft_with_context`** (ensena al modelo a leer fragmentos de documentacion, extraer parametros exactos y citar la fuente) y **30% prompts `closed_book_direct`** (refuerza familiaridad directa con las entidades de los servicios).
   * Por cada chunk se generan **3 categorias balanceadas (33% c/u)**:
     * `factual_qa`: Preguntas directas sobre columnas, endpoints, tipos de datos o cronjobs.
     * `troubleshooting_or_usage`: Casos practicos de operacion, resolucion de alertas (`alerts.md`) o configuracion de `SCOPE`.
     * `abstention_unanswerable`: Preguntas plausibles pero cuya respuesta **NO** figura en la documentacion, entrenando explicitamente al modelo pequeno a **abstenerse y declarar que no esta especificado** en lugar de alucinar.
3. **`data_output/eval_in_domain.jsonl` (59 filas - Evaluacion In-Domain):**
   * Generado a partir de **20 chunks retenidos** de los 9 servicios vistos en entrenamiento (`train_vs_eval_in_chunk_overlap = 0`). Mide retencion de dominio sobre secciones no vistas en SFT.
4. **`data_output/eval_out_of_domain.jsonl` (24 filas - Evaluacion Out-of-Domain / Holdout):**
   * Generado a partir del servicio **`zenith-keeper` (100% retenido fuera de `train_cpt` y `train_sft`)**. Mide generalizacion de lectura tecnica y abstencion honesta ante un microservicio completamente nuevo.

---

## 3. Como Validar que los Datos Sirven (`src/validator.py`)

El pipeline incluye un **Quality Gate automatico** que audita los datasets generados y exporta `data_output/quality_report.json`:
* **Cobertura de Trazabilidad Fisica (100.0%):** Verifica que cada `source_file` exista en `docs_raw/` y que `1 <= line_start <= line_end`.
* **Aislamiento de Splits (0% Leakage):** Certifica interseccion nula de `chunk_id` entre `train_sft` y `eval_*`, e interseccion nula del servicio Holdout (`zenith-keeper`).
* **Decontaminacion Activa de Preguntas (`Jaccard <= 0.80`):** Filtra cualquier pregunta en Evaluacion cuya similitud de 3-gramas supere 0.80 frente a cualquier pregunta de Entrenamiento.
* **Fidelidad Lexica y Cita Exacta (`evidence_quote`):** Verifica el anclaje de vocabulario tecnico entre la respuesta sintetica y el chunk original.

---

## 4. Diseno del Experimento (Plan de Entrenamiento y Evaluacion)

### 4.1. Que probariamos primero?
* **Modelo Base:** Un modelo abierto pequeno con soporte bilingue (ES/EN) e instruccional fuerte: **`Qwen2.5-3B-Instruct`** (o **`Llama-3.2-3B-Instruct`**).
* **Primer Experimento (Exp 1 - SFT con QLoRA estilo RAFT):**
  * Ajuste fino supervisado sobre `train_sft.jsonl` usando **LoRA** ($r=16, \alpha=32$, `target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`, `lr=2e-4`, cosine scheduler, 3 epocas, mascara de loss solo sobre tokens del `assistant`).
  * **Justificacion:** En modelos de 3B parametros, el mayor retorno de inversion proviene de alinear la capacidad de extraccion fiel, citacion de endpoints/tablas y abstencion controlada sobre contexto recuperado (RAFT), con menor riesgo de *catastrophic forgetting* que iniciar con CPT puro.

### 4.2. Contra que lo comparariamos (Baselines)?
Evaluamos todos los sistemas sobre los mismos conjuntos congelados (`eval_in_domain.jsonl` y `eval_out_of_domain.jsonl`):
1. **Baseline 0 (Zero-Shot Closed-Book):** `Qwen2.5-3B-Instruct` sin ajustar y sin contexto documental.
2. **Baseline 1 (RAG Vanilla con Modelo Base):** `Qwen2.5-3B-Instruct` sin ajustar + recuperacion hibrida (BM25 + Embeddings sobre `canonical_chunks.jsonl`, top-$k=3$). *Baseline critico a vencer para justificar el fine-tuning.*
3. **Candidato Principal (SFT-RAFT + Retrieval):** Nuestro modelo ajustado con `train_sft.jsonl` operando sobre los chunks recuperados.
4. **Ablacion (CPT -> SFT):** Fase previa de 2 epocas sobre `train_cpt.jsonl` (`lr=5e-5`) seguida de SFT sobre `train_sft.jsonl`, para medir ganancia marginal en consultas `closed_book_direct`.

### 4.3. Con que metricas?
1. **Exactitud Tecnica Determinista (para `factual_qa` y `troubleshooting_or_usage`):**
   * **Entity / Technical Token Recall:** Fraccion de identificadores exactos (columnas SQL, rutas `/v1/...`, codigos HTTP, expresiones cron) del ground-truth presentes en la prediccion.
   * **ROUGE-L / Token F1:** Similitud estructural.
2. **Fidelidad y Calidad Semantica (LLM-as-a-Judge calibrado):**
   * **Correctness (0/1):** Exactitud tecnica frente a la respuesta de referencia.
   * **Faithfulness / Groundedness (0/1):** Ausencia de parametros o endpoints inventados fuera del chunk.
3. **Seguridad ante Incertidumbre (para `abstention_unanswerable`):**
   * **Abstention Accuracy (%):** Porcentaje de preguntas sin soporte documental donde el modelo declara explicitamente que el dato no esta especificado.
   * **False Abstention Rate (%):** Tasa de falsos rechazos en preguntas que si tenian respuesta.

### 4.4. Que resultado cambiaria nuestra siguiente decision? (Arbol de Decisiones)
* **Si SFT-RAFT supera ampliamente a Baseline 1 (RAG Vanilla) en Abstention Accuracy y Faithfulness, pero falla en `closed_book` puro:** Consolidar arquitectura **RAG + Lector SFT-RAFT** e invertir el siguiente sprint en mejorar el *Retriever/Reranker* sobre `canonical_chunks.jsonl`.
* **Si el modelo SFT sigue alucinando en `abstention_unanswerable` (< 80% Abstention Accuracy):** Agregar una etapa de **DPO (Direct Preference Optimization)** usando como `chosen` la abstencion correcta y como `rejected` las alucinaciones muestreadas del propio modelo SFT.
* **Si cae el rendimiento en `eval_out_of_domain` (zenith-keeper) respecto a `eval_in_domain`:** Reducir epocas/rango LoRA e inyectar *Distractor Chunks* (chunks de otros servicios mezclados con el chunk correcto) durante el entrenamiento RAFT.

---

## 5. Escalabilidad: Como llevariamos este flujo a 10 Millones de Documentos?

1. **Ingesta y Deduplicacion Distribuida (Spark / Ray Data):** Procesamiento particionado sobre Object Storage usando **XXHash64** (duplicados exactos) + **MinHash LSH distribuido** (5-gram shingles) para deduplicacion cuasi-exacta en $O(N)$.
2. **Desacoplar Volumen CPT/RAG vs. SFT (Principio *LIMA: Less Is More*):** Los 10M de documentos limpios van completos al indice vectorial/hibrido y a CPT. Para SFT, seleccionamos una muestra estratificada y diversa de **50k-100k chunks** mediante clustering semantico por servicio y tipo de documento.
3. **Sintesis Batch y Quality Gate Automatizado:** Inferencia asincrona masiva (Vertex Batch Prediction o clusters **vLLM** con Guided JSON Decoding) seguida del filtro determinista `validator.py` antes de publicar el dataset.

---

## 6. Pasos Exactos para Instalar Dependencias y Correr el Flujo

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_pipeline.py
```

* **Reproducibilidad garantizada sin GPU ni credenciales Cloud:** El repositorio incluye la cache de sintesis (`data_output/llm_synthesis_cache.json`) y el fallback offline (`python run_pipeline.py --provider heuristic`), permitiendo reproducir todo el flujo y las auditorias en menos de 2 segundos en cualquier maquina.

---

## 7. Que Haria Despues y Por Que (Priorizacion de Siguientes Pasos)

Dado el limite de diseno de ~4 horas, priorizamos tener un pipeline 100% funcional, determinista, reproducible y auditado de punta a punta. En las siguientes iteraciones ejecutariamos este roadmap ordenado por retorno de inversion (ROI):

1. **Inyeccion de *Hard Negative / Distractor Chunks* en `train_sft.jsonl` (Alto Impacto / Bajo Esfuerzo):**
   * *Que haria:* En los ejemplos `raft_with_context`, adjuntar junto al chunk verdadero 1 o 2 chunks distractores recuperados por BM25 de otros servicios o de otras tablas del mismo servicio.
   * *Por que:* En produccion, el retriever suele traer ruido en el top-$k$. Entrenar al modelo con distractores (como propone el paper original de *RAFT*) mejora drasticamente su robustez para ignorar contexto irrelevante sin confundir servicios.
2. **Validacion Semantica con *NLI / LLM-as-a-Judge* en el Quality Gate de Datos (Alto Impacto / Medio Esfuerzo):**
   * *Que haria:* Complementar la metrica actual de solapamiento lexico (`mean_lexical_grounding_score`) con un clasificador ligero de *Natural Language Inference (DeBERTa-v3-large MNLI)* que verifique `entailment` estricto entre el chunk fuente y la respuesta generada.
   * *Por que:* Permite filtrar automaticamente cualquier par sintetico donde el LLM generador haya hecho una extrapolacion sutil no soportada por la documentacion antes de entrenar.
3. **Pares de Preferencia Sinteticos para DPO (`train_dpo.jsonl`) (Medio Impacto / Medio Esfuerzo):**
   * *Que haria:* Para las preguntas `abstention_unanswerable` y de esquemas versionados (`0.2.2` vs `latest`), generar respuestas `rejected` (ej. responder usando la columna deprecada `productive_date` o inventando un SLA) frente a la respuesta `chosen` (usar el esquema `latest` o abstenerse).
   * *Por que:* En modelos pequenos (1B-3B), una fase corta de alineamiento por preferencias (DPO/ORPO) posterior al SFT reduce la tasa de alucinacion residual mucho mejor que seguir agregando epocas de SFT.
4. **Tests Unitarios Automatizados (`pytest`) y Harness de Evaluacion Local (Ingenieria / Mantenibilidad):**
   * *Que haria:* Agregar tests unitarios sobre `parse_semver`, `swagger_to_markdown` y `decontaminate_eval_split`, mas un script `evaluate_model.py` con `vLLM` + `rank_bm25`.
   * *Por que:* Garantiza que futuros cambios en las reglas de limpieza no introduzcan regresiones ni fugas de datos cuando el pipeline se integre en CI/CD.
