from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dataset.registry import build_dataset

# Import dataset modules so they register themselves.
import dataset.sources.audiocaps.audiocaps_dataset  # noqa: F401
import dataset.sources.clotho.clotho_dataset  # noqa: F401
import dataset.sources.commonvoice.commonvoice_dataset  # noqa: F401
import dataset.sources.fleurs.fleurs_dataset  # noqa: F401
import dataset.sources.librispeech.librispeech_dataset  # noqa: F401
import dataset.sources.openhermes25.openhermes25_dataset  # noqa: F401
import dataset.sources.tulu3_sft_mixture.tulu3_sft_mixture_dataset  # noqa: F401
import dataset.sources.wenetspeech.wenetspeech_dataset  # noqa: F401


NEW_DATASETS = [
    "librispeech",
    "wenetspeech",
    "fleurs",
    "commonvoice",
    "audiocaps",
    "clotho",
    "openhermes25",
    "tulu3_sft_mixture",
]


def parse_dataset_config(config_path: Path) -> Dict[str, Dict[str, Any]]:
    datasets: Dict[str, Dict[str, Any]] = {}
    in_datasets = False
    current_dataset: str | None = None

    with config_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("#", 1)[0].rstrip()
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()

            if indent == 0:
                in_datasets = stripped == "datasets:"
                current_dataset = None
                continue

            if not in_datasets:
                continue

            if indent == 2 and stripped.endswith(":"):
                current_dataset = stripped[:-1]
                datasets[current_dataset] = {}
                continue

            if indent == 4 and current_dataset and ":" in stripped:
                key, value = stripped.split(":", 1)
                datasets[current_dataset][key.strip()] = parse_scalar(value.strip())

    return datasets


def parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", ""}:
        return None if value != "" else ""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def remap_root(root: str, source_prefix: str, target_prefix: str) -> str:
    if root.startswith(source_prefix):
        return target_prefix + root[len(source_prefix) :]
    return root


