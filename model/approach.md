# VALVE-WATCH Modeling Approach

## Intended Use

VALVE-WATCH supports post-implant surveillance of adults with a confirmed bioprosthetic aortic valve. It reconstructs the longitudinal valve record, identifies current dysfunction or missing surveillance that requires review, and estimates future structural valve deterioration (SVD) risk only when the patient remains free of confirmed SVD at an eligible landmark. It does not diagnose SVD, select SAVR versus TAVR, or recommend reintervention.

## Two-Layer Decision Logic

### Layer 1: Current Dysfunction and Care-Gap Detection

Before forecasting, deterministic code applies the prespecified VARC-3 rules to all information available at the candidate landmark.

| Current status | System handling |
|---|---|
| Tier 1 confirmed structural SVD | Record the first confirmed event date, remove the patient from future-SVD risk sets from that date, and route the case for clinician review. |
| Tier 2 probable SVD | Retrieve missing evidence and adjudicate. Use only in prespecified sensitivity analyses after resolution. |
| Tier 3 HVD of unknown mechanism | Review competing mechanisms and retrieve imaging. Do not treat the visit as confirmed SVD or an event-free landmark while unresolved. |
| Tier 4 minimal-data echo proxy | Retrieve full echo measurements or arrange reassessment. Use as a case-finding signal only. |
| Tier 5 BVF | Record as a separate patient-important secondary endpoint with its mechanism. |
| Alive, resolved and free of confirmed SVD | Proceed to future-risk prediction. |

This gate prevents the model from forecasting an event that is already present and prevents uncertain current dysfunction from being mislabeled as event-free follow-up.

### Layer 2: Future SVD Prediction

The prediction target is the first subsequent Tier 1 event after an eligible landmark: VARC-3 stage 2 or 3 HVD plus an intrinsic permanent structural mechanism confirmed by imaging, operative/explant evidence, or blinded adjudication. Conditional risk is estimated over 1, 3, and 5 years.

The reference echo and all eligible pre-landmark studies may provide gradient, EOA, DVI, intraprosthetic regurgitation, PPM, and longitudinal trajectory features. A later echo, CT, pathology result, or adjudication conclusion used to establish the event belongs to the outcome and cannot be used as a predictor at the preceding landmark.

## Separation of Extraction, Derivation and Prediction

MedGemma, or an equivalently validated local language model, extracts explicitly documented note facts into a fixed evidence-linked schema. It does not assign endpoint tiers or survival risk. Initial development uses prompt-constrained extraction rather than fine-tuning on the 117-patient prototype.

Structured laboratory, medication, procedure, implant and imaging fields enter through direct mappings where available. Versioned deterministic code selects the reference echo and calculates BMI, BSA, indexed EOA, PPM, echo changes, HVD stages, evidence tiers, censoring, landmark eligibility and care gaps. Clinicians adjudicate candidate structural mechanisms and clinically ambiguous outcomes.

Extraction validation uses a clinician-annotated, locked test set and reports field-level precision, recall and F1; date, value and unit accuracy; negation and temporality accuracy; evidence-span fidelity; correct null use; and hallucination rate. Performance is stratified by note type, site and clinically important field.

## Risk Sets and Retrospective Contribution

Patients who develop confirmed SVD contribute all eligible pre-event landmark rows and their first confirmed event date. They contribute no future-SVD landmarks on or after that event. Patients without confirmed SVD contribute event-free follow-up until non-valve death, censoring at the last reliable clinical contact, or study end. All rows from one patient stay in one data partition.

Tier 2–4 visits remain outside the event-free landmark table while unresolved. After adjudication, the timeline is rebuilt reproducibly: a confirmed Tier 1 date ends the risk interval, while a resolved non-event can become an eligible landmark if all other requirements are satisfied.

## Primary and Comparator Models

The primary approach uses elastic-net penalized cause-specific Cox models for:

