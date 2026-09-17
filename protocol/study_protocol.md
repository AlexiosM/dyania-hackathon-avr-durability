# Study Protocol

## 1. Study Title and Objectives

**Title:**  
**VALVE-WATCH: Dynamic Prediction of Structural Deterioration and Surveillance Gaps After Bioprosthetic Aortic Valve Replacement**

**Primary Objective:**  
To develop and externally validate a competing-risk survival model that estimates an individual patient's future risk of confirmed structural valve deterioration (SVD) after bioprosthetic surgical or transcatheter aortic valve replacement and identifies patients who may benefit from earlier echocardiographic or structural-heart review.

**Secondary Objectives:**

1. Compare post-implant durability trajectories after SAVR and TAVR without interpreting observational differences as causal treatment effects.
2. Predict hemodynamic valve deterioration (HVD), bioprosthetic valve failure (BVF), and aortic-valve reintervention as distinct secondary outcomes.
3. Determine whether serial changes in mean gradient, effective orifice area (EOA), Doppler velocity index (DVI), and intraprosthetic regurgitation improve prediction beyond implant characteristics and the reference postoperative echocardiogram.
4. Evaluate a risk-adapted surveillance strategy that flags patients for chart review or earlier echocardiography while preserving clinician control over diagnosis and intervention.

The primary use case is post-AVR surveillance. Preoperative selection between SAVR and TAVR is outside the primary prediction task because it requires a separate treatment-effect framework and must not use post-implant information. It may be studied later using a distinct target population and only pre-procedure predictors.

---

## 2. Target Population

### Inclusion Criteria

The primary cohort will include patients who meet all of the following criteria:

1. Age 18 years or older at implantation.
2. Confirmed bioprosthetic valve implanted in the aortic position by SAVR or TAVR.
3. Known implantation date and implant approach. Manufacturer, model, label size, and procedural details will be retained when available but are not mandatory for cohort entry.
4. An interpretable, technically adequate reference transthoracic echocardiogram obtained under stable hemodynamic conditions, preferably 30-90 days after implantation. If unavailable, the earliest stable study within 180 days may be used and will be flagged as a nonstandard reference.
5. Alive and free of confirmed SVD or BVF at the initial reference-echo landmark. This landmark is the date of the selected stable reference study, usually 30-90 days after implantation and no later than 180 days in the flagged fallback analysis.
6. At least one subsequent clinical or echocardiographic assessment and at least 12 months of potential follow-up after the landmark, unless a primary endpoint, competing event, or death occurs earlier.

The primary analysis will include first-time bioprosthetic SAVR and TAVR recipients. Concomitant coronary bypass or non-aortic valve procedures will not automatically exclude a patient when aortic-prosthesis measurements and outcomes can be identified separately. These procedures will be retained as covariates and examined in sensitivity analyses.

### Exclusion Criteria

Patients will be excluded from the primary cohort for any of the following:

1. Mechanical aortic prosthesis, native aortic valve without replacement, or a prosthesis confined to another valve position.
2. Unconfirmable aortic prosthesis identity, implantation date, or completed procedure status.
3. Index valve-in-valve TAVR, redo SAVR, or another prior aortic prosthesis. These patients will be retained in a separate exploratory redo/valve-in-valve cohort because their anatomy and durability mechanisms differ from first implantation.
4. Active prosthetic-valve endocarditis, clinically adjudicated prosthetic thrombosis, severe paravalvular regurgitation, major malposition, dehiscence, or another severe nonstructural dysfunction at the reference landmark.
5. Early technical or procedural failure before or at the reference-echo landmark, because the primary study concerns subsequent durability rather than peri-procedural performance.
6. Echocardiographic data that cannot be attributed specifically to the aortic prosthesis, including unresolved mixing of native-valve, mitral-prosthesis, and aortic-prosthesis measurements.
7. No usable reference echocardiogram or no subsequent outcome/censoring information.

Cancer, chronic kidney disease, frailty, and other major comorbidities are not automatic exclusions. Cancer will be recorded as active, in remission, historical, recurrent, or metastatic when explicitly documented. Thoracic or mediastinal radiation and cardiotoxic therapy will also be captured. Cancer-related and other non-valve deaths will be handled as competing events rather than removed from the cohort.

Patient-prosthesis mismatch (PPM) is a baseline nonstructural condition and a candidate predictor, not an incident SVD endpoint. Observed PPM will be calculated from the reference-echo EOA indexed to body surface area. Following the 2024 American Society of Echocardiography guidance, moderate and severe PPM will be defined as indexed EOA 0.66-0.85 and <=0.65 cm2/m2, respectively, for BMI <30 kg/m2, and 0.56-0.70 and <=0.55 cm2/m2 for BMI >=30 kg/m2 [4]. PPM will remain unknown when the required measurements or a suitable reference study are unavailable.

