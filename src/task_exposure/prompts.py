"""CDRF axis prompt definitions (v4) — economic impact estimation via task classification.

Classifies occupational tasks on four independent axes to estimate AI's economic
reach: C (cognitive complexity), D (physical/deployment requirements),
R (regulatory friction), F (failure consequences). Each axis measures one
dimension of what it would take for AI to meaningfully augment a task.

Axis versions:
  - C v4:   Manual test framework, boundary tests, verification-difficulty
            bump-up, craft/creative inflation fix, social tasks cap
  - D v4.1: Sensorimotor loop + contact complexity framing, driving rule,
            deformable/bimanual bump-ups, augmentation note
  - R v4:   50% threshold framing — measures whether friction binds at the
            economically meaningful threshold, not whether it exists in principle.
            Binding/nominal distinction compresses R1-R2 toward R0 when oversight
            is compatible with the productivity gain.
  - F v3.1: Compounding error bump-up, D-F correlation note, verb-spanning
            "Monitor" example (patched)

P-axis (Presence) deprecated: D v4.1's contact-complexity framing subsumes
the physical co-location signal that P was designed to capture.

Design principles:
  - Each axis measures exactly one thing; no cross-axis conflation.
  - Edge-case indicators help resolve borderlines.
  - Think-first format: reasoning columns precede classification columns.
  - Pipe-delimited output (|| separator) per existing pipeline.
  - Axes do NOT have forced structural symmetry — modifiers reflect
    the phenomena (R push-down, C/F bump-up), not parallel form.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Axis definitions — each is a self-contained block that can be composed
# ---------------------------------------------------------------------------

_HEADER = """\
You are classifying occupational tasks on {n_axes} independent axes simultaneously. \
Consider each task in the specific context of its occupation.

ECONOMIC FRAMING: For each task, ask "What would it take for AI to cut the time \
a worker spends on this task by at least {threshold}%, while maintaining the same \
level of quality?" This grounds classification in economic impact — not full \
replacement, but meaningful productivity gain at current quality standards.

You will receive an OCCUPATION PROFILE with contextual information about the \
occupation, followed by a list of tasks to classify. Use the occupation context \
to disambiguate verbs and activities."""


# ---- C-axis v4 ----

_C_AXIS = """\
=== CAPABILITY (C) — How much cognitive complexity does this task require? ===
C measures the intrinsic reasoning demand of the task — how much thinking, \
judgment, and knowledge synthesis is required. C is purely about COGNITION, \
independent of physical demands (D), failure stakes (F), or regulation (R).

UNDERLYING PRINCIPLE — THE MANUAL TEST:
C-levels reflect how much of the task's decision-making can be compressed into \
a document. Ask: "Could you write a complete how-to document for this task?" — \
considering ONLY the informational content (what to perceive, decide, and \
communicate), NOT the physical execution (that is D).
  - C0: No document needed. What to do is self-evident from the situation.
  - C1: A complete document exists or could be written. Follow the steps.
  - C2: The document needs a "use your judgment" section — conditions interact \
in ways that cannot be fully pre-specified.
  - C3: The document would need "consult an expert" at decision points — the \
judgment requires knowledge that cannot be transferred in a document.
  - C4: There is no document. The output IS the document. The task produces a \
new method, framework, or technique available to other practitioners.

- C0 (Minimal cognition): No reasoning beyond basic perception and action. \
What to do is self-evident from the context. No decision points, no ambiguity.
  Examples: emptying trash bins, sweeping a hallway, restocking shelves with \
pre-labeled items, transcribing a handwritten number into a form field.

- C1 (Procedural): Following explicit multi-step procedures or applying simple \
rules. The instructions exist and are clear; the worker must follow them \
correctly and recognize which rule applies.
  Examples: filing a simple tax return per form instructions, sorting packages \
by zip code, following a recipe, grading a multiple-choice exam with an answer \
key, running a standard lab assay per protocol.

- C2 (Contextual judgment): Integrating multiple information sources and \
exercising judgment where reasonable practitioners might disagree. Rules exist \
but their application requires weighing competing considerations.
  Examples: scheduling a complex project with resource constraints, drafting a \
persuasive business proposal, building rapport with a reluctant client, \
troubleshooting inconsistent assay results by adjusting conditions when the \
standard protocol yields unexpected output, creating a seasonal menu for a \
restaurant.

- C3 (Expert synthesis): Deep domain expertise applied to novel cases that \
don't fit established patterns. The practitioner synthesizes across complex, \
interacting factors using knowledge built through years of training. \
Distinguished from C2 by: the answer cannot be reached by a competent \
generalist — it requires specialized expertise. C3 produces a NEW SOLUTION \
using existing methods.
  Examples: diagnosing a rare autoimmune condition presenting atypically, \
interpreting an atypical biomarker panel in light of a patient's medication \
history and comorbidities where standard reference ranges do not apply, \
optimizing a multinational tax structure across treaty obligations, designing \
a bridge for unusual geological conditions, strategic case theory for complex \
litigation, designing a tasting menu under severe interacting dietary \
constraints (celiac, nightshade allergy, ketogenic) where the standard \
substitution for one restriction violates another, a therapist improvising an \
approach for complex trauma that defies standard protocols.

- C4 (Frontier contribution): Generating transferable knowledge — a new method, \
theory, design, proof, protocol, or framework that other practitioners can \
adopt. Distinguished from C3 by: the output EXTENDS the field's capability \
set. C3 produces a new solution; C4 produces a NEW TOOL FOR SOLVING. After \
this task is complete, practitioners who were not involved can do something \
they could not do before. Dissemination channel is irrelevant — patents, \
open-source releases, training programs, trade publications, and textbooks \
all count.
  Examples: proving a new mathematical theorem, developing a novel surgical \
technique that other surgeons learn, inventing a new programming paradigm \
(MapReduce, transformers), creating a new manufacturing methodology \
(Toyota Production System), developing a new therapeutic modality (DBT), \
synthesizing a novel material with properties not previously available.

C-AXIS KEY BOUNDARY TESTS:
- C0 vs C1: Does the task have decision points where the worker must choose \
between alternatives? If no → C0. If yes → C1+.
- C1 vs C2: Does the task have a DETERMINISTIC BEST OUTCOME given the starting \
conditions, even if reaching it requires skill? If yes → C1. Or does the task \
require choosing among genuinely competing approaches where the "right" answer \
depends on how the worker weighs tradeoffs? If yes → C2+. \
KEY: "Adjust refrigerant charge until subcooling reads 10-12°F" → C1 \
(deterministic target, skill in execution). "Develop a maintenance schedule \
balancing cost, equipment age, and usage patterns" → C2 (multiple valid \
schedules, practitioner weighs tradeoffs).
- C2 vs C3: Could a competent generalist handle this with a good reference, or \
does it require deep domain expertise? Also: can the output be verified by \
someone less expert than the producer? Generalist + easy verification → C2. \
Specialist required → C3+.
- C3 vs C4: Does this task produce a new solution to a specific case, or a new \
method that other practitioners can adopt? Solution → C3. Method → C4.

C-AXIS EDGE-CASE INDICATORS:
Push UP if: (a) Ambiguity dominates — the task sounds simple but practitioners \
report the hard part is deciding WHICH procedure applies, not executing it. \
(b) Competing frameworks — multiple valid approaches exist and choosing requires \
weighing context-dependent tradeoffs.
Push DOWN if: (c) Routinized expertise — the task sounds expert-level but the \
domain has been codified into decision trees or standard protocols a trained \
non-expert can follow. (d) Template with fill-in — the "reasoning" is really \
selecting from a known menu and filling in case-specific details.

BUMP-UP MODIFIER — VERIFICATION DIFFICULTY:
Tasks where output quality cannot be independently verified are harder to \
automate at any C-level, because AI feedback loops are slower and noisier. \
Push the task toward the top of its C-level when: (a) evaluating correctness \
requires expertise comparable to producing the output, or (b) quality is \
inherently subjective and cannot be checked against an objective standard \
(therapeutic rapport, persuasion, aesthetic judgment).
  Contrast: Software with tests (easy verification at C2) vs. strategic advice \
(hard verification at C2). Both are C2, but verification difficulty predicts \
different AI-augmentation timelines.

C-AXIS DISAMBIGUATION:
- THE MANUAL TEST EXCLUDES PHYSICAL TACIT KNOWLEDGE. "Hard to write a manual \
for" because you need to FEEL the dough is a D problem, not a C problem. The \
manual test asks only about informational content: what to perceive, decide, \
and communicate.
- C is about the TASK, not the occupation. A surgeon reviewing literature is C0 \
(retrieval). That same surgeon deciding whether to deviate from protocol \
mid-operation is C3 (expert synthesis under novel conditions).
- C is orthogonal to D. A task can be C0 + high-D (sweeping a floor) or C4 + \
D0 (proving a theorem).
- SOCIAL AND INTERPERSONAL TASKS follow the same C-scale. Greeting customers \
warmly → C0 (scripted). Following a de-escalation protocol → C1. Building \
rapport with a reluctant client → C2 (contextual judgment). Therapeutic \
intervention for complex trauma → C3 (expert synthesis). Social interaction \
tasks rarely exceed C3: when practitioners develop new social methodologies, \
the C4 component is the research and dissemination — a cognitive task — not \
the interpersonal interaction that generated the insight.

COMMON ERROR — VERBS THAT SPAN THE FULL RANGE:
"Analyze," "evaluate," "develop," and "create" appear at every C-level:
  - "Analyze" → C0 (read a dashboard), C1 (apply a checklist), C2 (weigh \
competing interpretations), C3 (synthesize across complex expert factors).
  - "Create" → C1 (fill a template), C2 (draft a proposal with audience \
judgment), C3 (design a novel solution using expert knowledge), C4 (invent a \
new method others adopt).
  - "Develop a new recipe" → C2 (novel instance, consumed by diners). \
"Develop a cooking technique that other chefs adopt" → C4 (transferable method).
Do not assign C-level from the verb. Examine what decision complexity the \
worker actually faces.

COMMON ERROR — CRAFT AND CREATIVE INFLATION:
Novel outputs in craft and creative fields (hairstyles, recipes, arrangements, \
repairs) are typically C2-C3, NOT C4. A novel hairstyle is consumed by the \
client; it does not enter a knowledge commons. A novel repair solution solves \
one case; it does not change the field's capabilities. C4 requires that the \
output produces transferable knowledge — a method, technique, or framework \
that other practitioners can learn from and build on. Novel combinations of \
existing techniques are C3 unless the combination itself becomes a method \
others adopt.

COMMON ERROR — OCCUPATION-LEVEL INFLATION:
Tasks within high-prestige occupations are NOT automatically high-C. Many tasks \
in elite occupations are C0-C1:
  - Surgeon: "Dictate operative notes" → C0 (transcription from memory)
  - Lawyer: "File a motion for extension of time" → C1 (fill in standard form)
  - Professor: "Enter grades into the LMS" → C0 (data entry)
Classify the TASK, not the occupation."""


# ---- C-axis v2 (manual test as unified reasoning framework) ----

_C_AXIS_V2 = """\
=== COGNITIVE COMPLEXITY (C) — How much reasoning does this task require? ===
C measures the intrinsic reasoning demand of the task — how much thinking, \
judgment, and knowledge synthesis is required. C is purely about COGNITION, \
independent of physical demands (D), failure stakes (F), or regulation (R).

THE MANUAL TEST — YOUR PRIMARY REASONING TOOL:
For every task, ask: "Could you write a complete how-to document that would \
let a trained worker perform this task correctly every time?" Consider ONLY \
the informational content (what to perceive, decide, and communicate), NOT \
the physical execution (that is D-axis).

Your answer to the manual test determines the C-level:

- C0 (No manual needed): What to do is self-evident from the situation. \
No decision points, no ambiguity. The task is fully specified by its context.
  Manual test: writing a manual would be absurd — it would say "do the \
obvious thing."
  Examples: emptying trash bins, sweeping a hallway, restocking shelves with \
pre-labeled items, transcribing a handwritten number into a form field.

- C1 (Complete manual exists): The task has decision points, but every \
decision can be fully specified in advance. A step-by-step document could \
cover all cases the worker will encounter. The worker follows the steps and \
recognizes which rule applies.
  Manual test: you could write the complete manual, and two workers following \
it independently would produce the same output.
  CRITICAL — C1 includes skilled execution: A task can require significant \
SKILL yet still be C1 if there is a deterministic best outcome given the \
starting conditions. "Adjust refrigerant charge until subcooling reads \
10-12°F" is C1 — it requires training and precision, but the target is \
unambiguous and the manual can specify exactly what "correct" looks like.
  Examples: filing a simple tax return per form instructions, sorting packages \
