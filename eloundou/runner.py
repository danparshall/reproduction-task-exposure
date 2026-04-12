"""Eloundou replication runner — provider-agnostic execution.

Runs the Eloundou Appendix A.1 rubric on O*NET tasks, one API call per occupation
(per-occ mode) or one API call per task (per-task mode). Supports OpenAI, Anthropic,
and Google models. Checkpoints per-SOC/task for resume. Async with configurable
concurrency for rate-limit-aware parallel execution.

Usage:
    python -m eloundou.runner --model gpt-4-0613 --soc-set pilot --seed 137
    python -m eloundou.runner --model gpt-5.2 --soc-set stratified_50 --per-task
    python -m eloundou.runner --model gpt-4-0613 --soc-set all --concurrency 50

Rate limits (OpenAI GPT-4-0613):
    Tier 1 (10k TPM):   --concurrency 1-3   (~3 calls/min)
    Tier 2 (40k TPM):   --concurrency 5-10  (~13 calls/min)
    Tier 3 (300k TPM):  --concurrency 10-50 (~100 calls/min)
    Each call uses ~3,000 tokens (2,100 in + 960 out).
"""
import argparse
import asyncio
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from eloundou.prompt import (
    build_system_prompt,
    build_user_prompt,
    build_user_prompt_single_task,
    parse_response,
)

PACKAGE_ROOT = Path(__file__).parent
DATA_DIR = PACKAGE_ROOT / "data"
RESULTS_DIR = PACKAGE_ROOT / "results"
TASKS_CSV = DATA_DIR / "onet_tasks_18k.csv"
STRAT50_SAMPLE = DATA_DIR / "stratified_50_sample.json"

SOC_SETS = {
    "pilot": [
        "39-5012.00",  # Hairdressers, Hairstylists, and Cosmetologists
        "49-9021.00",  # HVAC Mechanics and Installers
        "29-1141.00",  # Registered Nurses
    ],
    "expanded": [
        "39-5012.00",  # Hairdressers, Hairstylists, and Cosmetologists
        "49-9021.00",  # HVAC Mechanics and Installers
        "29-1141.00",  # Registered Nurses
        "11-1011.00",  # Chief Executives
        "13-2011.00",  # Accountants and Auditors
        "15-1252.00",  # Software Developers
        "25-2021.00",  # Elementary School Teachers
        "35-2014.00",  # Cooks, Restaurant
        "43-4051.00",  # Customer Service Representatives
        "47-2061.00",  # Construction Laborers
        "51-4121.00",  # Welders, Cutters, Solderers, and Brazers
        "53-3032.00",  # Heavy and Tractor-Trailer Truck Drivers
    ],
    "stratified_50": [
        "11-3051.00",  # Industrial Production Managers
        "11-9021.00",  # Construction Managers
        "11-9161.00",  # Emergency Management Directors
        "13-1071.00",  # Human Resources Specialists
        "13-1082.00",  # Project Management Specialists
        "13-1151.00",  # Training and Development Specialists
        "15-1299.04",  # Penetration Testers
        "15-1299.09",  # Information Technology Project Managers
        "17-2051.02",  # Water/Wastewater Engineers
        "17-3013.00",  # Mechanical Drafters
        "17-3026.00",  # Industrial Engineering Technologists and Technicians
        "19-1029.02",  # Molecular and Cellular Biologists
        "19-2043.00",  # Hydrologists
        "19-2099.01",  # Remote Sensing Scientists and Technologists
        "21-1012.00",  # Educational, Guidance, and Career Counselors and Advisors
        "23-2011.00",  # Paralegals and Legal Assistants
        "25-1126.00",  # Philosophy and Religion Teachers, Postsecondary
        "25-2032.00",  # Career/Technical Education Teachers, Secondary School
        "25-4011.00",  # Archivists
        "27-3031.00",  # Public Relations Specialists
        "27-4014.00",  # Sound Engineering Technicians
        "29-1141.03",  # Critical Care Nurses
        "29-1299.01",  # Naturopathic Physicians
        "29-2011.02",  # Cytotechnologists
        "29-2091.00",  # Orthotists and Prosthetists
        "31-9093.00",  # Medical Equipment Preparers
        "33-1012.00",  # First-Line Supervisors of Police and Detectives
        "35-3031.00",  # Waiters and Waitresses
        "37-2012.00",  # Maids and Housekeeping Cleaners
        "39-3012.00",  # Gambling and Sports Book Writers and Runners
        "39-5092.00",  # Manicurists and Pedicurists
        "41-3041.00",  # Travel Agents
        "43-2011.00",  # Switchboard Operators, Including Answering Service
        "43-4111.00",  # Interviewers, Except Eligibility and Loan
        "43-9031.00",  # Desktop Publishers
        "45-3031.00",  # Fishing and Hunting Workers
        "47-2142.00",  # Paperhangers
        "47-2181.00",  # Roofers
        "47-4099.03",  # Weatherization Installers and Technicians
        "49-3043.00",  # Rail Car Repairers
        "49-9043.00",  # Maintenance Workers, Machinery
        "49-9064.00",  # Watch and Clock Repairers
        "51-2061.00",  # Timing Device Assemblers and Adjusters
        "51-6021.00",  # Pressers, Textile, Garment, and Related Materials
        "51-8013.03",  # Biomass Plant Technicians
        "51-9141.00",  # Semiconductor Processing Technicians
        "51-9195.04",  # Glass Blowers, Molders, Benders, and Finishers
        "53-1042.01",  # Recycling Coordinators
        "53-3011.00",  # Ambulance Drivers and Attendants, Except Emergency Medical
        "53-7051.00",  # Industrial Truck and Tractor Operators
    ],
}