### Cohort Size Estimate

Recruitment will be event driven because precision and overfitting risk in a time-to-event prediction model depend on the number of observed endpoint events, follow-up, censoring, and the number of candidate parameter degrees of freedom, not simply on the number of enrolled patients [6]. A large cohort with few confirmed SVD events can still produce an unstable model.

**Development-cohort planning calculation:**

1. The primary penalized Cox model will initially be limited to approximately 20 effective predictor parameters. A parameter means one model degree of freedom, not one named clinical variable; indicator levels, spline terms, and prespecified interactions each consume parameters.
2. We use 15 events per effective parameter as a conservative planning floor: `20 parameters x 15 events = 300 confirmed SVD events`. This is more conservative than the historical 10-events-per-parameter rule and allows for penalization, heterogeneity between valve types, and some loss of information from censoring. It is a transparent preliminary calculation rather than the final sample-size method.
3. Because the supplied hackathon data cannot estimate SVD incidence reliably, the conversion from events to patients uses a planning range of 5.0%-7.5% confirmed SVD during usable follow-up. This gives `300 / 0.075 = 4,000` to `300 / 0.05 = 6,000` patients.
4. Allowing approximately 10% for unusable reference imaging, unresolved linkage, or loss to follow-up increases the operational recruitment range to approximately 4,500-6,700 patients. We therefore plan for **about 4,500-7,000 patients while continuing recruitment until at least 300 confirmed events are observed**.

The planning event rate is an assumption to be replaced by a blinded pilot estimate from participating sites; it is not inferred from synthetic data. If the observed event rate is lower, follow-up or site recruitment will be expanded, or the number of candidate parameters will be reduced before modeling. Synthetic events will never be counted toward the clinical sample-size requirement.

Before database lock, the formal calculation for the SVD cause-specific model will use the Riley time-to-event prediction-model framework implemented in `pmsampsize` [6]. Inputs will include the 5-year SVD event probability, mean follow-up, censoring pattern, the 20 candidate parameter degrees of freedom, and a conservative anticipated Cox-Snell R2. The competing-death model will be checked separately using its own event frequency and parameter count. A joint simulation of both cause-specific processes will then verify precision of the resulting cumulative-incidence predictions under the observed competing-risk pattern. The required sample will be the largest value needed to: (1) estimate overall 5-year risk precisely, (2) target global shrinkage >=0.90, meaning no more than approximately 10% correction for overfitting, and (3) keep optimism in apparent model fit small. The assumptions and executable calculations will be published with the analysis code.

An independent temporal or external-site validation cohort will initially target at least 100 confirmed SVD events, but 100 events is a recruitment floor rather than evidence of adequate precision. Once the final model and its linear-predictor distribution are known, a simulation-based calculation for time-to-event external validation will select the larger sample needed to target a 95% confidence-interval width <=0.10 for the C-index, <=0.30 for the calibration slope, and <=0.20 for the observed/expected risk ratio at 5 years [7,9]. Threshold-performance precision for sensitivity and alert burden will be checked separately using methods for classification thresholds [10]. This may require substantially more than 100 events. Recruitment will continue until these prespecified precision targets are met.

---

## 3. Endpoints

VALVE-WATCH separates **current dysfunction/care-gap detection** from **future SVD prediction**. At each candidate landmark, deterministic VARC-3-based rules first classify the latest available record. A patient with adjudicated Tier 1 SVD has already reached the endpoint: the case is sent for clinical review and the patient leaves the future-SVD risk set from that date. Tier 2 probable SVD, Tier 3 HVD of unknown mechanism, and Tier 4 minimal-data proxy findings trigger source retrieval and adjudication; they are not treated as event-free prediction landmarks until the current status is resolved. Only patients alive and free of confirmed SVD with an eligible, adequately resolved landmark proceed to future-risk calculation.

### Primary Endpoint

The primary endpoint is time from an eligible, event-free post-implant landmark to the first subsequent **Tier 1 confirmed structural SVD with VARC-3 stage 2 or stage 3 HVD** [1,3]. VARC-3 is the primary framework because it jointly defines hemodynamic deterioration, mechanism, and clinically relevant valve failure. The EAPCI/ESC/EACTS durability definition will be applied as a prespecified sensitivity analysis, not pooled with the primary definition, because published HVD/SVD frameworks are not fully interchangeable and can classify the same follow-up study differently [2,8].

HVD will be determined relative to the stable reference echocardiogram:

- **Stage 2 HVD:** an increase in mean transvalvular gradient >=10 mmHg resulting in a mean gradient >=20 mmHg, together with an EOA decrease >=0.3 cm2 or >=25% and/or a DVI decrease >=0.1 or >=20%; or new/worsening intraprosthetic aortic regurgitation by at least one grade resulting in at least moderate regurgitation.
- **Stage 3 HVD:** an increase in mean transvalvular gradient >=20 mmHg resulting in a mean gradient >=30 mmHg, together with an EOA decrease >=0.6 cm2 or >=50% and/or a DVI decrease >=0.2 or >=40%; or new/worsening intraprosthetic aortic regurgitation by at least two grades resulting in severe regurgitation.

For the primary endpoint, HVD must be accompanied by an intrinsic permanent prosthesis abnormality such as leaflet fibrosis, calcification, tear, flail, disruption, wear, or frame/strut deformation, documented by echocardiography, cardiac CT, operative/explant findings, or blinded clinical adjudication. Persistent HVD without structural confirmation may meet Tier 2 probable SVD, while HVD with an unresolved mechanism remains Tier 3; neither is a confirmed primary event.

PPM, paravalvular regurgitation, malposition, pannus or other extrinsic obstruction, thrombosis, endocarditis, and high-flow physiology are not SVD. Non-SVD death and valve reintervention for a non-SVD mechanism are competing events. The event date will be the earliest study date on which the HVD criteria were met once the structural mechanism has been confirmed through the adjudication process.

The model will generate conditional SVD risk at 1, 3, and 5 years after each eligible landmark. Eight- and 10-year cumulative risk from implantation will be exploratory because fewer patients are expected to have sufficiently long follow-up.

Echocardiography can contribute to both predictors and endpoint ascertainment, but never at the same time point. The reference echo and studies completed before a landmark may supply gradient, EOA, DVI, regurgitation, PPM, and trajectory features. A later echo, CT, pathology result, or adjudication record that establishes the event belongs to the outcome and cannot be used as a predictor at the preceding landmark.

The project-specific go/no-go criteria are Uno's C-index >=0.70; calibration slope between 0.80 and 1.20 with no clinically important calibration-in-the-large error at 3 and 5 years; and sensitivity >=85% for 3-year confirmed SVD at a threshold that flags no more than 25% of eligible patients. These values are design choices for this study, not universal standards of clinical usefulness. The locked validation cohort must also show positive decision-curve net benefit compared with fixed surveillance based on time since implantation alone. Failure will be reported without retuning on the test cohort, and confidence intervals around threshold performance will be interpreted against the prespecified precision calculation [10].

### Secondary Endpoints

| Endpoint | Measurement | Timeframe |
|---|---|---|
| Stage 2 or 3 HVD regardless of mechanism | VARC-3 paired-echo gradient, EOA, DVI, and intraprosthetic-regurgitation criteria | Time to first event; 1-, 3-, and 5-year risk |
| Bioprosthetic valve failure | VARC-3 BVF stage 1 (clinically expressive BVD or irreversible stage 3 HVD), stage 2 (reoperation/reintervention), or stage 3 (valve-related death) | Time to first stage and highest stage reached |
| Aortic-valve reintervention | Redo SAVR, valve-in-valve TAVR, or other completed aortic-prosthesis intervention | Time from landmark to procedure |
| Hemodynamic progression | Annualized mean-gradient and peak-velocity increase, EOA/DVI decrease, and change in intraprosthetic regurgitation | Continuous trajectory between dated echocardiograms |
| Alternative valve-dysfunction mechanisms | Adjudicated thrombosis, endocarditis, paravalvular regurgitation, PPM, pannus, malposition, or other nonstructural dysfunction | Time to first mechanism-specific event |
| Clinical deterioration | Heart-failure hospitalization, worsening NYHA class, or valve-related symptoms linked by adjudication to BVD | 1-, 3-, and 5-year risk |

All-cause death, cardiovascular death, cancer-related death, loss to follow-up, and non-SVD valve reintervention will be retained separately to support competing-risk and sensitivity analyses.

Tier 2 probable SVD will support prespecified sensitivity analyses. Tiers 3 and 4 are current surveillance and case-finding outcomes that trigger retrieval or review, not confirmed SVD events. Tier 5 BVF remains a separate patient-important secondary endpoint and does not replace the mechanism-specific primary endpoint.

---

## 4. Proposed Data Sources