by zip code, following a recipe, grading a multiple-choice exam with an answer \
key, running a standard lab assay per protocol, calibrating equipment to spec.

- C2 (Manual needs "use your judgment"): The manual can describe the process, \
tools, and considerations, but at key decision points it must say "weigh these \
factors and use your judgment." Reasonable practitioners would make different \
choices given the same inputs.
  Manual test: you could write 80% of the manual, but the remaining 20% would \
be "it depends" sections where the worker must weigh competing considerations. \
Two workers following the manual independently would produce DIFFERENT but \
equally defensible outputs.
  CRITICAL — C1 vs C2 boundary: Ask "is there a single correct answer that a \
manual could specify?" If YES → C1. If the task requires choosing among \
genuinely competing approaches where the "right" answer depends on how the \
worker weighs tradeoffs → C2. The presence of SKILL does not make a task C2; \
the presence of TRADEOFFS does.
  Examples: scheduling a complex project with resource constraints, drafting a \
persuasive business proposal, building rapport with a reluctant client, \
troubleshooting inconsistent assay results when the standard protocol yields \
unexpected output, creating a seasonal menu for a restaurant, developing a \
maintenance schedule balancing cost, equipment age, and usage patterns.

- C3 (Manual needs "consult an expert"): The manual would need to say "at this \
point, consult someone with deep domain expertise" because the judgment requires \
knowledge that cannot be transferred in a document — it requires years of \
specialized training and pattern recognition across complex, interacting factors.
  Manual test: you could write a manual for a generalist, but at critical \
decision points only a specialist can proceed. A competent generalist with a \
good reference CANNOT reach the correct answer. The output can only be verified \
by someone with comparable expertise.
  C3 produces a NEW SOLUTION to a specific case using existing methods.
  Examples: diagnosing a rare autoimmune condition presenting atypically, \
interpreting an atypical biomarker panel where standard reference ranges do not \
apply, optimizing a multinational tax structure across treaty obligations, \
designing a bridge for unusual geological conditions, strategic case theory for \
complex litigation, designing a tasting menu under severe interacting dietary \
constraints where the standard substitution for one restriction violates another.

- C4 (No manual possible — the output IS the manual): The task produces \
transferable knowledge — a new method, theory, proof, protocol, or framework \
that other practitioners can adopt. The output EXTENDS the field's capability \
set. After this task is complete, practitioners who were not involved can do \
something they could not do before.
  Manual test: there is no manual because the task is WRITING the manual. \
C3 solves a specific case; C4 produces a NEW TOOL FOR SOLVING that others \
can learn from.
  Dissemination channel is irrelevant — patents, open-source releases, training \
programs, trade publications, and textbooks all count.
  Examples: proving a new mathematical theorem, developing a novel surgical \
technique that other surgeons learn, inventing a new programming paradigm \
(MapReduce, transformers), creating a new manufacturing methodology \
(Toyota Production System), developing a new therapeutic modality (DBT).

C-AXIS BOUNDARY TESTS — APPLY THE MANUAL TEST AT EACH BOUNDARY:
- C0 vs C1: Does the task have decision points where the worker must choose \
between alternatives? If no → C0. If yes → C1+. \
(Manual test: is a manual even necessary?)
- C1 vs C2: Could a manual specify the SINGLE CORRECT outcome for every \
case the worker will encounter? If yes → C1. If the manual must say "use \
your judgment" because reasonable practitioners would reach different \
conclusions → C2+. \
(Manual test: would two workers following the manual independently produce \
the SAME output?)
- C2 vs C3: Could a GENERALIST with a good reference manual handle this task? \
If yes → C2. If the manual would need to say "consult a specialist" because \
the judgment requires years of domain-specific expertise → C3+. \
(Manual test: who is the manual written FOR? If any trained professional → C2. \
If only a specialist → C3.)
- C3 vs C4: Does this task solve a SPECIFIC CASE, or produce a new METHOD \
that other practitioners can adopt? Specific solution → C3. Transferable \
method → C4. \
(Manual test: is the output a solution, or is the output ITSELF a new manual \
that others will follow?)

C-AXIS EDGE-CASE INDICATORS:
Push UP if: (a) Ambiguity dominates — the task sounds simple but practitioners \
report the hard part is deciding WHICH procedure applies, not executing it. \
(b) Competing frameworks — multiple valid approaches exist and choosing requires \
weighing context-dependent tradeoffs.
Push DOWN if: (c) Routinized expertise — the task sounds expert-level but the \
domain has been codified into decision trees or standard protocols a trained \
non-expert can follow. (d) Template with fill-in — the "reasoning" is really \
selecting from a known menu and filling in case-specific details.

C-AXIS DISAMBIGUATION:
- THE MANUAL TEST EXCLUDES PHYSICAL TACIT KNOWLEDGE. "Hard to write a manual \
for" because you need to FEEL the dough is a D problem, not a C problem. The \
manual test asks only about informational content: what to perceive, decide, \
and communicate.
- C is about the TASK, not the occupation. A surgeon reviewing literature is C0 \
(retrieval). That same surgeon deciding whether to deviate from protocol \
mid-operation is C3 (expert synthesis under novel conditions).
- C is orthogonal to D. A task can be C0 + high-D (sweeping a floor) or C4 + \
D0 (proving a theorem).
- SOCIAL AND INTERPERSONAL TASKS follow the same C-scale. Greeting customers \
warmly → C0 (scripted). Following a de-escalation protocol → C1. Building \
rapport with a reluctant client → C2 (contextual judgment). Therapeutic \
intervention for complex trauma → C3 (expert synthesis).

COMMON ERROR — VERBS THAT SPAN THE FULL RANGE:
"Analyze," "evaluate," "develop," and "create" appear at every C-level:
  - "Analyze" → C0 (read a dashboard), C1 (apply a checklist), C2 (weigh \
competing interpretations), C3 (synthesize across complex expert factors).
  - "Create" → C1 (fill a template), C2 (draft a proposal with audience \
judgment), C3 (design a novel solution using expert knowledge), C4 (invent a \
new method others adopt).
Do not assign C-level from the verb. Apply the manual test.

COMMON ERROR — CRAFT AND CREATIVE INFLATION:
Novel outputs in craft and creative fields (hairstyles, recipes, arrangements, \
repairs) are typically C2-C3, NOT C4. A novel hairstyle is consumed by the \
client; it does not enter a knowledge commons. A novel repair solution solves \
one case; it does not change the field's capabilities. C4 requires that the \
output produces transferable knowledge — a method, technique, or framework \
that other practitioners can learn from and build on.

COMMON ERROR — OCCUPATION-LEVEL INFLATION:
Tasks within high-prestige occupations are NOT automatically high-C. Many tasks \
in elite occupations are C0-C1:
  - Surgeon: "Dictate operative notes" → C0 (transcription from memory)
  - Lawyer: "File a motion for extension of time" → C1 (fill in standard form)
  - Professor: "Enter grades into the LMS" → C0 (data entry)
Classify the TASK, not the occupation."""


# ---- D-axis v4.1 ----

_D_AXIS = """\
=== DEPLOYMENT (D) — What physical capability does this task require? ===
D measures the physical capability profile that a task inherently requires — \
what combination of sensing, locomotion, manipulation, and real-time physical \
adaptation is needed. D is organized by CONTACT COMPLEXITY: how much controlled \
physical contact with specific objects the task demands, and how predictable the \
environment is. Independent of cognitive demands (C), failure stakes (F), \
or regulation (R).

- D0 (No physical interaction): All inputs and outputs are informational (text, \
data, audio, images). A disembodied intelligence — receiving and transmitting \
only data — can handle this task entirely. The "brain in a jar" test: could \
an intelligence connected only to the internet do this?
  Examples: writing code, analyzing a spreadsheet, drafting a legal brief, \
conducting a phone interview, reading diagnostic images (radiology), translating \
text, giving verbal instructions over radio.

- D1 (Sensing and/or locomotion without manipulation): The task requires physical \
presence for observation, monitoring, or movement through space, but does NOT \
require controlled physical contact with specific objects. The system perceives \
the environment or navigates through it, but does not grasp, push, cut, join, or \
otherwise physically alter objects. Simple whole-environment actuation without \
object discrimination (e.g., autonomous floor cleaning) stays at D1 because no \
object-specific manipulation is involved.
  Examples: security patrol and surveillance, building/infrastructure inspection \
(visual, acoustic, thermal), environmental monitoring (air quality, weather), \
autonomous delivery navigation (the driving, not the handoff), warehouse \
inventory scanning, underwater pipeline inspection, agricultural drone scouting, \
autonomous floor cleaning.

- D2 (Manipulation in controlled environments): The task requires making physical \
contact with objects — grasping, placing, joining, cutting, or repositioning \
them — in an environment ENGINEERED to reduce variability. Known object \
geometries, fixed workspace layout, consistent lighting, predictable forces. \
The environment cooperates with the machine. A sensorimotor loop is required \
(sense → decide → act → verify), but the environment presents objects in known \
orientations at known positions.
  Examples: factory welding on a jig, automated pharmaceutical dispensing, \
assembly-line pick-and-place with known parts, warehouse picking in engineered \
pod layouts with controlled lighting, CNC machine loading, folding uniform \
items in a purpose-built facility, commercial dishwasher loading in a structured \
kitchen with known dish types.

- D3 (Manipulation in variable environments): Physical manipulation in an \
environment NOT engineered for the machine. Variable geometry, novel object \
instances, unexpected obstacles, or conditions that differ instance to instance. \
The system must adapt its manipulation strategy to conditions it has not been \
specifically trained on. Each instance is a novel arrangement requiring \
perception and adaptation.
  Examples: plumbing repair (variable pipe layouts, different homes), strawberry \
picking (variable geometry and orientation per berry, narrow force tolerance), \
home health aide physical tasks (variable patient bodies and homes), construction \
framing (variable lumber, weather, site geometry), cleaning a cluttered kitchen \
(variable dish arrangement, different kitchens), folding diverse laundry in a \
home (jeans, inside-out shirts — every garment differs), venipuncture/blood draw \
(variable patient anatomy, veins that roll), urban driving (variable pedestrians, \
cyclists, construction zones).

- D4 (Multi-modal real-time manipulation under dynamic uncertainty): Simultaneous \
demands across multiple physical dimensions — fine motor control + gross motor + \
force modulation + multi-sensory integration — in an environment that is actively \
changing DURING task execution. Not merely variable from instance to instance \
(D3), but changing while the system works. The system must make physical \
adjustments faster than deliberative planning allows.
  Examples: emergency surgery (haptic + visual + dexterity + adaptation to \
bleeding and tissue movement), physically restraining an agitated patient \
(adversarial, force modulation, safety), catching or intercepting moving objects \
under time pressure, firefighting while performing rescue (dynamic environment, \
time-critical), delivering a baby (variable anatomy, real-time response to \
complications).

D-AXIS UNDERLYING PRINCIPLE — THE SENSORIMOTOR LOOP:
D-levels reflect the speed and tightness of the perceive → plan → act → verify \
loop that the task requires:
  - D0: No loop. No physical interaction.
  - D1: Open loop or very slow loop. The worker is primarily a PERCEIVER — \
sensing, inspecting, monitoring, or navigating the environment — not a \
MANIPULATOR of objects. Sense → report. Navigate → avoid. No contact-force \
feedback required. D1 tasks require being physically present to observe, hear, \
smell, or navigate, but do NOT require grasping, pushing, cutting, or applying \
directed force to specific objects.
  - D2: Closed loop, slow cycle. Sense object → plan grasp → execute → verify → \
adjust. The environment is predictable, so the loop can take its time. If the \
first grasp fails, the object is still in the same place and orientation.
  - D3: Closed loop, moderate cycle, novel conditions each iteration. Same loop \
as D2, but each new object or environment requires RE-PLANNING, not just \
re-executing. The loop must generalize — this is the "transfer" problem.
  - D4: Closed loop, fast cycle, environment changing WITHIN the loop. The scene \
changes between perception and action. The loop must close faster than \
deliberative planning allows — reactive control, not planned control.

D-AXIS EDGE-CASE INDICATORS:
Push UP if: (a) Environmental variability — the physical environment changes \
between task instances in ways that affect execution. Same warehouse, different \
products each time → D2. Different home layout each time → D3. \
(b) Time-critical reactivity — the task requires physical responses faster than \
deliberative planning allows (catching, stabilizing, dodging).
Push DOWN if: (c) Structured workaround exists — the physical task can be \
re-engineered to reduce environmental variability (structured bins instead of \
random piles, pre-positioned fixtures). Rate the CURRENT typical work \
environment. (d) Single-mode dominance — the task sounds physically complex \
but actually requires only one type of physical interaction done well. Multiple \
simultaneous modes are what distinguishes D4.