# Model registry: maps user-facing names to (sdk, model_string, env_key, release_date)
MODEL_REGISTRY = {
    # OpenAI
    "gpt-4": ("openai", "gpt-4", "OPENAI_API_KEY", "March 2023"),
    "gpt-4-0314": ("openai", "gpt-4-0314", "OPENAI_API_KEY", "March 2023"),
    "gpt-4-0613": ("openai", "gpt-4-0613", "OPENAI_API_KEY", "June 2023"),
    "gpt-4-turbo-2024-04-09": ("openai", "gpt-4-turbo-2024-04-09", "OPENAI_API_KEY", "April 2024"),
    "gpt-4o": ("openai", "gpt-4o", "OPENAI_API_KEY", "May 2024"),
    "gpt-5": ("openai", "gpt-5-2025-08-07", "OPENAI_API_KEY", "August 2025"),
    "gpt-5.1": ("openai", "gpt-5.1-2025-11-13", "OPENAI_API_KEY", "November 2025"),
    "gpt-5-mini": ("openai", "gpt-5-mini", "OPENAI_API_KEY", "August 2025"),
    "gpt-5.2": ("openai", "gpt-5.2-2025-12-11", "OPENAI_API_KEY", "December 2025"),
    "gpt-5.4": ("openai", "gpt-5.4-2026-03-05", "OPENAI_API_KEY", "March 2026"),
    # OpenAI reasoning models
    "o1": ("openai", "o1-2024-12-17", "OPENAI_API_KEY", "December 2024"),
    "o3": ("openai", "o3-2025-04-16", "OPENAI_API_KEY", "April 2025"),
    # Anthropic
    "claude-sonnet-4-6": ("anthropic", "claude-sonnet-4-6", "ANTHROPIC_API_KEY", "March 2026"),
    "claude-opus-4-6": ("anthropic", "claude-opus-4-6", "ANTHROPIC_API_KEY", "March 2026"),
    # Google
    "gemini-3-flash": ("google", "gemini-3-flash-preview", "GEMINI_API_KEY", "March 2026"),
    "gemini-3-pro": ("google", "gemini-3-pro-preview", "GEMINI_API_KEY", "March 2026"),
}


# ── Data loading ─────────────────────────────────────────────────────────


