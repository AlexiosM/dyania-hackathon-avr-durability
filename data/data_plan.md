# Data Plan

## 1. Data Sources — Real Deployment

The production study requires a longitudinal record that connects the implanted aortic prosthesis to a stable postoperative reference echocardiogram, subsequent surveillance, alternative causes of valve dysfunction, clinical outcomes, and vital status. Data extraction and linkage will remain inside each participating institution's approved environment.

| Source domain | Required content | Preferred access pathway | Integration dependencies |
|---|---|---|---|
| Echocardiography | Dated TTE/TEE reports; peak velocity; peak and mean gradients; LVOT measurements; EOA; indexed EOA; DVI; acceleration time; stroke volume and flow state; intraprosthetic and paravalvular regurgitation; leaflet morphology/motion; LVEF; pulmonary pressure | HL7 messages, FHIR `DiagnosticReport` and `Observation`, reporting-database export, or approved warehouse tables | Stable study accession, patient identifier, acquisition date, report version, measurement units, and ability to distinguish aortic-prosthesis measurements |
| Implant and procedure records | Implant date; SAVR/TAVR; completed/cancelled status; first/redo/valve-in-valve status; manufacturer; model; label size; design; deployment details; concomitant procedures | Operative and catheterization reports, implant inventory, procedure modules, STS/ACC TVT-style registry, FHIR `Procedure` and `Device` | Device terminology crosswalk, procedure-to-device linkage, and reconciliation of planned versus completed procedures |
| EHR notes and problem-oriented documentation | Demographics, body size, symptoms, NYHA class, explicit valve assessments, comorbidities, cancer state and treatment exposures, smoking, and clinician interpretation | Approved clinical warehouse, FHIR `DocumentReference`, or note-system export | Note identifiers, service date, author/service type, version status, and local clinical-language-model inference |
| Laboratory data | Creatinine/eGFR, hemoglobin, HbA1c/glucose, lipids, calcium, phosphate, PTH, albumin, CRP/ESR, BNP/NT-proBNP, INR, dates, units, reference ranges, and result status | Laboratory information system, warehouse tables, HL7 ORU, or FHIR `Observation` | LOINC/local-code mapping, unit normalization, specimen/result status, and duplicate-result handling |
| Medication data | Anticoagulants, antiplatelets, lipid-lowering, antihypertensive, diabetes, heart-failure/diuretic, and calcium-phosphate therapies with order, administration, start/stop, and status information | Medication orders and administration records, pharmacy feed, FHIR `MedicationRequest` and `MedicationAdministration` | RxNorm/local formulary mapping, ingredient normalization, and distinction between ordered, active, administered, discontinued, and historical therapy |
| Cardiac CT and other imaging | HALT, reduced leaflet motion, calcification, thrombus, pannus, frame geometry/expansion, implantation depth, and other mechanism-defining findings | PACS/RIS metadata and reports, DICOM structured reports, or FHIR `DiagnosticReport` | Accession-to-patient linkage, modality/date, and report version |
| Encounters and outcomes | Heart-failure hospitalization, structural-heart review, redo SAVR, valve-in-valve TAVR, other aortic-prosthesis intervention, and last reliable contact | EHR encounter/procedure tables, claims, institutional registries, and FHIR `Encounter`/`Procedure` | Encounter-type validation, cross-facility capture, and completed-versus-planned procedure status |
| Pathology and mortality | Explant findings; date and cause of death; valve-related, cardiovascular, cancer-related, and other non-valve death | Surgical pathology, institutional vital status, claims, and regional/national mortality linkage where permitted | Cause-of-death adjudication, linkage quality, and jurisdiction-specific governance |

The minimum production dependencies are a consistent patient identifier across sources, a reliable implant date, dated and versioned echo reports, and a last-known-alive or death record. Cross-site identifiers must be transformed into study-specific linkage keys before analysis. PACS, registry, and mortality access may require separate approvals and interfaces beyond the core EHR feed.

### Extraction and Integration Architecture