- First confirmed Tier 1 SVD.
- Non-valve death as the principal competing event.
- Prespecified non-SVD valve failure or reintervention competing events where appropriate.

The fitted cause-specific hazards are combined into cumulative-incidence predictions. A random survival forest tests whether nonlinearities and interactions add reproducible value. A simple Cox comparator uses time since implantation, age, SAVR/TAVR approach, valve size and reference mean gradient. A further ablation removes longitudinal echo-change features to quantify their incremental value.

### Strategy Comparison

| Strategy | Strength | Limitation in this study | Role |
|---|---|---|---|
| Rolling-landmark cause-specific Cox | Uses censored follow-up, updates risk over time, handles competing death, and remains clinically interpretable | Requires prespecified functional forms and may miss complex interactions | **Primary model** |
| Random survival forest | Captures nonlinear effects and interactions without specifying them in advance | Requires more events, is harder to calibrate, and explanations are less stable | Nonlinear comparator |
| Fixed-horizon classifier | Simple deployment target such as “SVD within 3 years” | Excludes or reweights patients without complete horizon follow-up, discards event timing, and needs separate models for each horizon | Benchmark only, implemented with censoring-aware weights |
| Sequence model such as an RNN or transformer | Can learn directly from irregular longitudinal sequences | Data hungry, difficult to audit, vulnerable to site-specific visit patterns, and unjustified with approximately 300 primary events | Exploratory only after a substantially larger, denser cohort |
| Joint longitudinal-survival model | Directly links a repeated echo trajectory to event risk | More assumptions and implementation complexity; difficult with many intermittently measured predictors | Optional research comparator |

The primary choice will change only if a comparator shows reproducible improvement in calibration, discrimination, and decision-curve benefit in locked testing without unacceptable instability or loss of interpretability.

## Candidate Predictors

Predictors are limited to information available by the landmark:

- Patient characteristics and comorbidity, including CKD, diabetes, body size, smoking, cardiovascular disease and documented cancer context.
- Implant approach, manufacturer/model, label size, design and procedural characteristics.
- Stable reference-echo function and PPM.
- Prior echo levels and trajectories, including gradient, EOA, DVI and intraprosthetic regurgitation.
- Symptoms, NYHA class, heart-failure admissions, relevant laboratory trajectories and medications.
- Surveillance history and data-sufficiency indicators.

Displayed “contributing factors” are predictive associations or model explanations. They are not causal claims and do not imply that modifying a feature will change valve durability.

## Longitudinal Review of Confirmed Cases

For every confirmed Tier 1 event, the pipeline produces a pre-event case trajectory rather than a single flattened row. It includes the implant and reference study, every eligible pre-event echo, symptoms and clinical events, competing mechanisms considered, the last event-free landmark, and the later evidence that confirmed the event. Cohort analyses compare these trajectories with event-free follow-up using prespecified descriptive summaries and model coefficients; they identify predictive patterns, not biological causes.

At each pre-event landmark, the explanation layer stores the contribution of grouped clinical concepts to the selected horizon. For the Cox model, the auditable base explanation is the standardized term contribution to the linear predictor. For nonlinear comparators, a validated time-specific explanation method may be used only if it is stable under resampling. The interface reports no more than three grouped factors and their direction, plus the change in explanation since the preceding landmark. Missingness indicators are shown separately from clinical factors.

An explicit note statement such as “SVD,” “degenerating prosthesis,” or “prosthetic stenosis” creates a candidate signal. It does not confirm the primary endpoint by itself. The assertion must be attributed to the patient and prosthetic aortic valve, dated after implantation, and marked for negation, uncertainty, temporality, and author context. Tier 1 confirmation still requires deterministic stage 2/3 HVD plus an intrinsic structural mechanism supported by imaging, operative/explant evidence, or blinded adjudication. A specialist note that cites the relevant imaging may supply evidence to adjudicators, but raw note wording never bypasses the endpoint rules.