def load_tasks_for_socs(csv_path: Path, soc_codes: list[str] | None = None) -> dict[str, list[dict]]:
    """Load tasks grouped by SOC code.

    Args:
        csv_path: Path to onet_tasks_18k.csv
        soc_codes: SOC codes to include. If None, loads all.

    Returns:
        Dict mapping soc_code -> list of {"task_id": int, "task_description": str, "title": str}
    """
    soc_set = set(soc_codes) if soc_codes is not None else None
    grouped: dict[str, list[dict]] = defaultdict(list)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            soc = row["onet_soc_code"]
            if soc_set is None or soc in soc_set:
                grouped[soc].append({
                    "task_id": int(row["task_id"]),
                    "task_description": row["task_description"],
                    "title": row["occupation_title"],
                })
    return dict(grouped)


# ── API dispatch ─────────────────────────────────────────────────────────


async def call_model_async(sdk: str, model: str, api_key: str, system_prompt: str,
                           user_prompt: str, seed: int | None = None) -> str:
    """Call a model via the appropriate async SDK. Returns raw response text."""
    if sdk == "openai":
        import openai
        client = openai.AsyncOpenAI(api_key=api_key)
        is_reasoning = any(model.startswith(p) for p in ("o1", "o3", "o4", "gpt-5-"))
        uses_new_api = is_reasoning or model.startswith("gpt-5")
        token_param = "max_completion_tokens" if uses_new_api else "max_tokens"

        # Reasoning models use "developer" role instead of "system",
        # and don't support temperature or seed
        if is_reasoning:
            messages = [
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            kwargs = {
                "model": model,
                "messages": messages,
                token_param: 16384,
            }
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.0,
                token_param: 4096,
            }
            if seed is not None:
                kwargs["seed"] = seed

        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    elif sdk == "anthropic":
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        response = await client.messages.create(
            model=model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.0,
            max_tokens=4096,
        )
        return response.content[0].text

    elif sdk == "google":
        from google import genai
        client = genai.Client(api_key=api_key)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
                max_output_tokens=4096,
            ),
        ))
        return response.text

    else:
        raise ValueError(f"Unknown SDK: {sdk!r}")


# ── Per-occupation runner ────────────────────────────────────────────────


async def _process_soc(
    soc: str,
    tasks: list[dict],
    sdk: str,
    model_string: str,
    model_name: str,
    api_key: str,
    system_prompt: str,
    rubric: str,
    output_dir: Path,
    seed: int | None,
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    """Process a single SOC under semaphore control."""
    checkpoint_path = output_dir / f"{soc}.json"

    # Resume from checkpoint
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            checkpoint = json.load(f)
        return checkpoint["parsed_labels"]

    if not tasks:
        return []

    title = tasks[0]["title"]
    expected_ids = [t["task_id"] for t in tasks]

    async with semaphore:
        try:
            user_prompt = build_user_prompt(title, tasks)
            raw_response = await call_model_async(
                sdk, model_string, api_key, system_prompt,
                user_prompt, seed=seed,
            )
            parsed = parse_response(raw_response, expected_ids)
            unparsed = [tid for tid in expected_ids if tid not in {p["task_id"] for p in parsed}]

            checkpoint = {
                "soc_code": soc,
                "occupation_title": title,
                "model": model_name,
                "model_string": model_string,
                "rubric": rubric,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "n_tasks": len(tasks),
                "n_parsed": len(parsed),
                "n_unparsed": len(unparsed),
                "raw_response": raw_response,
                "parsed_labels": parsed,
                "unparsed_task_ids": unparsed,
            }

            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint, f, indent=2)

            status = f"parsed {len(parsed)}/{len(tasks)}"
            if unparsed:
                status += f" (WARNING: {len(unparsed)} unparsed)"
            print(f"  [{soc}] {title[:45]} ... {status}")

            return parsed

        except Exception as e:
            print(f"  [{soc}] ERROR: {e}")
            return []