Each note will be processed once with MedGemma, or an equivalently validated locally deployed language model, using the fixed evidence-linked extraction schema. The model may populate only prespecified fields, normalized categorical values, dates at their documented precision, and short supporting excerpts tied to the source note ID. It must return `null` when a fact is not explicitly documented and must not calculate PPM, HVD, SVD, BVF, censoring, or care-gap labels.

The schema is deliberately specific because its fields are based on prosthetic-valve guidance and published SVD risk-factor evidence [1-4]. Specificity reduces uncontrolled inference and makes extraction auditable. To avoid discarding unexpected but relevant AVR information, each clinical domain also includes bounded raw fields—for example, `prosthesis_description_raw`, `echo_comparison_text`, `other_aortic_prosthesis_imaging_findings`, and `other_relevant_comorbidity_text`. These fields remain linked to a source record and cannot become unrestricted generic event arrays.

Structured laboratory and medication rows will be imported directly rather than rewritten by the language model. The import will preserve patient linkage key, source row ID, timestamp, original name/code, value, unit, reference range or order status, and source system. Direct ingestion preserves precision and makes later normalization reversible.

The note facts, structured rows, imaging/procedure data, encounters, and outcomes will be merged by study patient ID into a dated longitudinal record. Deterministic code will then calculate BMI, Mosteller BSA, indexed EOA, BMI-adjusted PPM, echo changes and slopes, VARC-3 HVD/SVD/BVF tiers, prediction landmarks, competing events, censoring, and care-gap indicators. Separating literal extraction from clinical derivation makes each derived label reproducible and prevents the language model from silently applying incomplete criteria.

The production workflow has two sequential layers. First, the most recent eligible record is evaluated for current dysfunction. Tier 1 confirmed SVD records an event and removes the patient from the future-SVD risk set from that date. Tiers 2–4 enter a retrieval/adjudication queue and are withheld from event-free landmark prediction until resolved. Second, patients who remain alive and free of confirmed SVD receive conditional 1-, 3-, and 5-year predictions using only information available through the landmark.

### Planned Data Products

| Output | Grain | Purpose | Required provenance |
|---|---|---|---|
| `note_facts.jsonl` | One object per source note | Auditable facts extracted from narrative text | Study patient ID, note ID, service date/precision, note type, extracted fields, bounded supporting excerpts, schema/model version, and review flags |
| `patient_timeline.jsonl` | One object per patient containing dated domain events | Reconciled longitudinal view used for adjudication and feature derivation | Source row/note/accession IDs, original and normalized values, date precision, contradiction flags, provenance, and derivation version |
| `landmark_table.parquet` | One row per patient and eligible event-free prediction date | Model-ready predictors, future outcomes, competing events, and censoring | Landmark date, current-status gate result, reference echo, latest eligible source date, prediction horizon, feature version, label tier, data-sufficiency flags, and patient-level split |

The model-ready table will contain no post-landmark predictor information. Measurements from an earlier non-event visit may become historical predictors at a later eligible landmark. Measurements that define a confirmed event belong to the outcome, cannot predict that same event, and end subsequent future-SVD landmark eligibility.

---

## 2. Data Sources — Prototype / Hackathon

The organizer-supplied de-identified prototype contains:

| File domain | Records | Patients | Intended use |
|---|---:|---:|---|
| Notes | 215 notes | 117 | Develop and test constrained note extraction and evidence linkage |
| Laboratory results | 43,550 rows | 17 | Test direct structured import, normalization, and temporal linkage |
| Medications | 5,807 rows | 17 | Test direct structured import, ingredient grouping, status handling, and temporal linkage |

The existing echo-language screen flags at least one note for 93 of the 117 patients. Laboratory and medication data cover the same limited subset of 17 patients, so their availability must not be generalized to the full prototype cohort. The files support schema development, source reconciliation, timeline construction, and endpoint-rule testing. They do not contain enough consistently measured longitudinal valve data or confirmed outcomes to estimate discrimination, calibration, clinical utility, subgroup performance, or a real SVD event rate.