BUMP-UP MODIFIERS:
Within a D-level, certain factors push a task toward the NEXT level boundary. A \
single bump-up does not necessarily move to a new level (though it may for tasks \
already borderline), but two or more bump-ups almost certainly increase the level.
  - Narrow force margins: The object does not tolerate rough handling (strawberries, \
eggs, electronic components). Same manipulation, higher penalty for force errors.
  - Deformable objects: Clothes, cables, dough — geometry changes during \
manipulation, requiring continuous re-planning.
  - Bimanual coordination: Task requires two-handed manipulation with coordinated \
timing (assembly, cooking with two implements).
  - Multi-step compounding: Errors in earlier manipulation steps constrain or \
invalidate later steps (furniture assembly, multi-stage cooking).

D-AXIS KEY BOUNDARY TESTS:
- D0 vs D1: Does the task require being physically present to observe or move \
through the world? If all necessary information can be transmitted digitally → D0. \
Voice-only tasks (phone calls, dictation) → D0 even though sound is physical.
- D1 vs D2: PERCEIVER vs MANIPULATOR — Is the worker's physical contribution \
primarily PERCEIVING the environment (inspecting, monitoring, navigating) or \
ACTING ON objects (grasping, pushing, shaping, applying directed force)? If \
perceiving → D1. If acting on specific objects → D2+. A truck driver \
*inspecting* cargo → D1. The same driver *securing* cargo with straps → D2.
- D2 vs D3: Could the workspace be ENGINEERED so the object is always presented \
the same way? If yes, and it currently is → D2. If the task inherently occurs in \
environments that cannot be standardized (homes, outdoor sites, variable \
anatomy) → D3. Within-category object variability matters: "fold towels" in a \
commercial facility (uniform items) → D2. "Fold laundry" in a home (jeans, \
inside-out shirts) → D3.
- D3 vs D4: Can the system PAUSE mid-task for 5 seconds to re-plan without \
causing failure? If yes → D3. If a 5-second pause causes task failure, injury, \
or irreversible damage → D4. Time pressure alone does not make D4 — a strawberry \
picker has economic time pressure but the berry does not move during the pick \
(D3). An ER nurse stabilizing a seizing patient faces time pressure where the \
patient physically moves during intervention (D4).

D-AXIS DISAMBIGUATION:
- D is about the PHYSICAL demands, not the cognitive demands. A surgeon's hand \
movements during suturing are D4. The DECISION about which suture pattern is C3. \
Don't inflate D because the task is cognitively hard.
- D measures the task's inherent physical demands. What changes over time is the \
technology frontier, not the task's D-level.
- Rate TYPICAL CONDITIONS for the task+DWA combination, not best-case or \
worst-case. If the DWA says "restrain violent patients," rate for a violent \
patient — that is what the task describes. If the DWA says "shear animals," rate \
for a typical sheep being shorn (fidgety, uncooperative), not an idealized \
immobilized animal.
- "Inspect" can be D0 (inspect a document), D1 (inspect a bridge visually), or \
D3 (inspect by physically accessing a crawlspace). Context determines D.
- Driving: the vehicle IS the robot and the road IS the environment. Highway \
driving (structured lanes, predictable flow) → D2. Urban driving (variable \
pedestrians, cyclists, construction zones) → D3.
- The D2→D3 boundary is the critical one for current technology: structured vs. \
unstructured environment. This is where most deployed automation systems fail.
- AUGMENTATION NOTE: D rates the physical demands of THIS specific DWA/task. For \
compound tasks decomposed into DWAs, the cognitive DWA may be D0 while the \
physical DWA is D3 — both ratings are correct. The economic model combines them; \
the rater classifies each independently.

COMMON ERROR — NATURAL-LANGUAGE TASK LABELS OBSCURE D-LEVEL:
The same verb can span multiple D-levels depending on what "objects" means:
  - "Fold clothes" at a commercial laundry (uniform towels, fixed station) → D2
  - "Fold clothes" at home (jeans, inside-out shirts, varying fabrics) → D3
  - "Clean surfaces" in a structured lab (known layout, fixed stations) → D2
  - "Clean a kitchen" in a client's home (unknown layout, variable mess) → D3
Do not trust the task label. Examine what physical variability the worker \
actually faces."""


# ---- R-axis v4 (50% threshold framing) ----

_R_AXIS = """\
=== REGULATORY FRICTION (R) — Does regulation prevent AI from achieving a 50% time reduction on this task? ===
Classify based on the US regulatory environment. IMPORTANT: Classify the SPECIFIC \
TASK, not the occupation. Many tasks within heavily-licensed occupations (nursing, \
law, medicine) do not themselves require licensure.

ECONOMIC FRAMING: Assume AI can handle the cognitive requirements (C) and physical \
requirements (D) of this task. Given that technical capability, does regulation \
prevent a licensed professional from using AI assistance to achieve at least a 50% \
reduction in time spent on this task? R measures whether regulatory friction BINDS \
at the economically meaningful threshold — not whether friction exists in principle.

BINDING vs. NOMINAL FRICTION: Many forms of regulatory oversight are compatible \
with massive AI-driven time savings. A pharmacist spending 30 seconds reviewing an \
AI drug-interaction check that replaced 20 minutes of manual work faces nominal \
friction — the oversight exists but does not prevent the 50% gain. R0. A surgeon \
who must independently evaluate a patient before operating faces binding friction — \
no amount of AI preparation eliminates the requirement for personal assessment. R3. \
Rate based on whether the friction prevents the 50% gain, not whether it exists.

- R0 (No binding barrier): No regulatory friction prevents a 50% AI-assisted \
time reduction. This includes tasks with NO regulation AND tasks where oversight \
exists but is compatible with the 50% gain (e.g., brief human review of AI output \
that does not consume the time savings).

- R1 (Preference friction): Documented preference norms favor human involvement \
and may slow adoption, but do not legally prevent the 50% gain. R1 requires that \
you can NAME a specific preference norm (e.g., "patients expect a human nurse for \
bedside manner"). If you cannot name a specific norm, the task is R0. \
Key test: could an organization deploy AI assistance achieving 50% time savings \
despite this preference? If yes but with market friction → R1. If no one would \
notice or care → R0.

- R2 (Oversight that binds): A professional body (not the government) requires \
human oversight or review of AI output, AND that oversight consumes enough of the \
time savings to prevent a 50% reduction. AI can do the preparatory and analytical \
work, but the mandated review is substantive — not a quick sign-off. Violating \
these standards risks loss of credentials or accreditation, but not prosecution. \
Key test: does the required oversight consume more than half the original task \
time? If the oversight is a brief review that preserves most of the AI time \
savings → R0 or R1. If substantive re-evaluation is required → R2.

- R3 (Independent judgment required): A government statute requires INDEPENDENT \
human professional judgment on this specific act. The licensed professional cannot \
simply review AI output and sign off — regulation requires they exercise \
independent evaluation. This friction inherently binds: the statute requires \
human time that AI cannot displace, preventing a 50% gain regardless of AI \
capability. Reserve R3 for acts where AI assistance itself is restricted, not \
merely acts that require a licensed human.

- R4 (Moral agency required): The task's legal or institutional force derives \
from a human staking their personal integrity or liberty. Sworn testimony, \
personal attestation under penalty of perjury, sacramental acts. AI assistance \
is conceptually incoherent for these acts — the 50% question does not apply \
because the human performance IS the output.

R-AXIS KEY BOUNDARIES:
- R0 vs R1: Would a typical client/patient care whether AI did most of the work? \
If yes AND you can name the specific preference norm → R1. If nobody would notice \
or care → R0. Note: if oversight exists but is a quick check that preserves the \
time savings → R0, not R1.
- R1 vs R2: Does a professional BODY formally require human oversight of AI output \
AND does that oversight consume enough time to prevent a 50% gain? If yes → R2. \
If oversight is brief/nominal → R0 or R1.
- R2 vs R3: Does a GOVERNMENT statute require independent professional judgment \
(not just review of AI output)? If yes → R3. Professional body oversight → R2.

JURISDICTIONAL PUSH-DOWN RULE:
When a task is portable (D0 or D1) AND regulatory requirements vary widely across \
jurisdictions, the effective R-level is LOWER than the strictest jurisdiction's \
rules — because the work can migrate to less-regulated jurisdictions. Rate for \
the TYPICAL US regulatory environment, not the strictest state.
  - Licensed in nearly all US states (e.g., medicine, law) → no push-down. \
The barrier is effectively uniform.
  - Licensed in a minority of US states → push down by one level. The work can \
legally be performed from a less-regulated state.
  - For D0 tasks specifically, also consider international arbitrage: if the task \
can be performed remotely from a jurisdiction with no equivalent regulation, \
the effective barrier is further reduced.
  - This rule does NOT apply to D2+ tasks — physical work cannot migrate \
across jurisdictions.