| Source | Data Type | Access Pathway | Key Variables |
|---|---|---|---|
| Echocardiography reporting system | Structured measurements and narrative TTE/TEE reports | HL7/FHIR DiagnosticReport and Observation resources, reporting-database export, or approved data-warehouse tables | Study date/context, velocity, peak/mean gradient, LVOT measurements, EOA, indexed EOA, DVI, acceleration time, stroke volume/flow state, intraprosthetic and paravalvular regurgitation, leaflet morphology/motion, LVEF, pulmonary pressure |
| SAVR/TAVR procedural and implant records | Operative reports, cath-lab reports, implant logs, device registry | EHR procedure modules, implant inventory, institutional registry, or STS/ACC TVT-style registry extract | Implant date, SAVR/TAVR approach, primary/redo/valve-in-valve status, manufacturer, model, label size, tissue/design characteristics, deployment details, concomitant procedures |
| Longitudinal EHR encounters and notes | Demographics, diagnoses, symptoms, clinician assessments, hospitalizations | Approved clinical data warehouse and FHIR resources; constrained local clinical-language-model extraction for narrative text | Age, sex, height/weight/BSA, smoking, hypertension, diabetes, CKD/dialysis, CAD, PAD, heart failure, atrial fibrillation, cancer context, NYHA class, symptoms, explicit valve assessments, encounter dates |
| Laboratory system | Structured dated results | Laboratory information system, data warehouse, or FHIR Observation | Creatinine/eGFR, hemoglobin, HbA1c/glucose, lipid profile, calcium, phosphate, PTH, albumin, CRP/ESR, BNP/NT-proBNP, INR |
| Medication orders/administration | Structured medication records | EHR medication tables, FHIR MedicationRequest/MedicationAdministration, pharmacy extract | Anticoagulants, antiplatelets, lipid-lowering, antihypertensive, diabetes, heart-failure/diuretic, and calcium-phosphate therapies with dates and status |
| Cardiac CT and other imaging | Structured findings and narrative reports | PACS/RIS metadata, imaging-report export, or FHIR DiagnosticReport | HALT, reduced leaflet motion, calcification, thrombosis, pannus, frame geometry/expansion, implantation depth |
| Outcome and vital-status sources | Encounters, procedures, mortality, pathology | EHR, claims, regional/national death data where permitted, reintervention registry, surgical pathology | HF hospitalization, redo/valve-in-valve procedure, date/cause of death, explant findings, last known follow-up |

The clinical-language model will extract only explicitly documented facts into a fixed schema with source note IDs and evidence quotations. It is an extraction component, not the endpoint classifier or survival model. The initial implementation will use prompt-constrained extraction rather than fine-tuning on the small prototype. Structured laboratory and medication files will be mapped directly rather than regenerated by the language model. BMI, BSA, indexed EOA, PPM, echo changes/slopes, HVD, SVD, BVF, follow-up intervals, prediction-landmark eligibility, and care-gap labels will be calculated by deterministic code. Ambiguous mechanisms and valve-related clinical events will undergo clinician adjudication.

Extraction will be evaluated against clinician-annotated notes using field-level precision and recall, numeric/date/unit accuracy, negation and temporality accuracy, evidence-span fidelity, and hallucination rate. The extraction prompt, schema, model version, and decoding settings will be locked for evaluation; a stratified error review will include clinically important positive cases and apparent negatives.

### Hackathon Prototype Data

The supplied de-identified prototype contains 117 patients and 215 notes. The existing echo-language screen flags at least one note for 93 patients. The 43,550 laboratory rows and 5,807 medication rows cover only 17 patients. Only a small number of notes explicitly mention SVD or valve failure, so these data are insufficient to estimate clinical model performance.

The prototype will therefore demonstrate ingestion, constrained note extraction, source reconciliation, longitudinal alignment, deterministic endpoint construction, and the model interface. The synthetic demonstration will contain 2,000 patients, at most 12 years of follow-up, and seed `20260916`. It will generate serial echo trajectories, censoring, competing deaths, mechanism-specific events, surveillance gaps, and missingness, with complete latent-truth tables kept separate from the observed tables processed by the pipeline. Synthetic records will be clearly labeled, will not be combined with real patients for clinical performance claims, and will not be presented as evidence that the model generalizes to clinical practice.

**Ground Truth Definition:**

No single routinely available observation is a perfect gold standard. Explant pathology is highly specific but exists only for patients selected for reintervention and therefore overrepresents severe disease. Cardiac CT and detailed leaflet morphology improve etiologic confirmation but are not performed at every follow-up. Reintervention is clinically important but depends on age, frailty, local practice, access to care, and patient preference; it cannot by itself prove that the mechanism was SVD. An explicit SVD diagnosis in a note is useful for case finding but is not sufficiently standardized to serve as ground truth without supporting evidence.