Only aggregate inventory counts will be reported in the submission. Raw source files, patient-level extracts, identifiers, and note text will not be copied into the contest repository.

---

## 3. Availability Assumptions

The following assumptions will be tested during site feasibility and again before model development. Failure of a high-impact assumption changes the achievable cohort or endpoint rather than being hidden through imputation.

| Assumption | Risk if unmet | Feasibility check | Planned response |
|---|---|---|---|
| A stable reference echo is available preferably 30-90 days after implantation | Baseline PPM and within-patient change cannot be distinguished reliably from incident deterioration | Estimate availability and technical adequacy by site, year, and implant approach | Use the earliest stable study within 180 days only as a flagged nonstandard reference; otherwise exclude from the primary cohort and retain for descriptive screening |
| At least one later clinical or echo assessment is captured | Time-to-event status and trajectories are unknown | Measure proportions with follow-up at 1, 3, and 5 years and distribution of last contact | Require follow-up or an earlier endpoint/competing death for the primary cohort; model surveillance gaps separately |
| Serial studies contain sufficient aortic-specific measurements | Complete VARC-3 HVD cannot be derived | Profile gradient, EOA, DVI, regurgitation, flow-state, and comparison-text completeness | Use complete measurements for Tier 1-3; retain the Tier 4 proxy only as a screening outcome when EOA/DVI are missing |
| Implant model, manufacturer, and label size are coded consistently | Device-specific durability and small-valve effects may be misclassified | Compare registry, implant log, operative report, inventory, and note values | Apply a governed device crosswalk; retain unresolved text and an explicit unknown category; never infer a model from an unsupported clue |
| Mortality linkage captures deaths outside the institution | Competing risk may be treated incorrectly as censoring | Compare EHR status with permitted regional/national or claims linkage | Report linkage completeness by site; use sensitivity analyses for uncertain vital status and avoid assuming absence of death |
| External follow-up and reintervention are captured | Outcomes may appear absent because care occurred elsewhere | Check claims, health-information exchange, registry, and referral records where permitted | Set last reliable contact conservatively, flag external-care uncertainty, and perform site/capture sensitivity analyses |
| Patient identifiers link sources consistently | Records may be split or assigned to the wrong patient | Quantify match rates, one-to-many conflicts, and orphan records before de-identification | Resolve within the source institution; quarantine ambiguous links and exclude them from model-ready data |
| Source timestamps and report versions are reliable | Leakage, duplicate events, and incorrect sequencing may occur | Audit timestamp fields and compare preliminary/final/amended reports | Preserve all versions, select the final clinically valid version by rule, and retain an audit trail |

The production cohort-size and event-rate assumptions will be estimated from a blinded site-feasibility extract. Synthetic data and the prototype files will not be used to set the clinical event rate.

---

## 4. Preprocessing and Data Quality

### Data Cleaning

Source data will be preserved unchanged in a restricted raw zone. Cleaning will create versioned standardized tables without overwriting the original values.

1. **Duplicate and version resolution.** Exact duplicate rows will be collapsed only after source IDs are preserved. Preliminary, final, corrected, and amended reports will be ordered by source status and timestamp. The final clinically valid report will supply the analytic value; superseded versions remain auditable.
2. **Source precedence.** Completed procedure and implant registry/log data take precedence over planned procedures or retrospective note summaries. Final structured echo measurements take precedence over NLP extraction of the same value when study identity and units agree. Operative/explant pathology and adjudicated imaging determine mechanism; a text-only diagnosis does not override them.
3. **Unit normalization.** Values will be stored in original and canonical units. A governed mapping will normalize gradient to mmHg, velocity to m/s, EOA to cm2, creatinine to a chosen site-harmonized unit, and other laboratory measurements to prespecified units. Conversions will record the formula and version.
4. **Range and logic checks.** Physiologic and technical bounds will generate review flags, not silent clipping. Examples include peak gradient below mean gradient, nonpositive EOA/BSA, incompatible valve positions, implausible dates, follow-up before implantation, or regurgitation grades outside the controlled vocabulary.
5. **Echo consolidation.** Measurements referring to the same study/accession and aortic prosthesis will form one echo object per study date. Conflicting values from the same date will retain their sources and require a rule-based resolution or review; they will not be averaged automatically.
6. **Contradictions and evidence review.** Conflicting implant identity, approach, date, valve position, mechanism, or outcome claims will set explicit contradiction flags. Automated QA will verify that extracted facts have a valid source ID and that sampled supporting excerpts substantiate the normalized field.
7. **Clinician-review queues.** Tier 1 candidates are reviewed as possible current events. Tier 2–4 findings enter retrieval/adjudication before the system creates another event-free prediction landmark. Reinterventions, suspected thrombosis/endocarditis, unresolved implant conflicts, large echo changes, implausible values, and a stratified sample of apparent non-events also enter review. Two cardiologists or structural-heart specialists will adjudicate endpoint candidates independently, with a third reviewer resolving disagreement.