def validate_sample(sample: Dict[str, Any], dataset_root: Path) -> Dict[str, Any]:
    issues: List[str] = []
    audio_checks: List[Dict[str, Any]] = []

    required_top_level = ["id", "messages", "task", "data_source"]
    for key in required_top_level:
        if key not in sample:
            issues.append(f"missing top-level key: {key}")

    messages = sample.get("messages")
    if not isinstance(messages, list) or not messages:
        issues.append("messages must be a non-empty list")
        return {"issues": issues, "audio_checks": audio_checks}

    for msg_index, message in enumerate(messages):
        if not isinstance(message, dict):
            issues.append(f"message[{msg_index}] is not a dict")
            continue
        if "role" not in message:
            issues.append(f"message[{msg_index}] missing role")
        content = message.get("content")
        if not isinstance(content, list) or not content:
            issues.append(f"message[{msg_index}] content must be a non-empty list")
            continue

        for content_index, item in enumerate(content):
            if not isinstance(item, dict):
                issues.append(
                    f"message[{msg_index}].content[{content_index}] is not a dict"
                )
                continue
            if "text" not in item:
                issues.append(
                    f"message[{msg_index}].content[{content_index}] missing text"
                )
            if "audio_path" not in item:
                issues.append(
                    f"message[{msg_index}].content[{content_index}] missing audio_path"
                )
                continue

            audio_path = item.get("audio_path")
            if audio_path is None:
                audio_checks.append(
                    {
                        "message_index": msg_index,
                        "content_index": content_index,
                        "audio_path": None,
                        "exists": None,
                    }
                )
                continue

            path_obj = Path(str(audio_path))
            resolved = path_obj if path_obj.is_absolute() else dataset_root / path_obj
            audio_checks.append(
                {
                    "message_index": msg_index,
                    "content_index": content_index,
                    "audio_path": str(audio_path),
                    "resolved_path": str(resolved),
                    "exists": resolved.exists(),
                }
            )
            if not resolved.exists():
                issues.append(
                    "missing audio file at "
                    f"message[{msg_index}].content[{content_index}]: {resolved}"
                )

    return {"issues": issues, "audio_checks": audio_checks}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate newly added dataset loaders against multi_dataset_config.yaml."
    )
    parser.add_argument(
        "--config",
        default=str(
            Path(__file__).resolve().parent / "multi_dataset_config.yaml"
        ),
    )
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parent / "LOCAL_DATASET_SAMPLE_VALIDATION_REPORT.md"
        ),
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--source-prefix",
        default="/mnt/afs/share/voice_model_project",
    )
    parser.add_argument(
        "--target-prefix",
        default="/data/share/voice_model_project",
    )
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    datasets_cfg = parse_dataset_config(config_path)
    report_lines: List[str] = []
    report_lines.append("# Local Dataset Sample Validation Report")
    report_lines.append("")
    report_lines.append(f"- Config: `{config_path}`")
    report_lines.append(
        f"- Root remap: `{args.source_prefix}` -> `{args.target_prefix}`"
    )
    report_lines.append(f"- Sample count per dataset: `{args.sample_count}`")
    report_lines.append("")
    report_lines.append("## Process")
    report_lines.append("")
    report_lines.append(
        "1. Read `dataset/load_dataset/multi_dataset_config.yaml`."
    )
    report_lines.append(
        "2. For each newly added dataset, remap the configured root to the local `/data/share/...` prefix."
    )
    report_lines.append(
        "3. Instantiate the registered loader with `max_samples=<sample-count>`."
    )
    report_lines.append(
        "4. Validate top-level fields, `messages` structure, and whether each non-null `audio_path` resolves to an existing file."
    )
    report_lines.append("")

    overall_failures = 0

    for dataset_name in NEW_DATASETS:
        raw_cfg = datasets_cfg.get(dataset_name)
        report_lines.append(f"## {dataset_name}")
        report_lines.append("")

        if raw_cfg is None:
            overall_failures += 1
            report_lines.append("- Status: missing dataset config entry")
            report_lines.append("")
            continue

        dataset_kwargs = {
            key: value
            for key, value in raw_cfg.items()
            if key not in {"enabled"}
        }
        original_root = str(dataset_kwargs["root"])
        local_root = remap_root(original_root, args.source_prefix, args.target_prefix)
        dataset_kwargs["dataset_root"] = local_root
        dataset_kwargs.pop("root", None)
        dataset_kwargs["max_samples"] = args.sample_count

        report_lines.append(f"- Original root: `{original_root}`")
        report_lines.append(f"- Local root: `{local_root}`")
        report_lines.append(f"- Loader kwargs: `{json.dumps(dataset_kwargs, ensure_ascii=False)}`")

        try:
            dataset = build_dataset(name=dataset_name, **dataset_kwargs)
        except Exception as exc:
            overall_failures += 1
            report_lines.append(f"- Status: failed to instantiate: `{type(exc).__name__}: {exc}`")
            report_lines.append("")
            continue

        report_lines.append(f"- Loaded samples: `{len(dataset)}`")
        if len(dataset) == 0:
            overall_failures += 1
            report_lines.append("- Status: loader returned zero samples")
            report_lines.append("")
            continue

        dataset_root = Path(local_root)
        dataset_has_failures = False
        report_lines.append("- Sample checks:")
        for index, sample in enumerate(dataset):
            validation = validate_sample(sample, dataset_root)
            if validation["issues"]:
                dataset_has_failures = True

            report_lines.append(
                f"  - sample[{index}] id=`{sample.get('id')}` task=`{sample.get('task')}` data_source=`{sample.get('data_source')}`"
            )
            if validation["issues"]:
                for issue in validation["issues"]:
                    report_lines.append(f"    - issue: {issue}")
            else:
                report_lines.append("    - structure: ok")

            for audio_check in validation["audio_checks"]:
                if audio_check["audio_path"] is None:
                    report_lines.append(
                        "    - audio_path: null"
                    )
                else:
                    report_lines.append(
                        "    - audio_path: "
                        f"`{audio_check['audio_path']}` -> `{audio_check['resolved_path']}` "
                        f"(exists={audio_check['exists']})"
                    )

            report_lines.append("    - sample json:")
            report_lines.append("```json")
            report_lines.append(
                json.dumps(sample, ensure_ascii=False, indent=2)[:4000]
            )
            report_lines.append("```")

        report_lines.append(
            f"- Status: {'passed' if not dataset_has_failures else 'failed'}"
        )
        if dataset_has_failures:
            overall_failures += 1
        report_lines.append("")

    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append(
        f"- Overall result: `{'passed' if overall_failures == 0 else 'failed'}`"
    )
    report_lines.append(f"- Datasets with failures: `{overall_failures}`")
    report_lines.append("")

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