Serial transthoracic echocardiography is therefore the most practical proxy because it is the principal accessible method for longitudinal assessment after AVR and provides standardized changes in valve hemodynamics [2,4]. Its limitation is specificity: HVD can also arise from PPM, thrombosis, endocarditis, pannus, paravalvular regurgitation, high-flow physiology, or measurement error [1-4]. The protocol will preserve these distinctions rather than treat every gradient increase as SVD.

| Evidence tier | Operational definition | Role in analysis | Rationale and limitation |
|---|---|---|---|
| **Tier 1: confirmed structural SVD** | VARC-3 stage 2/3 HVD plus intrinsic permanent leaflet/frame abnormality documented by echo or CT, or operative/explant pathology confirming structural degeneration with compatible pre-intervention dysfunction | Primary endpoint | Highest specificity while remaining feasible without pathology in every patient |
| **Tier 2: probable SVD** | Stage 2/3 HVD present on at least two consecutive clinically distinct echocardiograms, no documented competing mechanism after standardized review, but morphology/pathology unavailable | Prespecified sensitivity endpoint; may support a secondary model | More available than Tier 1 but residual misclassification is possible |
| **Tier 3: HVD of unknown mechanism** | Complete VARC-3 stage 2/3 hemodynamic criteria relative to the reference echo, without adequate information to establish or exclude the mechanism | Secondary endpoint and case-finding pool | Reliable evidence of functional deterioration, but not proof of structural degeneration |
| **Tier 4: minimal-data echo proxy** | Persistent mean-gradient rise meeting the VARC-3 gradient change/final-gradient thresholds, or new moderate/severe intraprosthetic regurgitation, when EOA or DVI is missing | Screening flag only; triggers retrieval/adjudication and is never promoted automatically to primary SVD | Uses the measurements most commonly present in routine reports, but has lower specificity and may reflect flow or measurement differences |
| **Tier 5: clinical valve failure** | Reintervention, clinically expressive BVD, irreversible stage 3 HVD, or valve-related death under VARC-3 BVF definitions | Separate secondary endpoint | Captures patient-important failure but does not uniquely identify SVD and is affected by treatment-selection and access factors |
| **Text-only signal** | Explicit note statement such as `SVD`, `prosthetic stenosis`, or `degeneration` without adequate imaging or procedural support | NLP case-finding only | Useful for recall, but wording and diagnostic certainty vary between clinicians and sites |

For stenotic deterioration, transprosthetic gradients should be confirmed on at least two consecutive measurements when clinically possible, consistent with the EAPCI durability consensus [2]. A single abnormal study can still trigger review, particularly before urgent reintervention, but it will not be considered persistent probable SVD without adjudication. If EOA or DVI is absent, the mean-gradient proxy will remain a screening label rather than being treated as complete VARC-3 HVD. An isolated absolute high gradient without a rise from the patient's stable baseline is insufficient because it may represent baseline PPM. Requiring persistence also addresses evidence that hemodynamic-SVD classifications may not persist on the next echocardiogram [8].

The primary analysis will use Tier 1 only. Sensitivity analyses will use `Tier 1 + Tier 2`, while Tier 3 and Tier 4 will be modeled as separate surveillance outcomes. This prevents a common but clinically important proxy from being discarded while avoiding label leakage and overstatement of diagnostic certainty.

Two cardiologists or structural-heart specialists will independently adjudicate all Tier 1 candidates, Tier 2 candidates, reinterventions, and a stratified sample of apparent non-events while blinded to model predictions. Disagreement will be resolved by a third reviewer. Adjudicators will receive a standardized timeline showing the implant, reference study, serial valve measurements, morphology, symptoms, competing mechanisms, reinterventions, and death information. Every endpoint and proxy label will retain the supporting source record IDs.

---

## 5. Statistical Analysis Plan

### Sample Size

The primary development analysis requires at least 300 confirmed SVD events and an estimated 4,500-7,000 recruited patients under the provisional 5.0%-7.5% event-risk and 10% unusable/loss assumptions detailed in Section 2. The total is event driven: recruitment continues until the event requirement and the formal `pmsampsize` criteria are both satisfied. The primary model is capped at approximately 20 candidate parameter degrees of freedom unless the final sample-size calculation supports more. The nonlinear survival forest is a secondary model and will not justify increasing feature complexity when confirmed events are sparse.

For external validation, at least 100 confirmed events will be accrued as an initial floor, followed by the prespecified simulation-based precision assessment described in Section 2. The ultimate validation size will be the maximum required for precise calibration, discrimination, and observed/expected risk, not the smallest cohort that crosses 100 events.

The supplied 117-patient dataset will not be used to claim model validation. Synthetic data will be used only to verify that censoring, competing events, feature engineering, model fitting, and evaluation code behave as intended.

### Train / Validation / Test Split