Automated summaries will report row counts, unique patients, date ranges, duplication, missingness, unit distributions, linkage success, contradiction frequency, review yield, and changes between pipeline versions. No patient identifiers or source text will appear in those reports.

### Missing Data Strategy

True absence will remain `null`; it will not be converted to a normal finding. The pipeline will distinguish not documented, not measured, measured but unavailable, structurally inapplicable, and extraction/parse failure where the source supports that distinction.

For clinical model development, multiple imputation will be fitted only within each training fold and applied to its validation fold or locked test data without refitting. Imputation will use information available on or before the landmark and will respect variable type, site, and time. Missingness indicators will be retained for clinically meaningful absent measurements, and the random survival forest may also use model-native missing-value handling.

Routine last-observation-carried-forward is prohibited because echo timing is irregular and clinical deterioration can influence whether a test is performed. Missing outcomes will not be imputed. In the absence of a documented event, follow-up ends at the last reliable clinical contact; death and specified non-SVD valve events are handled as competing events rather than ordinary missingness.

### Temporal Alignment

The index implant is the earliest completed first-time bioprosthetic SAVR or TAVR selected for the primary cohort. A reference echocardiogram is chosen under stable hemodynamic conditions, preferably 30-90 days after implantation. If none is available, the earliest stable interpretable study within 180 days may be used with `reference_echo_nonstandard=true`; a later study is not treated as an equivalent baseline in the primary analysis.

Rolling prediction landmarks will be created only after the reference echo and while the patient is alive and free of confirmed Tier 1 SVD. Before creating a row, deterministic rules apply a current-status gate to the latest available evidence. Tier 1 records the event and ends future-SVD risk time. Unresolved Tier 2–4 findings are routed to retrieval/adjudication and withheld from the event-free prediction table. Every predictor must be documented on or before an eligible landmark, and every target or competing event must occur afterward. Endpoint-defining measurements from a visit cannot predict an endpoint declared at that visit. Exact dates will never be invented from year-only, month-only, or relative timing statements; date precision will be stored explicitly.

Echo change features will compare a follow-up study with the selected reference and will include absolute change, percentage change, elapsed time, annualized slope, variability, and time since the last interpretable study. A high absolute gradient without a rise from the patient's reference study will not be labeled incident SVD because baseline PPM or another stable nonstructural mechanism may explain it.

### Label / Ground Truth Construction

VARC-3 is the primary endpoint framework [1,3]. The EAPCI/ESC/EACTS durability definition will be implemented as a prespecified sensitivity analysis because published hemodynamic-SVD definitions are not interchangeable [2,5]. Each label will retain the source measurements, dates, mechanism evidence, algorithm version, and adjudication status.

