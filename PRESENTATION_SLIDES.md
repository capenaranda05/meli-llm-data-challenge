# Presentacion Tecnica — Senior Data Scientist (Data) · LLMs
**Desafio MercadoLibre:** Pipeline End-to-End de Datos de Entrenamiento, Evaluacion y Diseno Experimental

---

## Slide 1: Resumen Ejecutivo & Postura Arquitectonica (Min 1-2)

* **El Problema:** 107 archivos de documentacion tecnica de 10 microservicios exportados sin curacion: versiones superpuestas, esquemas contradictorios, plantillas vacias (`TO DO`) y especificaciones ocultas en `swagger.yaml`.
* **Nuestra Tesis (Parsimonia + Realismo Productivo):**
  1. **Garbage In, Hallucination Out:** En un modelo pequeno (3B), la limpieza semantica y resolucion de versiones aporta mas precision que cualquier hiperparametro de entrenamiento.
  2. **Por que RAFT (Retrieval-Augmented Fine-Tuning) + SFT en vez de solo memorizacion (CPT):** Las APIs cambian constantemente. El modelo pequeno debe entrenarse para **leer contexto tecnico con fidelidad, citar la fuente exacta y abstenerse cuando un dato no existe**, ademas de conocer el vocabulario interno.
  3. **Doble entrega:** Producimos tanto `train_cpt.jsonl` (conocimiento continuo) como `train_sft.jsonl` (instrucciones RAFT + Closed-Book + Abstencion) y dos sets de evaluacion libres de contaminacion (`eval_in_domain` y `eval_out_of_domain`).

---

## Slide 2: Diagnostico Forense de `docs_raw/` — Los 6 Hallazgos (Min 3-5)

| Hallazgo en el EDA | Caso Real Detectado | Riesgo para el LLM | Solucion en `src/parser_cleaner.py` |
| :--- | :--- | :--- | :--- |
| **1. Contradiccion silenciosa entre versiones** | `2p-revenue-optimizer-api/.../rule_header.md`: en `0.2.2` existen `created_date` y `productive_date`; en `latest` cambiaron a `date` y `version`. | Aprende dos esquemas opuestos para la misma tabla y alucina columnas deprecadas. | **Resolucion Canonica por `(service, rel_doc_path)`** priorizando version vigente y auditando `superseded_versions`. |
| **2. Puntero `latest` atrasado vs. SemVer** | En `vendor-stockkeeper-api`, `latest/guide/api.md` (1.7 KB) es copia exacta de `0.0.3`, pero `0.0.10-stock-consumer` tiene **el doble de documentacion** (3.5 KB). | Ordenar strings (`0.0.10 < 0.0.3`) o confiar ciegamente en `latest` pierde el 50% de la doc. | **Parser SemVer real `(0,0,10) > (0,0,3)`** que detecta cuando `latest` apunta a un snapshot viejo y promueve la version mas rica. |
| **3. Especificaciones ocultas en `swagger.yaml`** | `price-engine-api` y `zenith-keeper` tienen sus `.md` casi vacios, pero `specs/swagger.yaml` (3.9-13.5 KB) define todos sus endpoints y modelos. | Filtrar solo `*.md` deja al modelo ciego ante 3 de los 10 servicios. | **Transpilador determinista OpenAPI -> Markdown** (Endpoints, Parametros, HTTP Codes y Schemas). |
| **4. Stubs, `TO DO` y Solo-Imagen vs. Tablas Cortas** | `general.md` (281 B) solo dice `TO DO.`; `architecture.md` solo enlaza un `.png`. En cambio, `jobs.md` (225 B) contiene los cronjobs reales de produccion (`0 12 * * *`). | Un corte simple por tamano en bytes borra `jobs.md` y deja pasar `general.md`. | **Filtro de Densidad Semantica** (>= 12 palabras utiles tras limpiar imagenes, links, headers y tokens `TO DO`). |
| **5. Artefactos Docsify** | 34 archivos `documentationTypes.json`, `_sidebar.md`, `_coverpage.md`. | Ruido sintactico de navegacion. | Descarte trazable (`dropped_artifact`). |
| **6. Boilerplate transversal** | `2p-revenue-optimizer-api/.../README.md` es la plantilla generica de *Spring Boot Java 17 / VendorFlow*. | Sobre-ajuste a Java generico en vez del dominio del servicio. | Etiquetado `is_boilerplate=True` y exclusion de la sintesis Q&A. |

---

## Slide 3: Embudo de Datos y Estrategia Anti-Leakage (Min 6-8)