All observations from one patient will remain in the same partition. No individual echo, note, or encounter will cross partitions.

For the clinical study, development and testing will be separated primarily by time and site rather than by a simple random row split:

1. Earlier implant years from participating development sites will form the development cohort.
2. Grouped, nested five-fold cross-validation within the development cohort will tune penalization, nonlinear terms, and survival-forest hyperparameters. Imputation and preprocessing will be fitted separately within each training fold.
3. A later implant period and, when available, one or more held-out sites will form the locked test cohort. The test cohort will not be used for feature selection, threshold selection, recalibration, or hyperparameter tuning.
4. The alert threshold will be selected within development data to achieve at least 85% sensitivity for 3-year SVD while flagging no more than 25% of eligible patients, then frozen before test evaluation.

For the synthetic demonstration only, patients will be divided 60%/20%/20% into development, validation, and test sets using independent random streams. These results will be labeled as simulation-recovery checks rather than estimates of clinical performance.

Class imbalance will be handled through penalized time-to-event modeling, event-aware cross-validation, and evaluation measures designed for censoring. Primary performance estimates will use the natural event frequency; the clinical test set will not be artificially balanced. Any event oversampling used for computational experiments will be restricted to training folds and will not determine calibration.

At each candidate rolling landmark, the current-status gate is applied before a prediction row is created. Tier 1 at that visit is recorded as the first confirmed event and removes the patient from subsequent risk sets. Tiers 2–4 are routed to retrieval or adjudication and do not enter the event-free prediction set while unresolved. For an eligible landmark, predictors must have timestamps on or before the landmark and the target must occur afterward. Measurements used to declare an endpoint at a visit cannot be used to predict that same-visit endpoint. Patients will contribute multiple eligible landmark records, with resampling and confidence intervals clustered by patient.

### Modeling Framework

The primary model will use elastic-net penalized cause-specific Cox regression for confirmed SVD and for the principal competing events: non-SVD death and valve reintervention or clinically important valve failure caused by thrombosis, endocarditis, or nonstructural dysfunction. The fitted cause-specific hazards will be combined to estimate the cumulative incidence of SVD at 1, 3, and 5 years.

Patients who develop SVD contribute their event-free history and eligible pre-event landmarks through the first confirmed Tier 1 event date. Patients without confirmed SVD contribute follow-up until non-valve death, censoring at the last reliable contact, or study end. The event-defining visit does not become a prediction landmark for that same event.

A random survival forest will be evaluated as a nonlinear secondary model using the same landmark definitions and leakage restrictions. It may capture interactions and nonlinear trajectories but will not replace the primary model unless it demonstrates reproducible improvement in discrimination, calibration, and net benefit in the locked test cohort. The simple comparator will be an unpenalized or lightly penalized Cox model containing time since implantation, age, SAVR/TAVR approach, valve size, and reference mean gradient.

A censoring-aware fixed 3-year classifier will be evaluated as an implementation benchmark, not the primary analysis, because fixed-horizon classification discards event timing and requires exclusion or weighting of patients without observable horizon status. Recurrent neural networks, transformers, and other sequence models will remain exploratory until a substantially larger cohort contains enough confirmed events and sufficiently dense serial measurements to support their complexity. A joint longitudinal-survival model may be considered as a research comparator if serial echo completeness is adequate.

Candidate predictors will be prespecified from clinical guidance and published SVD risk-factor evidence [3-5] and grouped as follows:

- Patient factors: age at implantation, sex, body size, smoking, hypertension, diabetes, dyslipidemia, CKD/dialysis, anemia, CAD/PAD, heart failure, atrial fibrillation, and documented cancer/treatment context.
- Implant factors: SAVR/TAVR, prosthesis model/design, label size, valve-in-annulus relationship, concomitant procedures, and procedural complications.
- Reference echo: peak velocity/gradient, mean gradient, EOA/indexed EOA, DVI, acceleration time, flow state, intraprosthetic and paravalvular regurgitation, PPM, and ventricular response.
- Longitudinal features: latest value, absolute and percentage change from reference, annualized slope, variability, time since last interpretable echo, and number/timing of previous studies.
- Clinical context: symptoms, NYHA class, HF hospitalization, renal/metabolic laboratory trajectories, and relevant antithrombotic and cardiovascular medications.

Displayed “contributing factors” will describe predictive associations or model explanations at the landmark. They will not be presented as causal effects, treatment targets, or evidence that changing a factor will alter valve durability.

Missing baseline predictors will be addressed by multiple imputation within each training fold, using outcome-independent information available at the landmark. Missingness indicators will be retained for clinically meaningful absent measurements. The survival forest may additionally use model-native missing-value handling. Routine last-observation-carried-forward will not be used because echo visits are irregular and missingness may be informative. Missing outcomes will never be imputed; patients will be censored at their last reliable contact when no event is documented.