def run_replication(
    model_name: str,
    rubric: str,
    soc_set: str,
    output_dir: Path,
    seed: int | None = None,
    concurrency: int = 1,
) -> None:
    """Run the Eloundou replication for a given model and SOC set."""
    if model_name not in MODEL_REGISTRY:
        print(f"Unknown model: {model_name!r}")
        print(f"Available: {', '.join(sorted(MODEL_REGISTRY))}")
        sys.exit(1)

    sdk, model_string, env_key, release_date = MODEL_REGISTRY[model_name]
    api_key = os.environ.get(env_key, "")
    if not api_key:
        print(f"Missing API key: {env_key}")
        sys.exit(1)

    if soc_set == "all":
        soc_codes = None
    else:
        soc_codes = SOC_SETS[soc_set]
    system_prompt = build_system_prompt(rubric, release_date=release_date)

    # Load tasks
    tasks_by_soc = load_tasks_for_socs(TASKS_CSV, soc_codes)
    soc_list = sorted(tasks_by_soc.keys())

    # Count how many already checkpointed
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sum(1 for s in soc_list if (output_dir / f"{s}.json").exists())

    print(f"Model: {model_name} ({model_string})")
    print(f"Rubric: {rubric}")
    print(f"SOC set: {soc_set} ({len(soc_list)} occupations, {existing} already checkpointed)")
    print(f"Concurrency: {concurrency}")
    print(f"Output: {output_dir}")
    print()

    if existing == len(soc_list):
        print(f"All {existing} occupations already checkpointed. No API calls needed.")
        print(f"Regenerating {output_dir / 'all_results.csv'} from checkpoints.")

    async def _run():
        semaphore = asyncio.Semaphore(concurrency)
        tasks_coros = [
            _process_soc(
                soc, tasks_by_soc.get(soc, []),
                sdk, model_string, model_name, api_key,
                system_prompt, rubric, output_dir, seed, semaphore,
            )
            for soc in soc_list
        ]
        results = await asyncio.gather(*tasks_coros)
        return [label for soc_labels in results for label in soc_labels]

    all_results = asyncio.run(_run())

    # Write aggregate CSV
    if all_results:
        csv_path = output_dir / "all_results.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["task_id", "label", "explanation"])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nWrote {len(all_results)} labels to {csv_path}")


# ── Per-task runner (Eloundou's exact method) ────────────────────────────


async def _process_single_task(
    task: dict,
    sdk: str,
    model_string: str,
    model_name: str,
    api_key: str,
    system_prompt: str,
    rubric: str,
    output_dir: Path,
    seed: int | None,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    """Process a single task under semaphore control."""
    task_id = task["task_id"]
    checkpoint_path = output_dir / f"task_{task_id}.json"

    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            return json.load(f)

    async with semaphore:
        try:
            user_prompt = build_user_prompt_single_task(
                task["title"], task["task_id"], task["description"],
            )
            raw_response = await call_model_async(
                sdk, model_string, api_key, system_prompt,
                user_prompt, seed=seed,
            )
            parsed = parse_response(raw_response, [task_id])
            label = parsed[0]["label"] if parsed else "PARSE_ERROR"
            explanation = parsed[0]["explanation"] if parsed else raw_response[:200]

            result = {
                "task_id": task_id,
                "soc_code": task["soc_code"],
                "occupation_title": task["title"],
                "model": model_name,
                "rubric": rubric,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "label": label,
                "explanation": explanation,
                "eloundou_label": task.get("eloundou_label", ""),
                "raw_response": raw_response,
            }

            with open(checkpoint_path, "w") as f:
                json.dump(result, f, indent=2)

            print(f"  [task {task_id}] {task['title'][:35]} ... {label}")
            return result

        except Exception as e:
            print(f"  [task {task_id}] ERROR: {e}")
            return None


def run_per_task(
    model_name: str,
    rubric: str,
    output_dir: Path,
    seed: int | None = None,
    concurrency: int = 10,
    n_tasks: int | None = None,
    task_sample_path: Path | None = None,
) -> None:
    """Run per-task replication (Eloundou's exact method)."""
    if model_name not in MODEL_REGISTRY:
        print(f"Unknown model: {model_name!r}")
        sys.exit(1)

    sdk, model_string, env_key, release_date = MODEL_REGISTRY[model_name]
    api_key = os.environ.get(env_key, "")
    if not api_key:
        print(f"Missing API key: {env_key}")
        sys.exit(1)

    system_prompt = build_system_prompt(rubric, release_date=release_date)

    sample_path = task_sample_path or STRAT50_SAMPLE
    with open(sample_path) as f:
        task_list = json.load(f)

    if n_tasks is not None:
        task_list = task_list[:n_tasks]

    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sum(1 for t in task_list if (output_dir / f"task_{t['task_id']}.json").exists())

    print(f"Model: {model_name} ({model_string})")
    print(f"Rubric: {rubric}")
    print(f"Mode: per-task (Eloundou method)")
    print(f"Tasks: {len(task_list)} ({existing} already checkpointed)")
    print(f"Concurrency: {concurrency}")
    print(f"Output: {output_dir}")
    print()

    if existing == len(task_list):
        print(f"All {existing} tasks already checkpointed. No API calls needed.")
        print(f"Regenerating {output_dir / 'all_results.csv'} from checkpoints.")

    async def _run():
        semaphore = asyncio.Semaphore(concurrency)
        coros = [
            _process_single_task(
                task, sdk, model_string, model_name, api_key,
                system_prompt, rubric, output_dir, seed, semaphore,
            )
            for task in task_list
        ]
        return await asyncio.gather(*coros)

    results = [r for r in asyncio.run(_run()) if r is not None]

    # Write aggregate CSV
    if results:
        csv_path = output_dir / "all_results.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "task_id", "soc_code", "label", "eloundou_label", "explanation",
            ])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "task_id": r["task_id"], "soc_code": r["soc_code"],
                    "label": r["label"], "eloundou_label": r["eloundou_label"],
                    "explanation": r["explanation"],
                })
        print(f"\nWrote {len(results)} labels to {csv_path}")

        # Quick agreement summary
        agree = sum(1 for r in results
                    if r["label"].replace("E3", "E2") == r["eloundou_label"].replace("E3", "E2"))
        print(f"Agreement with Eloundou: {agree}/{len(results)} ({agree/len(results):.1%})")