| Tier | Operational definition | Analytic role |
|---|---|---|
| **Tier 1: confirmed structural SVD** | VARC-3 stage 2/3 HVD plus an intrinsic permanent leaflet or frame abnormality documented by echo or CT, or operative/explant pathology confirming structural degeneration with compatible pre-intervention dysfunction | Primary endpoint |
| **Tier 2: probable SVD** | Stage 2/3 HVD on at least two consecutive clinically distinct echocardiograms, no competing mechanism after standardized review, but morphology/pathology unavailable | Prespecified sensitivity endpoint and possible secondary model |
| **Tier 3: HVD of unknown mechanism** | Complete VARC-3 stage 2/3 hemodynamic criteria relative to the reference echo, without enough evidence to establish or exclude the mechanism | Secondary surveillance endpoint and case-finding pool |
| **Tier 4: minimal-data echo proxy** | Persistent mean-gradient rise meeting the VARC-3 change and final-gradient thresholds, or new moderate/severe intraprosthetic regurgitation, when EOA or DVI is missing | Screening flag for retrieval or review; never automatically promoted to primary SVD |
| **Tier 5: clinical valve failure** | Clinically expressive BVD, irreversible stage 3 HVD, aortic-valve reintervention, or valve-related death under VARC-3 BVF definitions | Separate patient-important secondary endpoint |

VARC-3 stage 2 stenotic HVD requires a mean-gradient increase >=10 mmHg resulting in a final mean gradient >=20 mmHg together with an EOA decrease >=0.3 cm2 or >=25%, or a DVI decrease >=0.1 or >=20%. Stage 3 requires a mean-gradient increase >=20 mmHg resulting in a final mean gradient >=30 mmHg together with an EOA decrease >=0.6 cm2 or >=50%, or a DVI decrease >=0.2 or >=40%. The regurgitation pathways are new/worsening intraprosthetic regurgitation by at least one grade to at least moderate for stage 2, or by at least two grades to severe for stage 3 [1,3].

PPM, paravalvular regurgitation, malposition, pannus or other extrinsic obstruction, thrombosis, endocarditis, and high-flow physiology remain separate mechanisms. PPM is a baseline predictor calculated from reference-echo EOA/BSA using BMI-adjusted ASE thresholds, not an incident SVD event [4]. Non-valve death and valve reintervention for a non-SVD mechanism are competing events. Text-only diagnoses such as “prosthetic stenosis,” “degeneration,” or “SVD” are case-finding signals and require supporting measurements or adjudication before they contribute to an endpoint.

The primary analysis uses Tier 1. Sensitivity analyses use Tier 1 plus Tier 2 and the EAPCI definition separately. Tiers 3 and 4 remain surveillance outcomes; Tier 5 remains a distinct BVF outcome. This hierarchy accepts a common echo proxy when richer evidence is absent without presenting functional deterioration as proven structural degeneration.

For survival-model construction, retrospective patients with confirmed SVD contribute their eligible pre-event landmarks and first confirmed event date. Patients without SVD contribute event-free follow-up until death, last reliable contact, or study end. A later echo, CT, pathology result, or adjudication decision may establish the outcome, but its contents cannot be moved backward into predictors for the preceding landmark.

### Extraction Model Validation

MedGemma, or an equivalently validated local model, is used for fixed-schema evidence extraction rather than endpoint classification or survival prediction. The prototype is too small to justify initial fine-tuning. A clinician-annotated stratified test set will measure field-level precision and recall, date/value/unit accuracy, negation and temporality accuracy, evidence fidelity, correct null use, and hallucination rate. Evaluation will retain difficult positive cases, clinically important negatives, different note types, and representation from each participating site. Deterministic rules and clinical adjudication remain independently testable even when the extraction model changes.

---

## 5. Synthetic or Proxy Data

Synthetic data will exercise the complete engineering and statistical workflow while keeping simulation truth separate from observed records. The generator is fixed at 2,000 patients, a maximum of 12 years of follow-up, and random seed `20260916`.

Each patient will be assigned one latent trajectory: stable prosthesis (70%), slow SVD (12%), rapid SVD (4%), PPM with a high residual gradient (6%), leaflet thrombosis (4%), endocarditis (2%), or valve-in-valve failure (2%). The generator will create a static patient/implant profile, a stable reference echo, serial hemodynamic trajectories, mechanism-specific events, competing death, and a care process. The care process includes annual clinical follow-up probability 0.82, surveillance-gap probability 0.22, external follow-up without a local echo probability 0.08, and alert-resolution probability 0.68.