### Evaluation Metrics

Performance will be reported with 95% confidence intervals using patient-clustered bootstrap resampling:

- Uno's C-index for overall censored-time discrimination.
- Time-dependent AUROC at 1, 3, and 5 years.
- Brier score at each horizon and integrated Brier score.
- Calibration-in-the-large, calibration slope, and observed-versus-predicted cumulative-incidence plots at each horizon.
- Sensitivity, specificity, positive/negative predictive value, and the proportion flagged at the locked clinical alert threshold.
- Decision-curve net benefit compared with time-since-implant surveillance and reviewing all or no eligible patients.
- Prediction interval or uncertainty/data-sufficiency status when required inputs or follow-up are limited.

Bootstrap optimism correction and nested cross-validation will be used during development. The locked test cohort will be evaluated once. Any post-test recalibration will be explicitly labeled and will require a subsequent independent validation cohort.

### Subgroup Analyses

Performance will be evaluated separately by:

- SAVR versus TAVR.
- Age at implantation (<65, 65-79, and >=80 years).
- Sex and race/ethnicity, where available and sufficiently complete.
- CKD stage/dialysis status.
- BMI <30 versus >=30 kg/m2 and PPM category.
- Valve label size, manufacturer/model, and major platform/design categories.
- Active/history of cancer versus no documented cancer.

For each subgroup, discrimination, calibration, sensitivity at the locked alert threshold, and the proportion flagged will be reported with uncertainty. Small manufacturer/model or demographic strata will be combined only by a prespecified clinically defensible rule; otherwise, results will be labeled insufficient rather than presented as stable estimates. Race/ethnicity will be used for fairness evaluation and will not be included as a default clinical predictor unless a governance review shows that its use improves rather than worsens equity and calibration.

### Comparator / Baseline

The primary model will be compared against:

1. Time since implantation alone.
2. A reduced clinical Cox model using age, SAVR/TAVR approach, valve size, and reference mean gradient.
3. Fixed surveillance based on elapsed time from implantation without individualized risk.
4. The same primary model without longitudinal echo-change features, testing whether serial trajectories add value beyond the reference study.

STS-PROM will not serve as the main comparator because it predicts perioperative risk rather than long-term bioprosthetic SVD. Clinician gestalt may be studied prospectively but is not assumed to be available retrospectively in a standardized form.

---

## 6. Ethical Considerations and Data Privacy

### IRB / Ethics Review

The full clinical study will be submitted to each participating institution's IRB or research ethics committee. A retrospective study using de-identified data may qualify for exemption or expedited review, but this determination will be made by the responsible IRB rather than assumed by the investigators. Where identifiable records are required for linkage or adjudication, the study will seek a waiver of informed consent based on minimal risk, impracticability of contacting the full historical cohort, and documented privacy safeguards.

The synthetic prototype does not involve human-subject intervention and will not be used to make clinical decisions. The project will not prospectively alter surveillance or treatment until external validation, impact assessment, and local governance approval are complete.

### Data Privacy

Identifiable source data will remain inside the participating institution's approved environment. Linkage keys will be stored separately from analytical data and accessible only to authorized personnel. Data access will be role based, logged, and limited to the minimum necessary variables. Transfers between sites will use an approved de-identified or limited dataset under a data-use agreement and encrypted transport/storage.

Clinical-language-model inference will occur on premises or in an institution-approved environment covered by the required contractual and security controls. Raw clinical notes or protected health information will not be sent to an unapproved external model. Model outputs will retain source-record identifiers for audit but will not reproduce unnecessary identifying text. The public GitHub repository will contain code, schemas, aggregate results, and clearly labeled synthetic data only; it will contain no real notes, dates of birth, direct identifiers, or re-identifiable patient-level data.

### Algorithmic Fairness

Fairness assessment will include subgroup-specific calibration, discrimination, sensitivity, false-negative rate, and alert burden across age, sex, race/ethnicity, CKD, body-size/PPM, SAVR/TAVR, cancer status, and valve manufacturer/model groups when sample sizes permit. Differences will be reported with confidence intervals rather than judged from point estimates alone.

Mitigation options will include improved source coverage, subgroup or site recalibration, hierarchical/shrinkage modeling for sparse valve models, and revised thresholds when clinically and ethically justified. Protected attributes will not be removed from the audit dataset merely to make the system appear race- or sex-blind. Deployment will be paused for any subgroup with clinically important under-detection or severe miscalibration that cannot be corrected and independently revalidated.