def main():
    # Load env vars from repo root
    repo_root = PACKAGE_ROOT.parent
    for env_file in [".env", ".env.local"]:
        env_path = repo_root / env_file
        if env_path.exists():
            load_dotenv(env_path)

    parser = argparse.ArgumentParser(description="Eloundou replication runner")
    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(MODEL_REGISTRY),
        help="Model to use for classification",
    )
    parser.add_argument(
        "--rubric",
        default="eloundou_2023",
        choices=["eloundou_2023", "frontier_2026"],
        help="Rubric variant (default: eloundou_2023)",
    )
    parser.add_argument(
        "--soc-set",
        default="pilot",
        choices=sorted(SOC_SETS) + ["all"],
        help="SOC set: pilot (3), expanded (12), stratified_50 (50), or all (923)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (OpenAI only)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Max concurrent API calls (default: 10). Lower this if you hit rate limits. "
        "GPT-4-0613 at Tier 1 (10k TPM) supports ~3 concurrent; Tier 3+ (300k TPM) supports 50+.",
    )
    parser.add_argument(
        "--per-task",
        action="store_true",
        help="Run in per-task mode (one API call per task, matching Eloundou's method). "
        "Uses the task sample from data/stratified_50_sample.json by default.",
    )
    parser.add_argument(
        "--n-tasks",
        type=int,
        default=None,
        help="Limit per-task mode to first N tasks (default: all in sample)",
    )
    parser.add_argument(
        "--task-sample",
        type=Path,
        default=None,
        help="Path to task sample JSON for per-task mode (default: data/stratified_50_sample.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: results/{model}-{mode}/)",
    )
    args = parser.parse_args()

    if args.per_task:
        output_dir = args.output_dir or (
            RESULTS_DIR / f"{args.model}-per-task"
        )
        run_per_task(args.model, args.rubric, output_dir,
                     seed=args.seed, concurrency=args.concurrency, n_tasks=args.n_tasks,
                     task_sample_path=args.task_sample)
    else:
        output_dir = args.output_dir or (
            RESULTS_DIR / f"{args.model}-per-occ"
        )
        run_replication(args.model, args.rubric, args.soc_set, output_dir,
                        seed=args.seed, concurrency=args.concurrency)


if __name__ == "__main__":
    main()