## Single-Inference Contract

One inference first returns the current-status gate result. Future-risk probabilities are returned only when `landmark_eligible=true`.

For an eligible event-free landmark, the primary output is:

> Conditional probability of first Tier 1 SVD at 1, 3 and 5 years; locally calibrated risk tier; risk change from the previous landmark; up to three grouped predictive contributions; data-sufficiency status; and a clinician-review action.

Eight- and 10-year risks from implantation are exploratory and must remain absent unless long-horizon calibration has been independently validated. The model does not directly prescribe an echo interval. A versioned clinical policy layer may translate validated risk and current findings into `routine_schedule`, `review_for_earlier_echo`, or `structural_heart_review`. A numeric interval remains null until local governance defines and prospectively validates it.

The machine-readable contract is `outputs/valve_watch_inference.schema.json`. Important behavior is:

- Tier 1 current event: probabilities are null; action is current clinical review.
- Tier 2–4 unresolved status: probabilities are null; action is retrieval/adjudication.
- Event-free eligible landmark: probabilities, risk tier, trajectory, explanation and data sufficiency are returned.
- High future risk: prompt chart review and consideration of earlier echocardiography or structural-heart review; never place an order or diagnose SVD automatically.

## Workflow Placement and Triggers

VALVE-WATCH runs as a passive EHR or valve-registry service. A new finalized echo, CT report, relevant signed note, procedure/reintervention record, death update, scheduled registry refresh, or surveillance due-date event triggers timeline reconstruction and the current-status gate. Preliminary reports do not trigger a durable prediction. If the gate resolves as event-free and the minimum data requirements are met, the service creates a new landmark and invokes the survival model.

The downstream system writes the result to a valve-clinic worklist and may expose a concise EHR panel. Tier 1 and unresolved Tier 2–4 cases appear in a current-review section. Event-free high-risk cases appear in a future-risk section. Clinicians can open the source-linked trajectory, acknowledge or dismiss the flag, request missing records, and document whether an earlier echo or specialist review is appropriate.

## Leakage Controls

1. Apply the current-status gate before creating a prediction row.
2. Require every predictor timestamp to be on or before the landmark.
3. Exclude event-defining measurements and evidence from the same visit as the declared event.
4. Fit imputation, scaling, feature selection and tuning inside training folds only.
5. Keep all records from one patient in one partition.
6. Freeze the alert threshold before testing in a temporal or held-out-site cohort.

## Missing Data and Observation Process

True missingness remains explicit. The Cox models use multiple imputation fitted within training folds plus clinically meaningful missingness indicators. The survival forest may use model-native missing-value handling. Routine last observation carried forward and outcome imputation are prohibited. Sensitivity analyses will address informative surveillance because clinical concern can affect the frequency of echocardiography.

## Evaluation

Performance is evaluated with Uno's C-index, time-dependent AUROC, integrated Brier score, calibration intercept and slope, cumulative-incidence calibration, sensitivity, proportion flagged and decision-curve net benefit. The project-specific go/no-go criteria are C-index at least 0.70, calibration slope 0.80–1.20, and at least 85% sensitivity for 3-year confirmed SVD while flagging no more than 25% of eligible patients. These are operational study criteria, not universal clinical standards.

Subgroup analyses cover SAVR/TAVR, age, sex, race/ethnicity, CKD, BMI/PPM, valve size/model/manufacturer and cancer status. External testing uses a later temporal period or held-out site/manufacturer cohort.

## Prototype and Synthetic Data

The supplied 117-patient dataset supports extraction, linkage and rule testing only. It cannot establish clinical model performance. The 2,000-patient synthetic cohort with a 12-year maximum follow-up, seed `20260916` and a 60%/20%/20% patient split exercises the two-layer routing, endpoint derivation, censoring, competing risks and model code. Synthetic results describe simulation recovery and software behavior, not clinical accuracy.