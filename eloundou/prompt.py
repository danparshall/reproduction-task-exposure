"""Eloundou rubric prompt construction and response parsing.

Reconstructs the Eloundou et al. (2023) Appendix A.1 exposure rubric
for reproduction with current models. Two rubric variants:
  - eloundou_2023: faithful to the published rubric (generic LLM, text-only, 2000-word context)
  - frontier_2026: updated model definition for multimodal frontier models
"""
import re


# ── Model definition variants ────────────────────────────────────────────

ELOUNDOU_MODEL_DEFINITION_TEMPLATE = """\
Consider the most powerful large language model (LLM) as of {release_date}. This model can complete many \
tasks that can be formulated as having text input and text output where the context for the input can be \
captured in 2000 words. The model also cannot draw up-to-date facts (those from <1 year ago) unless they \
are captured in the input.

You are classifying tasks as of the LLM's release date of {release_date}. Do not assume access to \
web browsing, external tools, or any capabilities beyond text input and text output."""

FRONTIER_MODEL_DEFINITION_TEMPLATE = """\
Consider the most powerful large language model (LLM) available as of {release_date}. This model can \
process text, images, audio, and video inputs, and produce text and image outputs. Its context window \
exceeds 1 million words. It has broad and generally current world knowledge, though it may not \
know events from the last few months.

You are classifying tasks as of the LLM's release date of {release_date}. Do not assume access to \
web browsing or external tools beyond the model's built-in capabilities."""


# ── Rubric body (verbatim from Appendix A.1, minus the model definition) ─

RUBRIC_BODY = """\
Assume you are a worker with an average level of expertise in your role trying to complete the given task. \
You have access to the LLM as well as any other existing software or computer hardware tools mentioned \
in the task. You also have access to any commonly available technical tools accessible via a laptop (e.g. a \
microphone, speakers, etc.). You do not have access to any other physical tools or materials.

Please label the given task according to the taxonomy below.

## E0 - No exposure

Label tasks E0 if direct access to the LLM through a chat interface \
cannot reduce the time it takes to complete this task with equivalent quality by half or more.

If a task requires a high degree of human interaction (for example, in person demonstrations) then it \
should be classified as E0.

## E1 - Direct exposure

Label tasks E1 if direct access to the LLM through a chat interface \
alone can reduce the time it takes to complete the task with equivalent quality by at least half. This includes \
tasks that can be reduced to:
- Writing and transforming text and code according to complex instructions
- Providing edits to existing text or code following specifications
- Writing code that can help perform a task that used to be done by hand
- Translating text between languages
- Summarizing medium-length documents
- Providing feedback on documents
- Answering questions about a document
- Generating questions a user might want to ask about a document

## E2 - Exposure by LLM-powered applications

Label tasks E2 if having access to the LLM alone may not reduce the time it takes to complete the task by \
at least half, but it is easy to imagine additional software that could be developed on top of the LLM that \
would reduce the time it takes to complete the task by half. This software may include capabilities such \
as:
- Summarizing documents longer than 2000 words and answering questions about those documents
- Retrieving up-to-date facts from the Internet and using those facts in combination with the LLM capabilities
- Searching over an organization's existing knowledge, data, or documents and retrieving information

Examples of software built on top of the LLM that may help complete worker activities include:
- Software built for a home goods company that quickly processes and summarizes their up-to-date internal data in customized ways to inform product or marketing decisions
- Software that is able to suggest live responses for customer service agents speaking to customers in their company's customer service interface
- Software built for legal purposes that can quickly aggregate and summarize all previous cases in a particular legal area and write legal research memos tailored to the law firm's needs
- Software specifically designed for teachers that allows them to input a grading rubric and upload the text files of all student essays and have the software output a letter grade for each essay
- Software that retrieves up-to-date facts from the internet and uses the capabilities of the LLM to output news summaries in different languages

## E3 - Exposure given image capabilities

Suppose you had access to both the LLM and a system that could view, caption, and create images. This \
system cannot take video media as inputs. This system cannot accurately retrieve very detailed information \
from image inputs, such as measurements of dimensions within an image. Label tasks as E3 if there is \
a significant reduction in the time it takes to complete the task given access to a LLM and these image \
capabilities:
- Reading text from PDFs
- Scanning images
- Creating or editing digital images according to instructions

## Annotation examples

Occupation: Inspectors, Testers, Sorters, Samplers, and Weighers
Task: Adjust, clean, or repair products or processing equipment to correct defects found during inspections.
Label: E0
Explanation: The model does not have access to any kind of physicality, and more than half of the task (adjusting, cleaning and repairing equipment) described requires hands or other embodiment.

Occupation: Computer and Information Research Scientists
Task: Apply theoretical expertise and innovation to create or apply new technology, such as adapting principles for applying computers to new uses.
Label: E1
Explanation: The model can learn theoretical expertise during training as part of its general knowledge base, and the principles to adapt can be captured in the text input to the model.

Activity: Schedule dining reservations.
Label: E2
Explanation: Automation technology already exists for this (e.g. Resy) and it's unclear what an LLM offers on top of using that technology (no-diff). That said, you could build something that allows you to ask the LLM to make a reservation on Resy for you.

Activity: Negotiate purchases or contracts.
Label: E2
Explanation: You could have each party transcribe their point of view and then feed this to an LLM to resolve any disputes. That said, many people would need to buy into using new technological tools to accomplish this.

Occupation: Allergists and Immunologists
Task: Prescribe medication such as antihistamines, antibiotics, and nasal, oral, topical, or inhaled glucocorticosteroids.
Label: E2
Explanation: The model can provide guesses for different diagnoses and write prescriptions and case notes. However, it still requires a human in the loop using their judgment and knowledge to make the final decision."""