R-AXIS COMMON ERROR — NOMINAL vs. BINDING FRICTION:
Many tasks in licensed professions have regulatory oversight that does NOT prevent \
a 50% AI-assisted time reduction:
- "Develop treatment plan" (Physical Therapist) → R1 (AI drafts 90%, PT reviews \
and adjusts in minutes; patient preference norm for human involvement exists, but \
the 50% gain is easily achieved. Nominal friction.)
- "Pharmacist checking drug interactions" → R0 (AI does the computational check; \
pharmacist's 30-second review does not consume the time savings. Nominal friction.)
- "Surgeon deciding whether to operate" → R3 (independent professional judgment \
required; surgeon must personally evaluate the patient regardless of AI analysis. \
Binding friction — the statute requires human time AI cannot displace.)
- "Lawyer researching case law" → R0 vs "Lawyer representing client in court" → R3

THIN BARRIER — SAME OCCUPATION, DIFFERENT R LEVELS:
Registered Nurse (29-1141):
- Filing patient charts → R0 (no friction at all; AI auto-generates chart notes)
- Administering medication → R0 (AI already assists with dosage calculation, \
drug interaction screening, barcode medication administration; the human bedside \
component is a D/C requirement, not a regulatory barrier. The 50% time reduction \
is achievable within current regulations.)
- Prescribing controlled substances → R3 (DEA requires personal evaluation by \
authorized prescriber — binding friction that AI cannot displace. But this is an \
MD/NP task, not an RN task.)

R-AXIS VERB-CATEGORY GUIDANCE:
- SUPPORT VERBS (prepare, maintain, record, collect, clean, file, organize, \
schedule, enter data): Default to R0 even in licensed occupations. These tasks \
have no binding friction.
- CLINICAL VERBS — split by whether friction binds at 50%:
  - "diagnose" → context-dependent: AI dramatically assists (imaging AI, \
differential generators). Rate R0 when oversight is a brief review that \
preserves time savings. Rate R2 when professional body requires substantive \
re-evaluation that consumes the savings. Rate R3 when statute requires the \
clinician's independent evaluation (e.g., pathology sign-out, psychiatric \
diagnosis — binding friction).
  - "administer medication" → R0 (AI already assists with dosage/interaction \
checks and barcode verification; 50% time reduction achievable within current \
regulations; physical bedside presence is a D requirement, not R)
  - "prescribe controlled substances" → R3 (DEA requires personal evaluation \
by authorized prescriber — binding)
  - "perform surgery" → R3 (independent judgment required for intraoperative \
decisions — binding; AI assists with planning but cannot displace the \
surgeon's in-procedure evaluation)
- APPROVAL VERBS (certify, sign, stamp, seal, attest, authorize): R3 when the \
act requires independent professional judgment. R0-R1 when routine sign-off.
- TEACHING VERBS (lecture, instruct, grade): Typically R0. K-12 state \
certification → R3 (government statute). Institutional accreditation → R2.
- Verb + occupation context matters more than verb alone.

R-AXIS SOC HIERARCHY GUIDANCE:
- Tasks performed by technicians, assistants, and aides (SOC XX-3xxx, 25-9xxx, \
31-xxxx) are typically R0-R1 even when the supervising profession requires R3."""


# ---- R-axis v5 (regulatory assignment framing) ----

_R_AXIS_V5 = """\
=== REGULATORY FRICTION (R) — Does custom or regulation assign this task to a particular professional? ===
Classify based on the US regulatory environment. IMPORTANT: Classify the SPECIFIC \
TASK, not the occupation. Many tasks within heavily-licensed occupations (nursing, \
law, medicine) are not themselves assigned to a credentialed professional by any \
regulation or standard.

R measures whether custom, professional standards, or government statute specifies \
that a particular type of professional must perform THIS specific act. R is about \
the REGULATORY LANDSCAPE — who is required to do the work — not about whether AI \
can or cannot assist.

- R0 (No assignment): No regulation, standard, or established custom specifies \
who must perform this task. Anyone with the relevant skill could do it. This \
includes tasks performed within licensed occupations where the specific task \
itself has no professional assignment — filing charts, scheduling appointments, \
cleaning equipment, entering data.

- R1 (Custom or preference): Established professional or social norms expect a \
particular type of professional to perform this task, but no formal standard or \
law requires it. R1 requires that you can NAME a specific norm (e.g., "patients \
expect a human nurse for bedside manner," "clients expect a human financial \
advisor for portfolio discussions"). If you cannot name a specific norm → R0. \
Key test: would a client, patient, or peer object if a non-professional \
performed this task? If yes and you can name the norm → R1. If nobody would \
notice or object → R0.

- R2 (Professional body requirement): A professional body (not the government) \
has adopted standards specifying that a credentialed professional must perform \
or directly oversee this task. Violating these standards risks loss of \
credentials, accreditation, or professional standing — but not criminal \
prosecution. The requirement comes from the profession's own governance, not \
from statute. \
Key test: is there a specific professional standard or accreditation \
requirement you can cite? If yes → R2. If it is only custom → R1.

- R3 (Government statute): A government statute or regulation specifies that a \
licensed professional must perform this specific act. The legal authority comes \
from the state, not from the profession itself. Violation is a legal offense — \
practicing without a license, unauthorized practice, regulatory infraction. \
Key test: could someone face legal consequences (not just professional \
sanctions) for performing this task without the required credential? If yes → R3.

- R4 (Moral agency required): The task's legal or institutional force derives \
from a human staking their personal integrity or liberty. Sworn testimony, \
personal attestation under penalty of perjury, sacramental acts. The task is \
not about professional assignment but about human moral participation — the \
human IS the output.

R-AXIS KEY BOUNDARIES:
- R0 vs R1: Would a client/patient/peer object if a non-credentialed person did \
this? If yes AND you can name the norm → R1. If no one would notice → R0.
- R1 vs R2: Has a professional body formally adopted a standard requiring a \
credentialed professional? If yes (citable standard) → R2. If only custom → R1.
- R2 vs R3: Does a GOVERNMENT statute require a licensed professional for this \
specific act? Government law → R3. Professional body standard → R2. The \
distinction is WHO imposes the requirement: the state or the profession.
- R3 vs R4: Does the requirement exist because the professional has specialized \
knowledge (R3), or because the task inherently requires a human moral agent (R4)? \
Testifying under oath → R4 (anyone can testify; the sworn act requires a human). \
Prescribing controlled substances → R3 (requires medical knowledge and license).

JURISDICTIONAL PUSH-DOWN RULE:
When a task is portable (D0 or D1) AND regulatory requirements vary widely across \
jurisdictions, the effective R-level is LOWER than the strictest jurisdiction's \
rules — because the work can migrate to less-regulated jurisdictions. Rate for \
the TYPICAL US regulatory environment, not the strictest state.
  - Licensed in nearly all US states (e.g., medicine, law) → no push-down. \
The barrier is effectively uniform.
  - Licensed in a minority of US states → push down by one level. The work can \
legally be performed from a less-regulated state.
  - For D0 tasks specifically, also consider international arbitrage: if the task \
can be performed remotely from a jurisdiction with no equivalent regulation, \
the effective barrier is further reduced.
  - This rule does NOT apply to D2+ tasks — physical work cannot migrate \
across jurisdictions.

SAME OCCUPATION, DIFFERENT R LEVELS:
Registered Nurse (29-1141):
- Filing patient charts → R0 (no regulation assigns charting to a specific \
professional; clerks, medical assistants, and AI systems all do this)
- Administering medication → R3 (state nurse practice acts specify that \
medication administration requires a licensed nurse or higher credential; \
this is a government statute, not just professional custom)
- Prescribing controlled substances → R3 (DEA requires a licensed prescriber; \
but this is an MD/NP task, not an RN task — classify the TASK, not the \
occupation)

Lawyer (23-1011):
- Researching case law → R0 (no regulation assigns legal research to lawyers; \
paralegals, law students, and AI tools all perform legal research)
- Representing a client in court → R3 (unauthorized practice of law statutes \
restrict courtroom representation to licensed attorneys)
- Signing a declaration under penalty of perjury → R4 (the declarant stakes \
personal liberty; this is moral agency, not professional assignment)

R-AXIS VERB-CATEGORY GUIDANCE:
- SUPPORT VERBS (prepare, maintain, record, collect, clean, file, organize, \
schedule, enter data): Default to R0 even in licensed occupations. These tasks \
are not assigned to a specific professional by any regulation.
- CLINICAL/PROFESSIONAL VERBS — split by whether regulation assigns the act:
  - "diagnose" → context-dependent: formal diagnosis is often assigned by \
statute to a licensed clinician (R3). Preliminary assessment or screening \
may not be (R0-R1). Check whether the DWA describes a formal diagnostic \
act or a screening/triage function.
  - "administer medication" → typically R3 (state nurse practice acts assign \
medication administration to licensed professionals)
  - "prescribe" → R3 (government statute assigns prescriptive authority to \
licensed prescribers)
  - "perform surgery" → R3 (government statute restricts surgical acts to \
licensed physicians)
- APPROVAL VERBS (certify, sign, stamp, seal, attest, authorize): R3 when \
statute assigns the approval authority to a licensed professional. R4 when \
the act requires personal moral commitment (sworn testimony, attestation \
under penalty of perjury). R0-R1 when the approval is routine and not \
assigned to a specific credential.
- TEACHING VERBS (lecture, instruct, grade): Typically R0. K-12 state \
certification → R3 (government statute). University teaching → R2 \
(institutional accreditation, not government statute).
- Verb + occupation context matters more than verb alone.

R-AXIS SOC HIERARCHY GUIDANCE:
- Tasks performed by technicians, assistants, and aides (SOC XX-3xxx, 25-9xxx, \
31-xxxx) are typically R0-R1 even when the supervising profession requires R3. \
The regulation assigns the SUPERVISORY act to the professional, not every task \
performed under supervision.

COMMON ERROR — OCCUPATION-LEVEL INFLATION:
A licensed occupation does NOT mean every task is regulated. Most tasks within \
any occupation — including medicine, law, and engineering — are R0. Charting, \
scheduling, cleaning, communicating, organizing, and planning are not assigned \
to any specific professional by regulation, even when they happen inside a \
hospital or courtroom. Classify the TASK."""


# ---- R-axis v6 (pure regulatory taxonomy — no economic binding question) ----

_R_AXIS_V6 = """\
=== REGULATORY FRICTION (R) — What regulatory constraints apply to this task? ===
Classify based on the US regulatory environment. IMPORTANT: Classify the SPECIFIC \
TASK, not the occupation. Many tasks within heavily-licensed occupations (nursing, \
law, medicine) are not themselves subject to any regulatory constraint.

R measures the SOURCE AND STRENGTH of regulatory constraints on THIS SPECIFIC ACT. \
R is a factual question about the regulatory landscape — who, if anyone, has \
authority over who may perform this task. The economic consequences of these \
constraints are handled separately; R classifies the constraints themselves.

- R0 (No regulatory constraint): No regulation, professional standard, or \
established custom restricts who may perform this task. Anyone with the relevant \
skill could do it. This includes tasks performed within licensed occupations where \
the specific task itself is not subject to any restriction — filing charts, \
scheduling appointments, cleaning equipment, entering data, researching \
information, preparing materials.

- R1 (Preference or custom): Established professional or social norms expect a \
particular type of professional to perform this task, but no formal standard or law \
requires it. Violation produces market friction (client discomfort, reputational \
cost) but not legal or professional consequences. \
Key test: would a client, patient, or peer object if a non-credentialed person \
performed this task? If yes and you can identify an established norm → R1. \
If nobody would notice or care → R0.

- R2 (Professional body standard): A professional body (not the government) has \
adopted standards requiring a credentialed professional to perform or directly \
oversee this task. Violation risks loss of credentials, accreditation, or \
professional standing — but not criminal prosecution. The requirement comes from \
the profession's own governance, not from statute. \
Key test: does a professional body standard exist that requires a credentialed \
professional for this task? If yes → R2. If only custom or preference → R1.

- R3 (Government statute): A government statute or regulation specifically \
restricts this act to licensed professionals. Performing this act without the \
required credential is a legal offense — unauthorized practice, regulatory \
infraction, or criminal violation. \
Key test: does the statute create a SPECIFIC PROHIBITION — would a competent but \
unlicensed person face prosecution for performing THIS act? Reserve R3 for acts \
the statute specifically targets. A broad scope-of-practice statute that defines \
what a profession includes does not automatically make every task within that \
scope R3 — only acts the statute specifically restricts.

- R4 (Moral agency required): The task's legal or institutional force derives \
from a human staking their personal integrity or liberty. Sworn testimony, \
personal attestation under penalty of perjury, sacramental acts. The task is \
not about professional restriction but about human moral participation — the \
human IS the output.

R-AXIS KEY BOUNDARIES:
- R0 vs R1: Would a client/patient/peer object if a non-credentialed person did \
this? If yes AND you can identify a specific norm → R1. If no one would notice → R0.
- R1 vs R2: Has a professional body formally adopted a standard requiring a \
credentialed professional? Professional body standard → R2. Custom only → R1.
- R2 vs R3: Does a GOVERNMENT statute specifically restrict this act? \
Government law → R3. Professional body standard → R2. The distinction is WHO \
imposes the requirement: the state or the profession.
- R3 vs R4: Does the requirement exist because the professional has specialized \
knowledge (R3), or because the task inherently requires a human moral agent (R4)? \
Testifying under oath → R4 (the sworn act requires a human). \
Prescribing controlled substances → R3 (requires medical license).

R-AXIS CRITICAL DISTINCTION — SPECIFIC RESTRICTION vs BROAD SCOPE:
Many licensed professions have scope-of-practice statutes that broadly define what \
the profession encompasses. These broad definitions do NOT make every task within \
the scope a specifically restricted act. R3 requires that the statute creates a \
specific prohibition on unlicensed performance of THIS act — not merely that the \
act falls within a broadly defined professional scope.
  - "Prescribe controlled substances" → R3 (DEA specifically restricts prescriptive \
authority; unlicensed prescribing is a criminal offense)
  - "Represent a client in court" → R3 (unauthorized practice of law statutes \
specifically prohibit courtroom representation by non-attorneys)
  - "Take patient vital signs" → R0 (no statute specifically prohibits unlicensed \
persons from taking vital signs; medical assistants, nursing aides, and family \
members all do this routinely)
  - "Apply hair dye" → R0 (no specific prohibition; clients routinely do this \
themselves at home)

SAME OCCUPATION, DIFFERENT R LEVELS:
Registered Nurse (29-1141):
- Filing patient charts → R0 (no restriction on who performs charting; clerks, \
medical assistants, and automated systems all do this)
- Taking vital signs → R0 (no specific prohibition; nursing aides, medical \
assistants, and family members take vital signs)
- Administering medication → R3 (state nurse practice acts specifically restrict \
medication administration to licensed professionals; unlicensed medication \
administration is a legal offense in most states)
- Prescribing controlled substances → R3 (DEA requires a licensed prescriber; \
but this is an MD/NP task, not an RN task — classify the TASK, not the occupation)

Lawyer (23-1011):
- Researching case law → R0 (no restriction; paralegals, law students, and \
anyone can research case law)
- Drafting contracts → R1 (clients generally expect a lawyer, but paralegals \
and business professionals draft routine contracts without legal consequence)
- Representing a client in court → R3 (unauthorized practice of law statutes \
specifically restrict courtroom representation to licensed attorneys)
- Signing a declaration under penalty of perjury → R4 (the declarant stakes \
personal liberty; this is moral agency, not professional restriction)

R-AXIS VERB-CATEGORY GUIDANCE:
- SUPPORT VERBS (prepare, maintain, record, collect, clean, file, organize, \
schedule, enter data): Default to R0 even in licensed occupations. No statute \
specifically restricts these activities.
- CLINICAL/PROFESSIONAL VERBS — split by whether statute specifically restricts:
  - "diagnose" → context-dependent: formal diagnosis (e.g., pathology sign-out, \
psychiatric diagnosis) is specifically restricted by statute (R3). Preliminary \
assessment, screening, or triage is not specifically restricted (R0-R1).
  - "administer medication" → typically R3 (state nurse practice acts specifically \
restrict medication administration to licensed professionals)
  - "prescribe" → R3 (statute specifically restricts prescriptive authority)
  - "perform surgery" → R3 (statute specifically restricts surgical acts)
- APPROVAL VERBS (certify, sign, stamp, seal, attest, authorize): R3 when \
statute requires a licensed professional's certification. R4 when the act \
requires personal moral commitment (sworn testimony, attestation under perjury).
- TEACHING VERBS (lecture, instruct, grade): Typically R0. K-12 public school \
teaching → R3 (state certification statutes specifically restrict who may teach \
in public schools). University teaching → R0-R1 (institutional preference, no \
statute).
- Verb + occupation context matters more than verb alone.

R-AXIS SOC HIERARCHY GUIDANCE:
- Tasks performed by technicians, assistants, and aides (SOC XX-3xxx, 25-9xxx, \
31-xxxx) are typically R0-R1 even when the supervising profession requires R3. \
The statute restricts the supervisory professional's act, not every task \
performed under supervision.

COMMON ERROR — OCCUPATION-LEVEL INFLATION:
A licensed occupation does NOT mean every task is regulated. Most tasks within \
any occupation — including medicine, law, and engineering — are R0. Charting, \
scheduling, cleaning, communicating, organizing, and planning are not restricted \
by any statute, even when they happen inside a hospital or courtroom. \
Classify the TASK."""


# ---- R-axis v7 (v6 definitions + soft augmentation anchor) ----

_R_AXIS_V7 = """\
=== REGULATORY FRICTION (R) — What regulatory constraints apply to this task? ===
Classify based on the US regulatory environment. IMPORTANT: Classify the SPECIFIC \
TASK, not the occupation. Many tasks within heavily-licensed occupations (nursing, \
law, medicine) are not themselves subject to any regulatory constraint.

R classifies regulatory constraints in TWO STEPS:
  Step 1: What constraint EXISTS on who may perform this task?
  Step 2: Does that constraint BIND when a licensed professional uses AI assistance?

STEP 1 — IDENTIFY THE CONSTRAINT:

- R0 (No regulatory constraint): No regulation, professional standard, or \
established custom restricts who may perform this task. Anyone with the relevant \
skill could do it. This includes tasks performed within licensed occupations where \
the specific task itself is not subject to any restriction — filing charts, \
scheduling appointments, cleaning equipment, entering data, researching \
information, preparing materials.

- R1 (Preference or custom): Established professional or social norms expect a \
particular type of professional to perform this task, but no formal standard or law \
requires it. Violation produces market friction (client discomfort, reputational \
cost) but not legal or professional consequences. \
Key test: would a client, patient, or peer object if a non-credentialed person \
performed this task? If yes and you can identify an established norm → R1. \
If nobody would notice or care → R0.

- R2 (Professional body standard): A professional body (not the government) has \
adopted standards requiring a credentialed professional to perform or directly \
oversee this task. Violation risks loss of credentials, accreditation, or \
professional standing — but not criminal prosecution. The requirement comes from \
the profession's own governance, not from statute. \
Key test: does a professional body standard exist that requires a credentialed \
professional for this task? If yes → R2. If only custom or preference → R1.

- R3 (Government statute): A government statute or regulation specifically \
restricts this act to licensed professionals. Performing this act without the \
required credential is a legal offense — unauthorized practice, regulatory \
infraction, or criminal violation. \
Key test: does the statute create a SPECIFIC PROHIBITION — would a competent but \
unlicensed person face prosecution for performing THIS act? Reserve R3 for acts \
the statute specifically targets. A broad scope-of-practice statute that defines \
what a profession includes does not automatically make every task within that \
scope R3 — only acts the statute specifically restricts.

- R4 (Moral agency required): The task's legal or institutional force derives \
from a human staking their personal integrity or liberty. Sworn testimony, \
personal attestation under penalty of perjury, sacramental acts. The task is \
not about professional restriction but about human moral participation — the \
human IS the output.

STEP 2 — AUGMENTATION BINDING TEST (apply to R2 and R3 only):
After identifying a constraint in Step 1, ask: "Does this regulation prevent a \
licensed professional from using AI tools to ASSIST with this task?"

Regulations restrict WHO may perform a task. AI assistance does not change WHO \
is performing it — the licensed professional is still performing the task, just \
with computational support. If the regulation restricts WHO but not HOW, and \
AI assistance is a HOW, then the constraint does not bind for augmentation \
purposes.

- If the constraint DOES NOT BIND (licensed professional can freely use AI to \
assist): Downgrade to R0. The regulation exists but creates zero friction for \
AI augmentation.
  Examples: A nurse using AI to help prioritize patient assessments — the nurse \
still performs the assessment. A lawyer using AI to draft a motion — the lawyer \
still files and signs it. An accountant using AI to identify anomalies in an \
audit — the CPA still signs the opinion.

- If the constraint PARTIALLY BINDS (AI can assist but specific sub-steps \
require unassisted human judgment): Keep R2 or R3 as classified. The regulation \
constrains the workflow even though AI can help with portions.
  Examples: A surgeon using AI for pre-operative planning can delegate planning \
to AI, but the statute specifically restricts the act of cutting — the surgical \
act itself cannot be delegated. A pharmacist using AI to check drug interactions \
can delegate the check, but dispensing the controlled substance requires the \
pharmacist's personal authorization.

- If the constraint FULLY BINDS (the regulation specifically prohibits \
computational delegation or requires unassisted human performance): Keep R3 or R4.
  Examples: Sworn testimony (R4) — the human must personally attest. Certain \
forensic certifications require the examiner to have personally performed the \
analysis, not reviewed AI output.

IMPORTANT: Most R3 constraints DO NOT BIND for augmentation. A licensed \
professional using AI assistance is still a licensed professional performing \
the task. The default for R3 tasks where the professional remains in the loop \
is to downgrade to R0. Only keep R3 when the statute specifically restricts \
the METHOD (not just who may do it) or requires personal, unassisted performance.

R-AXIS KEY BOUNDARIES:
- R0 vs R1: Would a client/patient/peer object if a non-credentialed person did \
this? If yes AND you can identify a specific norm → R1. If no one would notice → R0.
- R1 vs R2: Has a professional body formally adopted a standard requiring a \
credentialed professional? Professional body standard → R2. Custom only → R1.
- R2 vs R3: Does a GOVERNMENT statute specifically restrict this act? \
Government law → R3. Professional body standard → R2. The distinction is WHO \
imposes the requirement: the state or the profession.
- R3 vs R4: Does the requirement exist because the professional has specialized \
knowledge (R3), or because the task inherently requires a human moral agent (R4)? \
Testifying under oath → R4 (the sworn act requires a human). \
Prescribing controlled substances → R3 (requires medical license).
- AFTER boundary classification, apply the AUGMENTATION BINDING TEST to R2/R3.

R-AXIS CRITICAL DISTINCTION — SPECIFIC RESTRICTION vs BROAD SCOPE:
Many licensed professions have scope-of-practice statutes that broadly define what \
the profession encompasses. These broad definitions do NOT make every task within \
the scope a specifically restricted act. R3 requires that the statute creates a \
specific prohibition on unlicensed performance of THIS act — not merely that the \
act falls within a broadly defined professional scope.
  - "Prescribe controlled substances" → Step 1: R3. Step 2: constraint partially \
binds (AI can suggest, but the prescriber must personally authorize) → keep R3.
  - "Represent a client in court" → Step 1: R3. Step 2: constraint partially \
binds (AI can help prepare, but courtroom representation requires the attorney's \
personal presence and judgment) → keep R3.
  - "Take patient vital signs" → Step 1: R0. No statute restricts this. \
Step 2: not applicable.
  - "Apply hair dye" → Step 1: R0. No specific prohibition. Step 2: not applicable.

SAME OCCUPATION, DIFFERENT R LEVELS:
Registered Nurse (29-1141):
- Filing patient charts → R0 (no restriction; Step 2 not needed)
- Taking vital signs → R0 (no restriction; Step 2 not needed)
- Administering medication → Step 1: R3 (state nurse practice acts specifically \
restrict medication administration). Step 2: constraint partially binds — AI can \
help with dosage calculation and interaction checks, but the nurse must personally \
administer the medication → keep R3.
- Assessing patient condition → Step 1: R2 (nursing standards require RN \
assessment). Step 2: constraint does not bind — a nurse using AI to help \
synthesize vital signs and patient history is still personally assessing the \
patient → downgrade to R0.

Lawyer (23-1011):
- Researching case law → R0 (no restriction; Step 2 not needed)
- Drafting contracts → R1 (client preference; Step 2 not needed for R1)
- Representing a client in court → Step 1: R3. Step 2: constraint partially \
binds — AI can help prepare arguments but the attorney must personally appear \
and advocate → keep R3.
- Signing a declaration under penalty of perjury → R4 (moral agency; the \
declarant stakes personal liberty)

Elementary School Teacher (25-2021):
- Preparing lesson plans → R0 (no restriction on who creates lesson plans; \
Step 2 not needed)
- Grading student work → R0 (no statute restricts grading; Step 2 not needed)
- Leading classroom instruction → Step 1: R3 (state certification statutes \
restrict who may teach in public schools). Step 2: constraint does not bind — \
a certified teacher using AI to assist with instruction delivery is still \
a certified teacher leading the class → downgrade to R0.

R-AXIS VERB-CATEGORY GUIDANCE:
- SUPPORT VERBS (prepare, maintain, record, collect, clean, file, organize, \
schedule, enter data): Default to R0 even in licensed occupations. No statute \
specifically restricts these activities.
- CLINICAL/PROFESSIONAL VERBS — split by whether statute specifically restricts:
  - "diagnose" → formal diagnosis specifically restricted (R3), but Step 2: a \
doctor using AI to help interpret scans is still diagnosing → often downgrade \
to R0 unless the statute requires unassisted analysis.
  - "administer medication" → R3, partially binds (physical act cannot be \
delegated to AI) → keep R3.
  - "prescribe" → R3, partially binds (prescriber must personally authorize) \
→ keep R3.
  - "perform surgery" → R3, fully binds (the physical act is the restricted \
act) → keep R3.
- APPROVAL VERBS (certify, sign, stamp, seal, attest, authorize): R3 when \
statute requires a licensed professional's certification; Step 2: often \
partially binds (the signature/attestation is the restricted act). R4 when \
the act requires personal moral commitment.
- TEACHING VERBS (lecture, instruct, grade): Typically R0. K-12 public school \
teaching → Step 1: R3, Step 2: does not bind (certified teacher using AI \
assistance is still a certified teacher) → downgrade to R0.
- Verb + occupation context matters more than verb alone.

R-AXIS SOC HIERARCHY GUIDANCE:
- Tasks performed by technicians, assistants, and aides (SOC XX-3xxx, 25-9xxx, \
31-xxxx) are typically R0-R1 even when the supervising profession requires R3. \
The statute restricts the supervisory professional's act, not every task \
performed under supervision.

COMMON ERROR — OCCUPATION-LEVEL INFLATION:
A licensed occupation does NOT mean every task is regulated. Most tasks within \
any occupation — including medicine, law, and engineering — are R0. Charting, \
scheduling, cleaning, communicating, organizing, and planning are not restricted \
by any statute, even when they happen inside a hospital or courtroom. \
Furthermore, even tasks that ARE regulated (R2/R3) often have constraints that \
DO NOT BIND for AI augmentation — a licensed professional using AI tools is \
still a licensed professional. Apply the binding test before finalizing R2/R3. \
Classify the TASK."""


# ---- R-axis v8: broadened R1/R2, graduated downgrade, licensed physical acts ----

_R_AXIS_V8 = """\
=== REGULATORY RESTRICTIONS (R) — What regulatory constraints apply to this task? ===
Classify based on the US regulatory environment. IMPORTANT: Classify the SPECIFIC \
TASK, not the occupation. Many tasks within heavily-licensed occupations (nursing, \
law, medicine) are not themselves subject to any regulatory constraint.

R classifies regulatory constraints in TWO STEPS:
  Step 1: What constraint EXISTS on who may perform this task?
  Step 2: Does that constraint BIND when a licensed professional uses AI assistance?

STEP 1 — IDENTIFY THE CONSTRAINT:

- R0 (No restriction): No regulation, professional standard, or established norm \
restricts who may perform this task. Anyone with the relevant skill could do it. \
This includes administrative and support tasks performed within licensed \
occupations — filing charts, scheduling appointments, cleaning equipment, \
entering data, preparing materials.

- R1 (Social or market norm): Established professional or social norms expect a \
particular type of professional to perform this task, but no formal standard or \
law requires it. Violation produces market friction — client discomfort, \
reputational cost, reduced employability — but not professional sanctions or \
legal consequences. Key test: would a client, patient, or peer object if a \
non-credentialed person performed this task? If yes and you can identify an \
established norm → R1. If nobody would notice or care → R0.
  Examples: Taking patient vital signs (no statute, but patients expect trained \
clinical staff). Preparing a client's tax return at a commercial firm (no CPA \
requirement for preparation, but clients expect qualified preparers). A \
non-certified personal trainer leading gym classes (clients expect credentials, \
no legal barrier).

- R2 (Professional standard): Established professional standards — whether from a \
formal body or from strong occupational norms — require a credentialed or trained \
professional to perform or directly oversee this task. Violation risks \
professional consequences: loss of credentials, termination for cause, \
significant liability exposure, or loss of accreditation. The requirement comes \
from the profession's own standards, not from government statute. Key test: could \
a practitioner face professional consequences or significant liability exposure \
for performing this task without the expected credentials or training? If yes → \
R2. If only social discomfort → R1.
  Examples: Leading classroom instruction in a public school (professional \
teaching standards set expectations; a district would fire an uncredentialed \
instructor). Drawing blood / performing phlebotomy (hospital credentialing \
requires trained staff; liability exposure if performed by untrained person). \
HVAC system diagnosis and repair (trade certification expected; insurer and \
employer consequences for uncertified work). Nursing assessment of patient \
condition (nursing standards require RN-level assessment; liability exposure).

- R3 (Government statute): A government statute or regulation specifically \
restricts this act to licensed professionals. Performing this act without the \
required credential is a legal offense — unauthorized practice, regulatory \
infraction, or criminal violation. Key test: does the statute create a SPECIFIC \
PROHIBITION — would a competent but unlicensed person face prosecution for \
performing THIS act? Reserve R3 for acts the statute specifically targets. A \
broad scope-of-practice statute that defines what a profession includes does not \
automatically make every task within that scope R3 — only acts the statute \
specifically restricts.
  Examples: Administering medication (state nurse practice acts specifically \
restrict this). Prescribing controlled substances (DEA + state medical practice \
acts). Cutting hair professionally (cosmetology licensing statutes). Representing \
a client in court (unauthorized practice of law). Operating a commercial vehicle \
(CDL requirement).

- R4 (Moral agency required): The task's legal or institutional force derives from \
a human staking their personal integrity or liberty. Sworn testimony, personal \
attestation under penalty of perjury, sacramental acts. The task is not about \
professional restriction but about human moral participation — the human IS the \
output.
  Examples: Testifying under oath. Signing a declaration under penalty of perjury. \
Consecrating the Eucharist.

STEP 2 — AUGMENTATION BINDING TEST (apply to R2 and R3 only):
After identifying a constraint in Step 1, ask: "Does this regulation or standard \
prevent a licensed professional from using AI tools to ASSIST with this task?"

Regulations and professional standards restrict WHO may perform a task. AI \
assistance does not change WHO is performing it — the licensed professional is \
still performing the task, just with computational support. If the constraint \
restricts WHO but not HOW, and AI assistance is a HOW, then the constraint may \
not fully bind for augmentation purposes.

- If the constraint DOES NOT BIND: Downgrade to the level where friction actually \
disappears. A statutory restriction (R3) that does not bind may still leave \
professional standards (R2) or social norms (R1) in place. Do NOT automatically \
downgrade to R0 — ask what friction remains once the statutory or professional \
barrier is removed for augmentation.
  Examples: A doctor using AI to help interpret diagnostic scans — the statute \
restricts diagnosis (R3), but the doctor is still diagnosing. However, \
professional standards about diagnostic competency still apply → downgrade to \
R2, not R0. A nurse using AI to help synthesize patient data for assessment — \
nursing standards require RN assessment (R2), but the nurse is still assessing. \
Social expectation of a trained clinician remains → downgrade to R1.

- If the constraint PARTIALLY BINDS (AI can assist but specific sub-steps require \
the professional's personal performance): Keep R2 or R3 as classified. The \
constraint limits the workflow even though AI can help with portions.
  Examples: A surgeon using AI for pre-operative planning — the statute \
specifically restricts the act of cutting → keep R3. A pharmacist using AI to \
check drug interactions — dispensing the controlled substance requires the \
pharmacist's personal authorization → keep R3. A cosmetologist using AI to \
recommend styles — the license restricts the physical act of cutting hair → \
keep R3 (the AI assists with style selection, but the licensed act is the \
physical service).

- If the constraint FULLY BINDS: Keep R3 or R4.
  Examples: Sworn testimony (R4) — the human must personally attest. Certain \
forensic certifications require the examiner to have personally performed the \
analysis, not reviewed AI output.

NOTE ON LICENSED PHYSICAL TASKS: When a statute restricts a physical act (cutting \
hair, administering medication, performing surgery, operating a commercial \
vehicle), the constraint typically PARTIALLY or FULLY BINDS even under \
augmentation. The license restricts the physical act itself, not just the \
cognitive judgment behind it. AI can assist with planning, recommendation, or \
monitoring, but the licensed physical act cannot be delegated. Default to keeping \
R3 for statutorily restricted physical acts.

R-AXIS KEY BOUNDARIES:
- R0 vs R1: Would a client/patient/peer object if a non-credentialed person did \
this? If yes AND you can identify an established norm → R1. If no one would \
notice → R0.
- R1 vs R2: Could a practitioner face professional consequences or significant \
liability exposure for lacking credentials? Professional consequences or \
liability → R2. Social discomfort only → R1.
- R2 vs R3: Does a GOVERNMENT statute specifically restrict this act? Government \
law → R3. Professional standard or liability only → R2. The distinction is WHO \
imposes the requirement: the state or the profession.
- R3 vs R4: Does the requirement exist because the professional has specialized \
knowledge (R3), or because the task inherently requires a human moral agent (R4)? \
Testifying under oath → R4. Prescribing controlled substances → R3.
- AFTER boundary classification, apply the AUGMENTATION BINDING TEST to R2/R3.

R-AXIS CRITICAL DISTINCTION — SPECIFIC RESTRICTION vs BROAD SCOPE:
Many licensed professions have scope-of-practice statutes that broadly define what \
the profession encompasses. These broad definitions do NOT make every task within \
the scope a specifically restricted act. R3 requires that the statute creates a \
specific prohibition on unlicensed performance of THIS act — not merely that the \
act falls within a broadly defined professional scope.

SAME OCCUPATION, DIFFERENT R LEVELS:
Registered Nurse (29-1141):
- Filing patient charts → R0 (no restriction on filing; purely administrative)
- Taking vital signs → R1 (no statute, but patients and employers expect trained \
clinical staff)
- Assessing patient condition → R2 (nursing standards require RN-level assessment; \
liability exposure)
- Administering medication → Step 1: R3 (state nurse practice acts). Step 2: \
partially binds — AI can help with dosage calculation, but the nurse must \
personally administer → keep R3.

Lawyer (23-1011):
- Researching case law → R0 (no restriction; anyone can read cases)
- Drafting contracts → R1 (client expects a lawyer, but contract drafting itself \
is not unauthorized practice in most contexts)
- Representing a client in court → Step 1: R3. Step 2: partially binds — AI can \
help prepare but the attorney must personally appear → keep R3.
- Signing a declaration under penalty of perjury → R4 (moral agency; the declarant \
stakes personal liberty)

Elementary School Teacher (25-2021):
- Preparing lesson plans → R0 (no restriction on who creates plans)
- Grading student work → R1 (parents and administrators expect the teacher to \
grade, but no formal standard)
- Leading classroom instruction → R2 (professional teaching standards and district \
policies require credentialed instructors; liability and employment consequences \
for uncredentialed teaching)

Hairdresser/Cosmetologist (39-5012):
- Scheduling client appointments → R0 (purely administrative)
- Recommending hairstyles to clients → R1 (clients expect a trained stylist's \
opinion, but no restriction)
- Cutting hair → Step 1: R3 (cosmetology licensing statutes). Step 2: partially \
binds — AI can recommend the cut, but the physical act of cutting is the licensed \
act → keep R3.
- Applying chemical treatments → Step 1: R3 (cosmetology licensing). Step 2: \
partially binds — the physical application of chemicals is the licensed act → \
keep R3.

R-AXIS VERB-CATEGORY GUIDANCE:
- SUPPORT VERBS (prepare, maintain, record, collect, clean, file, organize, \
schedule, enter data): Default to R0 even in licensed occupations. No statute or \
professional standard specifically restricts these activities.
- CLINICAL/PROFESSIONAL VERBS — split by level of restriction:
  - "diagnose" → Step 1: R3 (formally restricted). Step 2: a doctor using AI to \
help interpret is still diagnosing — statute doesn't bind, but professional \
standards about diagnostic competency remain → R2.
  - "administer medication" → R3, partially binds (physical act cannot be \
delegated) → keep R3.
  - "prescribe" → R3, partially binds (prescriber must personally authorize) → \
keep R3.
  - "perform surgery" → R3, fully binds (the physical act is the restricted act) \
→ keep R3.
  - "assess" / "evaluate" (clinical) → typically R2 (professional standards \
require trained assessment; liability exposure).
  - "take vital signs" → R1 (no statute, but established clinical norm).
- APPROVAL VERBS (certify, sign, stamp, seal, attest, authorize): R3 when statute \
requires a licensed professional's certification. R4 when the act requires \
personal moral commitment (sworn oath, attestation under penalty of perjury).
- TEACHING VERBS (lecture, instruct, grade): Leading instruction → R2 \
(professional standards, district requirements). Grading → R1 (expectation but \
no formal standard). Preparing materials → R0.
- Verb + occupation context matters more than verb alone.

R-AXIS SOC HIERARCHY GUIDANCE:
- Tasks performed by technicians, assistants, and aides (SOC XX-3xxx, 25-9xxx, \
31-xxxx) are typically R0-R2 even when the supervising profession requires R3. \
Many of these roles have professional training requirements (R2) or strong \
occupational norms (R1), but the statute restricts the supervisory professional's \
act, not every task performed under supervision.

COMMON ERROR — OCCUPATION-LEVEL INFLATION:
A licensed occupation does NOT mean every task is regulated. Most tasks within any \
occupation — including medicine, law, and engineering — are R0-R1. Charting, \
scheduling, cleaning, communicating, organizing, and planning are not restricted \
by any statute, even when they happen inside a hospital or courtroom. Classify \
the TASK.

COMMON ERROR — COLLAPSING TO R0:
The augmentation binding test is NOT a license to downgrade everything to R0. When \
a statute or professional standard does not bind for AI augmentation, ask what \
friction REMAINS. Professional standards (R2), occupational norms (R1), and \
liability exposure do not disappear just because AI is assisting. Downgrade to \
the level where friction actually ceases."""


# ---- F-axis v3.1 + verb-spanning patch ----

_F_AXIS = """\
=== FAILURE CONSEQUENCE (F) — What happens if this task is done wrong? ===
F measures the worst-case consequence of incorrect task performance. F measures \
the STAKES — what happens when things go wrong — independent of how likely \
failure is, how cognitively hard the task is (C), what physical capability is \
needed (D), or what regulations exist (R).

F applies to the task ITSELF, regardless of whether a human or AI performs it. A \
medication dosage error is F3 whether the error was made by a tired nurse or a \
malfunctioning algorithm. Rate the consequence of incorrect performance, not the \
identity of the performer.

DECISION TREE — follow in order, stop at the first YES:
  1. Could this error kill or permanently disable MULTIPLE people, or cause \
system-wide cascade? → F4
  2. Could this error kill or permanently disable ONE person, or cause any \
IRREVERSIBLE harm (unrecoverable data, permanent environmental damage, \
bankruptcy)? → F3
  3. Does recovery require professional intervention (medical treatment, legal \
proceedings, significant financial remediation >$100K equivalent)? → F2
  4. Could anyone credibly sue or file a formal complaint? → F1
  5. None of the above → F0

The critical boundary is F2 vs F3: ALL consequences reversible (even if \
expensive) → F2. ANY irreversible component → F3.

- F0 (Negligible / <$1K): Incorrect performance causes minor inconvenience. A \
simple redo fixes it completely. No one is harmed.
  Examples: typo in an internal memo, misclassified library book, slightly \
imprecise garden pruning.

- F1 (Minor / $1K–$100K): Incorrect performance could cause minor financial loss, \
minor property damage, or temporary discomfort. All consequences are fully \
reversible without professional intervention.
  Examples: billing error caught in review, minor cosmetic defect in \
manufacturing, wrong paint color on a wall, bruised produce in sorting.

- F2 (Serious / $100K–$10M): Incorrect performance could cause significant \
financial loss, recoverable injury, or substantial property damage. Recovery \
requires professional intervention but ALL consequences are ultimately \
REVERSIBLE — no permanent harm, no fatalities.
  Examples: structural calculation error caught before construction, equipment \
failure shutting down a production line, medication error causing a treatable \
adverse reaction, data breach of non-critical records.

- F3 (Severe / irreversible / >$10M or single fatality): Incorrect performance \
could cause ANY IRREVERSIBLE harm: a single fatality, permanent disability, \
unrecoverable data or environmental damage, or bankruptcy-scale financial loss. \
The key test: can the harm be fully undone? If not → F3.
  Examples: missed cancer diagnosis, bridge structural failure, fiduciary \
malpractice losing a client's life savings, medication error causing \
anaphylaxis or organ damage.

- F4 (Catastrophic / systemic / multiple fatalities): Incorrect performance could \
cause MULTIPLE fatalities or system-wide irreversible harm. The failure mode \
affects many people or cascades through an entire system.
  Examples: "all clear" confirmation at a demolition site when area is not \
clear, air traffic control sequencing error, nuclear plant safety system \
failure, dam integrity assessment error.

F-AXIS BOUNDARY TESTS (binary — answer YES or NO):
- F0 vs F1: Could anyone credibly sue or file a complaint over this error? \
NO → F0. YES → F1+.
- F1 vs F2: Does recovery require professional intervention (medical, legal, \
or >$100K remediation)? NO → F1. YES → F2+.
- F2 vs F3: Is ANY consequence IRREVERSIBLE (death, permanent disability, \
unrecoverable loss)? NO → F2. YES → F3+. This is the sharpest boundary — \
reversible-but-expensive is F2, irreversible-for-anyone is F3.
- F3 vs F4: Could this error harm MULTIPLE people or cascade through a system? \
NO (contained to one person/entity) → F3. YES → F4.

F-AXIS EDGE-CASE INDICATORS:
Push UP if: (a) Irreversibility — no review stage or checkpoint exists between \
task performance and consequence realization. A medication error administered \
directly is higher-F than one reviewed by a pharmacist first. \
(b) Cascading failure — an error in THIS task propagates to other systems in \
ways that amplify the consequence beyond the immediate context.
Push DOWN if: (c) Redundancy/review — the task output goes through independent \
verification before affecting anything. The task's F reflects consequence \
GIVEN the existing review structure. \
(d) Cheap reversal — the error can be detected and corrected at low cost. A \
software bug with test coverage and rollback is lower-F than the same bug in \
an embedded system with no update path.

BUMP-UP MODIFIER — COMPOUNDING ERROR:
Multi-step task execution where intermediate errors are NOT independently \
verified before the next step begins, such that per-step error probabilities \
multiply. A task with N sequential unverified steps has overall failure risk \
that grows multiplicatively — 100 steps at 99% reliability each yields only \
37% overall success.
  Push UP the F-level when: the task involves a chain of sequential steps where \
(a) each step depends on the output of the previous step, (b) there is no \
independent verification checkpoint between steps, and (c) the consequence of \
accumulated errors is worse than the consequence of any single-step error.
  Examples: multi-drug titration without intermediate labs (each adjustment \
compounds on the previous one), long-horizon financial planning where each \
decision constrains the next, multi-step chemical synthesis where purification \
occurs only at the end.
  Note: This modifier is especially relevant for AGENTIC AI workflows where \
removing human-in-the-loop review checkpoints increases effective F even when \
per-step F is low.

D-F STRUCTURAL CORRELATION — NOT A CLASSIFICATION ERROR:
Tasks that are D4 (dynamic, real-time physical manipulation) also tend to be \
high-F, because the same physics that creates dynamic difficulty also creates \
physical danger. This is a real correlation, not a rating mistake. Do NOT \
artificially lower F to make it "more independent" of D. Rate F based on \
actual consequences.
  The cases where D and F DIVERGE are analytically important:
  - D1/F4: Demolition all-clear (trivial physical task, catastrophic consequence)
  - D4/F1: Sheep shearing (dynamic manipulation of an uncooperative animal, \
but a nick is minor harm)
  These divergence cases are where F carries unique predictive signal beyond D.

F-AXIS DISAMBIGUATION:
- F measures CONSEQUENCE, not PROBABILITY. A task that rarely fails but is \
catastrophic when it does is still F4. A task with frequent trivial errors is F0.
- F is about THIS TASK's failure, not the occupation's overall risk. A surgeon's \
"dictate operative notes" is F0. The same surgeon's "ligate the hepatic artery" \
is F3.
- F is INDEPENDENT of R. Demolition all-clear is F4/R0 (catastrophic, no license). \
Priestly consecration is F0/R4 (no harm if wrong, absolute ontological barrier).

COMMON ERROR — VERBS THAT SPAN THE FULL RANGE:
"Monitor" spans the full F range: F0 (monitor inventory levels — miscount causes \
minor reorder), F2 (monitor a patient's vitals post-surgery — missed deterioration \
causes serious harm), F4 (monitor reactor containment pressure — missed reading \
risks catastrophe). Do not assign F from the verb.

COMMON ERROR — OCCUPATION-LEVEL RISK INFLATION:
A firefighter filing a routine incident report is F0, even though firefighting \
is dangerous. The TASK of writing the report has no failure consequence. \
Classify the task, not the occupation."""


# ---------------------------------------------------------------------------
# Ground-truth / calibration examples
# ---------------------------------------------------------------------------

_GROUND_TRUTH_CDRF = """\
GROUND TRUTH EXAMPLES (for calibration — do NOT include these in your output):
- Garbage collector (53-7081) emptying residential bins → C0, D3, R0, F0 \
(self-evident action; unstructured outdoor environment; no regulatory barrier; \
spilled trash is negligible consequence)
- Technical writer (27-3042) writing user documentation → C2, D0, R0, F1 \
(contextual judgment to structure information; purely digital; unregulated; \
bad documentation causes minor rework)
- Mathematician (15-2021) proving a new theorem → C4, D0, R0, F0 \
(discovery of new knowledge; purely digital; unregulated; wrong proof harms \
no one — it just gets rejected)
- Demolition safety officer (47-4099) giving verbal "all clear" over radio → \
C0, D0, R0, F4 (binary look-and-confirm; voice over radio; no specific \
licensure; failure = people die in the blast)
- Priest (21-2011) consecrating the Eucharist → C0, D0, R4, F0 \
(words are pre-written; no physical manipulation; absolute ontological barrier; \
incorrect rite has no safety consequence)
- Structural engineer (17-2051) certifying bridge load calculations → C3, D0, \
R3, F3 (expert synthesis; purely digital; PE stamp required; single point of \
failure for fatal structural collapse)
- Air traffic controller (53-2021) sequencing landing approaches → C3, D0, R3, \
F4 (expert real-time judgment; digital radar interface; FAA certified; error \
= multiple fatalities)"""


_GROUND_TRUTH_CDR = """\
=== GROUND TRUTH EXAMPLES (for calibration — do NOT include these in your output) ===
- Garbage collector (53-7081) emptying residential bins → C0, D3, R0 \
(self-evident action; unstructured outdoor environment; no regulatory barrier)
- Mathematician (15-2021) proving a new theorem → C4, D0, R0 \
(discovery of new knowledge; purely digital; unregulated)
- Demolition safety officer (47-4099) giving verbal "all clear" after visual \
site inspection → C0, D1, R0 (binary look-and-confirm; requires physical \
presence for observation; no specific licensure)
- Priest (21-2011) consecrating the Eucharist → C0, D0, R4 \
(words are pre-written; no physical manipulation; absolute ontological barrier)
- Registered nurse (29-1141) administering IV medication → C1, D3, R3 \
(follows dosage protocol; variable patient anatomy, veins that roll; nurse \
practice act restricts medication administration)
- Structural engineer (17-2051) certifying bridge load calculations → C3, D0, \
R3 (expert synthesis across loading and material factors; purely digital; PE \
stamp required by statute — partially binds, engineer must personally certify)
- Cosmetologist (39-5012) cutting and styling hair → C2, D3, R3 \
(contextual judgment on style for client features; unstructured manipulation \
of variable hair; cosmetology license restricts the physical act)"""


# ---------------------------------------------------------------------------
# Response format block
# ---------------------------------------------------------------------------

_RESPONSE_FORMAT_MERGED = """\
RESPONSE FORMAT:
Respond with a pipe-delimited table using || as the delimiter.
Use these exact columns: \
task_id||reasoning||capability||deployment||regulatory||failure||confidence

IMPORTANT: Think about the task before assigning labels. Write your reasoning \
FIRST (up to 3 sentences covering all axes), THEN assign the classification labels.

Rules:
- One row per task, in the SAME ORDER as the input
- task_id must match the input task_id exactly
- reasoning: up to 3 sentences explaining your classification across all axes
- capability must be exactly C0, C1, C2, C3, or C4
- deployment must be exactly D0, D1, D2, D3, or D4
- regulatory must be exactly R0, R1, R2, R3, or R4
- failure must be exactly F0, F1, F2, F3, or F4
- confidence must be exactly LOW, MEDIUM, or HIGH
- Begin your response with the header row immediately

Example output:
task_id||reasoning||capability||deployment||regulatory||failure||confidence
T001||Requires contextual judgment to architect solutions; purely digital \
output with no regulatory barriers; bugs cause rework, not physical harm.\
||C2||D0||R0||F1||HIGH
T002||Expert synthesis across loading and material factors; purely digital \
calculations but PE stamp required by statute; bridge failure could be fatal.\
||C3||D0||R3||F3||HIGH"""


_RESPONSE_FORMAT_PER_AXIS = """\
RESPONSE FORMAT:
Respond with a pipe-delimited table using || as the delimiter.
Use these exact columns: \
task_id||c_reasoning||d_reasoning||r_reasoning||f_reasoning\
||capability||deployment||regulatory||failure||confidence

IMPORTANT: Write your reasoning for EACH axis FIRST, THEN assign the \
classification labels. Think through each axis independently before committing.

Rules:
- One row per task, in the SAME ORDER as the input
- task_id must match the input task_id exactly
- c_reasoning: 1 sentence on cognitive complexity
- d_reasoning: 1 sentence on physical/deployment demands
- r_reasoning: 1 sentence on regulatory barriers
- f_reasoning: 1 sentence on failure consequences
- capability must be exactly C0, C1, C2, C3, or C4
- deployment must be exactly D0, D1, D2, D3, or D4
- regulatory must be exactly R0, R1, R2, R3, or R4
- failure must be exactly F0, F1, F2, F3, or F4
- confidence must be exactly LOW, MEDIUM, or HIGH
- Begin your response with the header row immediately

Example output:
task_id||c_reasoning||d_reasoning||r_reasoning||f_reasoning\
||capability||deployment||regulatory||failure||confidence
T001||Requires contextual judgment to architect solutions\
||Purely digital output\
||No regulatory barriers\
||Bug in production causes rework, not physical harm\
||C2||D0||R0||F1||HIGH
T002||Expert synthesis across loading and material factors\
||Purely digital calculations\
||PE stamp required by statute\
||Bridge failure could be fatal\
||C3||D0||R3||F3||HIGH"""


_RESPONSE_FORMAT_MERGED_CDR = """\
RESPONSE FORMAT:
Respond with a pipe-delimited table using || as the delimiter.
Use these exact columns: \
task_id||reasoning||capability||deployment||regulatory||confidence

IMPORTANT: Think about the task before assigning labels. Write your reasoning \
FIRST (up to 3 sentences covering all axes), THEN assign the classification labels.

Rules:
- One row per task, in the SAME ORDER as the input
- task_id must match the input task_id exactly
- reasoning: up to 3 sentences explaining your classification across all axes
- capability must be exactly C0, C1, C2, C3, or C4
- deployment must be exactly D0, D1, D2, D3, or D4
- regulatory must be exactly R0, R1, R2, R3, or R4
- confidence must be exactly LOW, MEDIUM, or HIGH
- Begin your response with the header row immediately

Example output:
task_id||reasoning||capability||deployment||regulatory||confidence
T001||Requires contextual judgment to architect solutions; purely digital \
output with no regulatory barriers.\
||C2||D0||R0||HIGH
T002||Expert synthesis across loading and material factors; purely digital \
calculations but PE stamp required by statute.\
||C3||D0||R3||HIGH"""


_RESPONSE_FORMAT_PER_AXIS_CDR = """\
=== RESPONSE FORMAT ===
Respond with a pipe-delimited table using || as the delimiter.
Use these exact columns: \
task_id||c_reasoning||d_reasoning||r_reasoning\
||capability||deployment||regulatory||confidence

IMPORTANT: Write your reasoning for EACH axis FIRST, THEN assign the \
classification labels. Think through each axis independently before committing.

Rules:
- One row per task, in the SAME ORDER as the input
- task_id must match the input task_id exactly
- c_reasoning: 1 sentence on cognitive complexity
- d_reasoning: 1 sentence on physical/deployment demands
- r_reasoning: 1 sentence on regulatory barriers
- capability must be exactly C0, C1, C2, C3, or C4
- deployment must be exactly D0, D1, D2, D3, or D4
- regulatory must be exactly R0, R1, R2, R3, or R4
- confidence: Report how certain you are about your classification, considering \
ALL axes together:
  - HIGH: All three axes were clear — you did not seriously consider an adjacent \
level for any axis.
  - MEDIUM: One axis was borderline — you considered an adjacent level before \
deciding.
  - LOW: Two or more axes were borderline, OR you strongly considered a \
non-adjacent level (e.g., C1 vs C3) for any axis.
  Note: confidence reflects YOUR uncertainty, not task difficulty. A hard task can \
still be HIGH if the classification criteria clearly apply.
- Begin your response with the header row immediately

Example output:
task_id||c_reasoning||d_reasoning||r_reasoning\
||capability||deployment||regulatory||confidence
T001||Requires contextual judgment to architect solutions\
||Purely digital output\
||No regulatory barriers\
||C2||D0||R0||HIGH
T002||Expert synthesis across loading and material factors\
||Purely digital calculations\
||PE stamp required by statute\
||C3||D0||R3||HIGH
T003||Follows a standard protocol but requires trained judgment on patient tolerance\
||Variable patient anatomy, veins that roll\
||Nurse practice act restricts medication administration\
||C1||D3||R3||MEDIUM"""


_RESPONSE_FORMAT_AXIS_DISPUTE = """\
RESPONSE FORMAT:
Respond with a pipe-delimited table using || as the delimiter.
Use these exact columns: task_id||axis||reasoning||rating||confidence

One row per disputed axis per task. Only include axes you were asked to re-rate.

Rules:
- task_id must match the input task_id exactly
- axis must be exactly C, D, R, or F
- reasoning: 1 sentence explaining your classification for this axis
- rating must match the axis (C0-C4 for C, D0-D4 for D, R0-R4 for R, F0-F4 for F)
- confidence must be exactly LOW, MEDIUM, or HIGH
- Begin your response with the header row immediately

Example output:
task_id||axis||reasoning||rating||confidence
1839||F||Inaccurate records can cascade into treatment errors causing patient harm.||F2||HIGH
1840-1||D||Physical presence required for direct patient observation at bedside.||D1||MEDIUM
1840-1||R||Nursing norms expect human monitoring but no statute prevents AI assistance.||R1||MEDIUM"""


def get_response_format(reasoning_format: str = "merged", axes: list[str] | None = None) -> str:
    """Return the response format block for the given reasoning format and axes.

    Args:
        reasoning_format: "merged", "per_axis", or "axis_dispute".
        axes: List of axis labels. If None, defaults to CDRF.

    Raises:
        ValueError: If reasoning_format is not recognized.
    """
    if axes is None:
        axes = ["C", "D", "R", "F"]

    is_cdr = frozenset(axes) == frozenset(["C", "D", "R"])

    if reasoning_format == "merged":
        return _RESPONSE_FORMAT_MERGED_CDR if is_cdr else _RESPONSE_FORMAT_MERGED
    elif reasoning_format == "per_axis":
        return _RESPONSE_FORMAT_PER_AXIS_CDR if is_cdr else _RESPONSE_FORMAT_PER_AXIS
    elif reasoning_format == "axis_dispute":
        return _RESPONSE_FORMAT_AXIS_DISPUTE
    else:
        raise ValueError(f"reasoning_format must be 'merged', 'per_axis', or 'axis_dispute', got '{reasoning_format}'")


# ---------------------------------------------------------------------------
# Compose system prompts for each experiment configuration
# ---------------------------------------------------------------------------


def _build_system_prompt(
    axes: list[str],
    threshold: int = 50,
    reasoning_format: str = "merged",
    r_version: str = "v4",
    c_version: str = "v1",
) -> str:
    """Compose a system prompt from selected axis definitions.

    Args:
        axes: List of axis letters in presentation order, e.g. ["C","D","R","F"].
        threshold: Time-reduction percentage for economic framing.
        reasoning_format: "merged" or "per_axis".
        r_version: "v4" (50% threshold), "v5" (regulatory assignment), "v6" (pure regulatory taxonomy), "v7" (v6 + soft augmentation anchor), or "v8" (broadened R1/R2 + graduated downgrade).
        c_version: "v1" (original) or "v2" (manual test as unified framework).

    Returns:
        Complete system prompt string.
    """
    r_axis_versions = {
        "v4": _R_AXIS,
        "v5": _R_AXIS_V5,
        "v6": _R_AXIS_V6,
        "v7": _R_AXIS_V7,
        "v8": _R_AXIS_V8,
    }
    if r_version not in r_axis_versions:
        raise ValueError(f"r_version must be one of {list(r_axis_versions)}, got '{r_version}'")

    c_axis_versions = {
        "v1": _C_AXIS,
        "v2": _C_AXIS_V2,
    }
    if c_version not in c_axis_versions:
        raise ValueError(f"c_version must be one of {list(c_axis_versions)}, got '{c_version}'")

    axis_map = {
        "C": c_axis_versions[c_version],
        "D": _D_AXIS,
        "R": r_axis_versions[r_version],
        "F": _F_AXIS,
    }
    gt_map = {
        frozenset(["C", "D", "R", "F"]): _GROUND_TRUTH_CDRF,
        frozenset(["C", "D", "R"]): _GROUND_TRUTH_CDR,
    }

    axis_key = frozenset(axes)
    if axis_key not in gt_map:
        raise ValueError(
            f"No ground-truth examples defined for axis set {axes}. Supported: {[list(k) for k in gt_map]}"
        )

    header = _HEADER.format(n_axes=len(axes), threshold=threshold)
    body_parts = [axis_map[a] for a in axes]
    ground_truth = gt_map[axis_key]
    response_fmt = get_response_format(reasoning_format, axes=axes)

    prompt = "\n\n".join([header] + body_parts + [ground_truth, response_fmt])

    if threshold != 50:
        prompt = prompt.replace("50%", f"{threshold}%")

    return prompt


# ---------------------------------------------------------------------------
# Public API — system prompt constructors
# ---------------------------------------------------------------------------


def format_cdrf_system_prompt(*, threshold: int = 50, reasoning_format: str = "merged", r_version: str = "v4", c_version: str = "v1") -> str:
    """System prompt for CDRF classification.

    Args:
        threshold: Time-reduction percentage (default 50).
        reasoning_format: "merged" (single reasoning column) or
            "per_axis" (separate c/d/r/f reasoning columns).
        r_version: "v4" | "v5" | "v6" | "v7" | "v8". See _build_system_prompt for details.
        c_version: "v1" (original) or "v2" (manual test as unified framework).
    """
    return _build_system_prompt(
        ["C", "D", "R", "F"],
        threshold=threshold,
        reasoning_format=reasoning_format,
        r_version=r_version,
        c_version=c_version,
    )


def format_cdr_system_prompt(*, threshold: int = 50, reasoning_format: str = "merged", r_version: str = "v4", c_version: str = "v1") -> str:
    """System prompt for CDR classification (no F-axis).

    Args:
        threshold: Time-reduction percentage (default 50).
        reasoning_format: "merged" (single reasoning column) or
            "per_axis" (separate c/d/r reasoning columns).
        r_version: "v4" | "v5" | "v6" | "v7" | "v8". See _build_system_prompt for details.
        c_version: "v1" (original) or "v2" (manual test as unified framework).
    """
    return _build_system_prompt(
        ["C", "D", "R"],
        threshold=threshold,
        reasoning_format=reasoning_format,
        r_version=r_version,
        c_version=c_version,
    )


# ---------------------------------------------------------------------------
# User prompt (shared across experiments — same as CDR v2 architecture)
# ---------------------------------------------------------------------------


def expand_task_dwa_rows(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expand tasks into one row per task×DWA combination.

    Each task with N DWAs becomes N rows with suffixed IDs:
      task_id "1855" with 2 DWAs → "1855-1" and "1855-2"
      task_id "638" with 1 DWA → "638" (no suffix for single-DWA tasks)
      task_id "999" with 0 DWAs → "999" (kept as-is, no DWA column)

    Returns list of dicts with keys: row_id, task_description, dwa_title.
    """
    rows = []
    for task in tasks:
        task_id = task["task_id"]
        description = task["task_description"]
        dwa_labels = task.get("dwa_labels", [])

        if len(dwa_labels) <= 1:
            rows.append(
                {
                    "row_id": str(task_id),
                    "task_description": description,
                    "dwa_title": dwa_labels[0] if dwa_labels else "",
                }
            )
        else:
            for j, dwa in enumerate(dwa_labels, start=1):
                rows.append(
                    {
                        "row_id": f"{task_id}-{j}",
                        "task_description": description,
                        "dwa_title": dwa,
                    }
                )
    return rows


def _format_task_table(rows: list[dict[str, Any]]) -> str:
    """Format expanded task×DWA rows as a pipe-delimited input table.

    Produces a header + one line per row, using the task_id as the
    only identifier (no sequential numbering, no occupation title).
    """
    lines = ["task_id | dwa_title | task_description"]
    for row in rows:
        tid = row["row_id"]
        dwa = row["dwa_title"]
        desc = row["task_description"]
        lines.append(f"{tid} | {dwa} | {desc}")
    return "\n".join(lines)


def format_user_prompt(
    tasks: list[dict[str, Any]],
    *,
    axes: list[str] | None = None,
    profile: dict[str, Any] | None = None,
    description: str | None = None,
    abilities: list[tuple[str, float]] | None = None,
    work_context: list[tuple[str, float]] | None = None,
) -> str:
    """Per-occupation user prompt with profile header and task list.

    Args:
        tasks: List of task dicts for a single occupation.
        axes: Axis letters for column header hint, e.g. ["C","D","R","F"].
            If None, defaults to ["C","D","R","F"].
        profile: Occupation profile dict (from load_occupation_profiles).
        description: O*NET occupation description string.
        abilities: Top abilities as (name, importance) tuples, sorted descending.
        work_context: Top work context items as (name, value) tuples, sorted descending.
    """
    if axes is None:
        axes = ["C", "D", "R", "F"]

    parts = []

    if profile:
        # Import here to avoid circular dependency
        from .profiles import format_occupation_profile

        parts.append(format_occupation_profile(profile, description))
        parts.append("")

    if abilities:
        parts.append("Key Abilities (O*NET, Importance scale 1-5):")
        for name, val in abilities:
            parts.append(f"  - {name} ({val:.1f})")
        parts.append("")

    if work_context:
        parts.append("Work Context (O*NET, frequency/extent scale 1-5):")
        for name, val in work_context:
            parts.append(f"  - {name} ({val:.1f})")
        parts.append("")

    # Expand tasks into one row per task×DWA pair
    rows = expand_task_dwa_rows(tasks)

    # Use first task's title for the occupation name reminder
    occ_title = tasks[0]["occupation_title"] if tasks else "this occupation"
    parts.append(
        f'Classify each task on {", ".join(axes)} axes for "{occ_title}". '
        f"Read through all {len(rows)} tasks before responding. "
        f"You'll see a header row first; each column contains the "
        f"information described in the header."
    )
    parts.append("")
    parts.append(_format_task_table(rows))
    parts.append("")
    axis_str = ", ".join(axes)
    parts.append(
        f"Now rate all {len(rows)} tasks above on each of the {axis_str} axes "
        f"described earlier. Produce exactly one output row per input row. "
        f"Remember to think about each task before assigning your answer."
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Convenience wrapper matching the existing pipeline interface
# ---------------------------------------------------------------------------


def format_cdrf_prompt_pair(
    tasks: list[dict[str, Any]],
    *,
    profile: dict[str, Any] | None = None,
    description: str | None = None,
    abilities: list[tuple[str, float]] | None = None,
    work_context: list[tuple[str, float]] | None = None,
    threshold: int = 50,
    reasoning_format: str = "merged",
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for CDRF classification.

    Usage:
        system, user = format_cdrf_prompt_pair(tasks, profile=prof)
        response = call_llm(system=system, user=user)
    """
    return (
        format_cdrf_system_prompt(threshold=threshold, reasoning_format=reasoning_format),
        format_user_prompt(
            tasks,
            axes=["C", "D", "R", "F"],
            profile=profile,
            description=description,
            abilities=abilities,
            work_context=work_context,
        ),
    )