### Clinical Transparency

Each inference will present:

- Estimated 1-, 3-, and 5-year SVD risk and the risk trajectory since the previous landmark.
- The prediction landmark, implant identity, reference echo, latest included data date, and missing critical inputs.
- A data-sufficiency/uncertainty statement.
- The leading documented factors contributing to the estimate, using coefficient-level contributions for the Cox model and a validated explanation method for the survival forest.
- The reason for any care-gap flag, such as overdue surveillance, worsening symptoms, or accelerating echo measurements.

The inference first reports the current-status gate. When Tier 1 is already present or Tier 2–4 is unresolved, future-risk probabilities are withheld and the output requests current review, source retrieval, or adjudication. For an eligible event-free landmark, the machine-readable response contains conditional 1-, 3-, and 5-year Tier 1 SVD probabilities, a locally calibrated risk tier, change from the prior landmark, up to three grouped predictive contributions, and the data-sufficiency status. Eight- and 10-year risks from implantation remain exploratory and will not be displayed unless independently calibrated.

The model will not directly prescribe a surveillance interval. A separately governed and versioned clinical policy may translate validated output into `routine_schedule`, `review_for_earlier_echo`, or `structural_heart_review`. Any numeric interval will remain null until local governance and prospective evaluation support it.

The system sits passively within the EHR or valve registry. A finalized echo or CT, relevant signed note, procedure/reintervention record, death update, registry refresh, or surveillance due-date event rebuilds the timeline and runs the current-status gate. An eligible event-free result then triggers model inference. Outputs feed a valve-clinic worklist; a high-risk flag prompts chart review and consideration of an earlier echocardiogram or structural-heart consultation. The system does not diagnose SVD, change surveillance automatically, place orders, or recommend reintervention. Final interpretation remains with the treating clinician, and suspected endpoints or alternative mechanisms require imaging review and, when appropriate, multidisciplinary adjudication.

---

## References

1. Généreux P, Piazza N, Alu MC, et al. Valve Academic Research Consortium 3: Updated Endpoint Definitions for Aortic Valve Clinical Research. *J Am Coll Cardiol.* 2021;77:2717-2746. https://doi.org/10.1016/j.jacc.2021.02.038
2. Capodanno D, Petronio AS, Prendergast B, et al. Standardized definitions of structural deterioration and valve failure in assessing long-term durability of transcatheter and surgical aortic bioprosthetic valves. *Eur Heart J.* 2017;38:3382-3390. https://doi.org/10.1093/eurheartj/ehx303
3. Pibarot P, Herrmann HC, Wu C, et al. Standardized Definitions for Bioprosthetic Valve Dysfunction Following Aortic or Mitral Valve Replacement: JACC State-of-the-Art Review. *J Am Coll Cardiol.* 2022;80:545-561. https://doi.org/10.1016/j.jacc.2022.06.002
4. Zoghbi WA, Jone PN, Chamsi-Pasha MA, et al. Guidelines for the Evaluation of Prosthetic Valve Function With Cardiovascular Imaging. *J Am Soc Echocardiogr.* 2024;37:2-63. https://www.asecho.org/wp-content/uploads/2024/01/PIIS0894731723005333.pdf
5. Ochi A, Cheng K, Zhao B, Hardikar AA, Negishi K. Patient Risk Factors for Bioprosthetic Aortic Valve Degeneration: A Systematic Review and Meta-Analysis. *Heart Lung Circ.* 2020;29:668-678. https://doi.org/10.1016/j.hlc.2019.09.013
6. Riley RD, Ensor J, Snell KIE, et al. Calculating the sample size required for developing a clinical prediction model. *BMJ.* 2020;368:m441. https://doi.org/10.1136/bmj.m441
7. Riley RD, Collins GS, Ensor J, et al. Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study. *BMJ.* 2024;384:e074821. https://doi.org/10.1136/bmj-2023-074821
8. Velders BJJ, Vriesendorp MD, Asch FM, et al. Current definitions of hemodynamic structural valve deterioration after bioprosthetic aortic valve replacement lack consistency. *JTCVS Open.* 2024;19:68-90. https://doi.org/10.1016/j.xjon.2024.02.023
9. Riley RD, Collins GS, Ensor J, et al. Minimum sample size calculations for external validation of a clinical prediction model with a time-to-event outcome. *Stat Med.* 2022;41:1280-1295. https://doi.org/10.1002/sim.9275
10. Whittle R, Ensor J, Archer L, et al. Extended sample size calculations for evaluation of prediction models using a threshold for classification. *BMC Med Res Methodol.* 2025;25:170. https://doi.org/10.1186/s12874-025-02592-4
study_protocol.md
43 KB