# ── Rubric assembly ──────────────────────────────────────────────────────

RUBRIC_VARIANT_TEMPLATES = {
    "eloundou_2023": ELOUNDOU_MODEL_DEFINITION_TEMPLATE,
    "frontier_2026": FRONTIER_MODEL_DEFINITION_TEMPLATE,
}


def build_system_prompt(rubric: str = "eloundou_2023", release_date: str = "March 2023") -> str:
    """Return the full system prompt for a given rubric variant.

    Args:
        rubric: One of "eloundou_2023" or "frontier_2026".
        release_date: Human-readable date string for anchoring the model definition.

    Returns:
        Complete system prompt string.

    Raises:
        ValueError: If rubric name is not recognized.
    """
    if rubric not in RUBRIC_VARIANT_TEMPLATES:
        raise ValueError(
            f"Unknown rubric: {rubric!r}. Choose from: {list(RUBRIC_VARIANT_TEMPLATES)}"
        )
    model_def = RUBRIC_VARIANT_TEMPLATES[rubric].format(release_date=release_date)
    return model_def + "\n\n" + RUBRIC_BODY


def build_user_prompt(occupation_title: str, tasks: list[dict]) -> str:
    """Format the per-occupation user prompt.

    Args:
        occupation_title: O*NET occupation title.
        tasks: List of dicts with "task_id" and "task_description" keys.

    Returns:
        Formatted user prompt string.

    Raises:
        ValueError: If tasks list is empty.
    """
    if not tasks:
        raise ValueError("Tasks list must not be empty")

    lines = [f"Occupation: {occupation_title}", ""]
    lines.append(
        "For each task below, provide your label (E0, E1, E2, or E3) and a brief explanation."
    )
    lines.append(
        "Use the format: Task ID: <id> | <label> | <explanation>"
    )
    lines.append("")
    for task in tasks:
        lines.append(f"Task ID: {task['task_id']} | {task['task_description']}")

    return "\n".join(lines)


def build_user_prompt_single_task(occupation_title: str, task_id: int, task_description: str) -> str:
    """Format a per-task user prompt (Eloundou's exact method).

    One task per API call, matching Eloundou's methodology.

    Args:
        occupation_title: O*NET occupation title.
        task_id: The task ID (included for parseability).
        task_description: The task description text.

    Returns:
        Formatted user prompt string.
    """
    return (
        f"Occupation: {occupation_title}\n"
        f"Task ID: {task_id}\n"
        f"Task: {task_description}\n\n"
        f"Label (E0/E1/E2/E3) and explain briefly.\n"
        f"Use the format: Task ID: {task_id} | <label> | <explanation>"
    )


# ── Response parsing ─────────────────────────────────────────────────────

# Patterns to match task_id and E-label in various formats
_LABEL_PATTERN = re.compile(
    r"(?:Task\s*ID:?\s*)?(\d+)\s*[\|:\-–—]\s*(E[0-3])\b\s*[\|:\-–—]?\s*(.*)",
    re.IGNORECASE,
)

_TABLE_ROW_PATTERN = re.compile(
    r"\|\s*(\d+)\s*\|\s*(E[0-3])\s*\|\s*(.*?)\s*\|?$",
    re.IGNORECASE,
)


def parse_response(response_text: str, expected_task_ids: list[int]) -> list[dict]:
    """Extract task_id → label mappings from a model response.

    Handles pipe-delimited, colon-delimited, and markdown table formats.

    Args:
        response_text: Raw model response text.
        expected_task_ids: List of task IDs we expect to find.

    Returns:
        List of dicts with "task_id" (int), "label" (str), "explanation" (str).
        Only includes successfully parsed tasks.
    """
    expected_set = set(expected_task_ids)
    results = {}

    for line in response_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        # Try table format first
        m = _TABLE_ROW_PATTERN.match(line)
        if not m:
            m = _LABEL_PATTERN.match(line)
        if not m:
            continue

        task_id = int(m.group(1))
        label = m.group(2).upper()
        explanation = m.group(3).strip().rstrip("|").strip()

        if task_id in expected_set and task_id not in results:
            results[task_id] = {
                "task_id": task_id,
                "label": label,
                "explanation": explanation,
            }

    return list(results.values())