* **107 Archivos Crudos (`docs_raw/`)**:
  * Descartados: **34** `dropped_artifact` + **16** `dropped_exact_dup` + **11** `dropped_older_version` + **6** `dropped_stub_or_todo`.
  * Retenidos: **40 Documentos Canonicos** (cubriendo los 10 servicios).
* **100 Chunks Jerarquicos Trazables** (`# / ## / ###`, sin cortar bloques de codigo ni tablas Markdown):
  * **72 Chunks -> Split TRAIN:** Genera `train_cpt.jsonl` (71 filas) y `train_sft.jsonl` (213 filas).
  * **20 Chunks -> Split EVAL_IN_DOMAIN:** Genera `eval_in_domain.jsonl` (59 filas, 0% chunk overlap con Train).
  * **8 Chunks -> Split EVAL_OOD:** Genera `eval_out_of_domain.jsonl` (24 filas, 100% servicio Holdout: `zenith-keeper`).
* **Por que dividimos ANTES de sintetizar preguntas:** Evita que dos preguntas parafraseadas del mismo parrafo caigan en Train y Eval (*Data Leakage*).

---

## Slide 4: Diseno de los Datasets y Control de Calidad Automatico (Min 9-11)

### Taxonomia Balanceada en SFT y Evaluacion (33.3% cada categoria):
1. **`factual_qa`**: Extraccion exacta de columnas, tipos de datos, endpoints, cronjobs o responsables.
2. **`troubleshooting_or_usage`**: Resolucion de alertas operativas (`alerts.md`), configuracion de `SCOPE` o flujos de integracion.
3. **`abstention_unanswerable`**: Preguntas tecnicas plausibles sobre el servicio pero **ausentes en la documentacion**, entrenando al modelo a declarar que no esta especificado en lugar de alucinar.

### Resultados del Quality Gate (`src/validator.py` -> `quality_report.json`):
* **Trazabilidad Fisica:** `100.0%` (`0` archivos faltantes, `0` rangos de linea invalidos, cita textual en `evidence_quote`).
* **Solapamiento de Chunks / Servicio Holdout:** `0` entre Train y Eval.
* **Decontaminacion Activa de Preguntas (3-gram Jaccard):** `0` pares con similitud > 0.80 (media maxima Jaccard: `0.119`).

---

## Slide 5: Diseno del Experimento — Hipotesis, Baselines y Metricas (Min 12-14)

1. **Que probariamos primero:** `Qwen2.5-3B-Instruct` entrenado con **SFT QLoRA** ($r=16, \alpha=32$, 3 epocas sobre `train_sft.jsonl`, loss mask solo en respuestas del `assistant`).
2. **Contra que lo comparariamos (Baselines):**
   * **Baseline 0:** Modelo base Zero-Shot sin contexto.
   * **Baseline 1 (Critico):** Modelo base + RAG Hibrido (BM25 + Dense sobre `canonical_chunks.jsonl`, top-k=3) sin fine-tuning.
   * **Candidato 1:** Modelo SFT-RAFT + Retrieval.
   * **Ablacion:** CPT (2 epocas en `train_cpt.jsonl`) -> SFT (`train_sft.jsonl`).
3. **Con que metricas:**
   * *Deterministas:* Technical Entity Recall (columnas, rutas HTTP, cron expressions) y ROUGE-L.
   * *Semanticas (LLM-as-a-Judge):* Correctness (0/1) y Faithfulness/Groundedness (0/1).
   * *Incertidumbre:* Abstention Accuracy (%) vs. False Abstention Rate (%).
4. **Que resultado cambiaria nuestra siguiente decision:**
   * Si SFT-RAFT gana con contexto pero falla sin contexto -> Consolidar arquitectura RAG + Reranker.
   * Si Abstention Accuracy < 80% -> Agregar etapa **DPO (Direct Preference Optimization)** usando alucinaciones del modelo como `rejected`.
   * Si cae en `eval_out_of_domain` -> Inyectar *Distractor Chunks* de otros servicios en los prompts de entrenamiento.

---

## Slide 6: Escalabilidad a 10 Millones de Documentos (Min 15)

1. **Ingesta Distribuida ($O(N)$):** Ray Data / Spark con **XXHash64** (duplicados exactos) + **MinHash LSH distribuido** (5-gram shingles).
2. **Desacoplar Volumen CPT/RAG vs. SFT (*Principio LIMA*):** Los 10M limpios van al indice RAG y CPT; para SFT se muestrean estratificadamente **50k-100k chunks diversos** mediante clustering semantico y se sintetizan en batch con **vLLM** + Guided JSON Decoding.