Missingness, irregular visit timing, incomplete EOA/DVI, and external-care gaps will be generated after the latent clinical course so the full truth remains recoverable. Two table families will be retained:

- **Latent-truth tables:** complete clinical state, true mechanism, event times, and fully observed trajectories. These are used only to test whether derivation and model code recover what was simulated.
- **Observed tables:** the data visible after visit processes, missingness, documentation, and censoring are applied. These are processed by the same extraction, derivation, and modeling interfaces as production data.

Patients—not rows or visits—will be assigned 60%/20%/20% to development, validation, and test sets using independent random streams. Required checks include mutually exclusive splits, valid scenario probabilities, physiologic and temporal constraints, reproducible endpoint derivation, correct competing-risk handling, and recovery of the direction of simulated associations.

Synthetic output can show simulation recovery, software correctness, endpoint-rule behavior, and interface function. It cannot estimate clinical discrimination, calibration, safety, fairness, treatment effects, or expected real-world accuracy. Every synthetic table and result will be labeled accordingly, and clinical claims will require independent multi-site validation.

---

## 6. Data Governance and Privacy

The hackathon files were supplied in de-identified form for the Dyania event. Before any use outside the event, the team will confirm the organizer's reuse terms and, where required, execute a data-use agreement. Receipt of de-identified files does not by itself authorize redistribution, linkage to new sources, publication of patient-level records, or use for clinical deployment.

Real deployment data will remain in the institution-controlled environment. Direct identifiers and linkage keys will be separated from analytic data; access will be role based, least-privilege, and logged. Transfers will use an approved de-identified or limited dataset, encrypted transport and storage, and the necessary institutional agreements. MedGemma or another language model will run on premises or in an approved environment with appropriate contractual, security, and retention controls. Protected health information will not be submitted to public model endpoints.

The public repository may contain code, schemas, deterministic derivation rules, aggregate data-quality statistics, blank templates, documentation, and clearly labeled synthetic data. It may not contain the supplied workbooks, raw or extracted note text, source dates that could aid re-identification, identifiers, linkage keys, or real patient-level records. Supporting excerpts used for internal evidence review will remain in the restricted environment.

Audit logs will record source version, schema/model version, prompt version, extraction timestamp, deterministic-rule version, reviewer actions, and model-release version. Data-quality failures that affect endpoint validity will stop promotion to the model-ready table. The system's output is decision support: a high-risk or care-gap flag prompts chart review or consideration of earlier echocardiography, not an automatic diagnosis or reintervention decision.

---

## References

1. Généreux P, Piazza N, Alu MC, et al. Valve Academic Research Consortium 3: updated endpoint definitions for aortic valve clinical research. *J Am Coll Cardiol.* 2021;77:2717-2746. https://doi.org/10.1016/j.jacc.2021.02.038
2. Capodanno D, Petronio AS, Prendergast B, et al. Standardized definitions of structural deterioration and valve failure in assessing long-term durability of transcatheter and surgical aortic bioprosthetic valves. *Eur Heart J.* 2017;38:3382-3390. https://doi.org/10.1093/eurheartj/ehx303
3. Pibarot P, Herrmann HC, Wu C, et al. Standardized definitions for bioprosthetic valve dysfunction following aortic or mitral valve replacement: JACC state-of-the-art review. *J Am Coll Cardiol.* 2022;80:545-561. https://doi.org/10.1016/j.jacc.2022.06.002
4. Zoghbi WA, Jone PN, Chamsi-Pasha MA, et al. Guidelines for the evaluation of prosthetic valve function with cardiovascular imaging. *J Am Soc Echocardiogr.* 2024;37:2-63. https://www.asecho.org/wp-content/uploads/2024/01/PIIS0894731723005333.pdf
5. Velders BJJ, Vriesendorp MD, Asch FM, et al. Current definitions of hemodynamic structural valve deterioration after bioprosthetic aortic valve replacement lack consistency. *JTCVS Open.* 2024;19:68-90. https://doi.org/10.1016/j.xjon.2024.02.023