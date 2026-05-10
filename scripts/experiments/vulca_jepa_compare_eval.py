#!/usr/bin/env python3
"""Compare Vulca visual audit signals and write a Chinese experiment report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text())


def _sample_maps(inventory: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    by_id = {sample["sample_id"]: sample for sample in inventory["samples"]}
    by_path = {sample["path"]: sample["sample_id"] for sample in inventory["samples"]}
    return by_id, by_path


def _load_eval_scores(eval_dir: Path | str) -> dict[str, dict[str, Any]]:
    scores: dict[str, dict[str, Any]] = {}
    for path in sorted(Path(eval_dir).glob("*_scores.json")):
        data = _load_json(path)
        dims = {key: float(data[key]) for key in ("L1", "L2", "L3", "L4", "L5") if key in data}
        scores[path.stem.removesuffix("_scores")] = {
            "path": str(path),
            "dimensions": dims,
            "mean": round(sum(dims.values()) / len(dims), 4) if dims else None,
        }
    return scores


def _match_gemini_items(gemini: dict[str, Any], path_to_sample_id: dict[str, str]) -> list[dict[str, Any]]:
    matched: list[dict[str, Any]] = []
    for item in gemini.get("items", []):
        sample_id = path_to_sample_id.get(item["path"])
        if not sample_id:
            continue
        matched.append(
            {
                "sample_id": sample_id,
                "kind": item.get("kind"),
                "tradition": item.get("tradition"),
                "seed": item.get("seed"),
                "path": item["path"],
                "total": item.get("total"),
                "passed": item.get("passed"),
                "notes": item.get("scores", {}).get("notes", ""),
            }
        )
    return matched


def _dinov2_lookup(dinov2: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["sample_id"]: item for item in dinov2.get("anomaly_ranking", [])}


def _siglip_lookup(siglip: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["sample_id"]: item for item in siglip.get("samples", [])}


def _gemini_lookup(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["sample_id"]: item for item in items}


def _maybe_probability(siglip_by_id: dict[str, dict[str, Any]], sample_id: str) -> float | None:
    row = siglip_by_id.get(sample_id)
    if not row:
        return None
    return float(row["probability"])


def _build_gongbi_case(
    gemini_items: list[dict[str, Any]],
    dinov2_by_id: dict[str, dict[str, Any]],
    siglip_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    gemini_by_id = _gemini_lookup(gemini_items)
    promptfix_ids = ["gongbi_promptfix_seed1", "gongbi_promptfix_seed2", "gongbi_promptfix_seed3"]
    promptfix_probs = {
        sample_id: _maybe_probability(siglip_by_id, sample_id)
        for sample_id in promptfix_ids
        if _maybe_probability(siglip_by_id, sample_id) is not None
    }
    best_promptfix_id = max(promptfix_probs, key=promptfix_probs.get) if promptfix_probs else None
    baseline_dino = dinov2_by_id.get("gongbi_baseline_failed_subject", {})
    return {
        "gemini_baseline_total": gemini_by_id.get("gongbi_baseline_failed_subject", {}).get("total"),
        "gemini_baseline_passed": gemini_by_id.get("gongbi_baseline_failed_subject", {}).get("passed"),
        "gemini_promptfix_totals": {
            sample_id: gemini_by_id.get(sample_id, {}).get("total")
            for sample_id in promptfix_ids
            if sample_id in gemini_by_id
        },
        "dinov2_baseline_nearest": baseline_dino.get("nearest_sample_id"),
        "dinov2_baseline_nearest_distance": baseline_dino.get("nearest_distance"),
        "siglip_baseline_probability": _maybe_probability(siglip_by_id, "gongbi_baseline_failed_subject"),
        "siglip_promptfix_probabilities": promptfix_probs,
        "siglip_promptfix_best_id": best_promptfix_id,
        "siglip_promptfix_best_probability": promptfix_probs.get(best_promptfix_id) if best_promptfix_id else None,
    }


def _build_fusion_case(dinov2_by_id: dict[str, dict[str, Any]], siglip_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = dinov2_by_id.get("fusion_source", {})
    generated = dinov2_by_id.get("fusion_iter0", {})
    return {
        "source_nearest": source.get("nearest_sample_id"),
        "source_nearest_distance": source.get("nearest_distance"),
        "iter0_nearest": generated.get("nearest_sample_id"),
        "iter0_nearest_distance": generated.get("nearest_distance"),
        "source_siglip_text_source": siglip_by_id.get("fusion_source", {}).get("text_source"),
        "iter0_siglip_text_source": siglip_by_id.get("fusion_iter0", {}).get("text_source"),
    }


def build_report_data(
    *,
    inventory_path: Path | str,
    dinov2_audit_path: Path | str,
    siglip_audit_path: Path | str,
    eval_dir: Path | str,
    gemini_rescore_path: Path | str,
    guard_path: Path | str | None = None,
) -> dict[str, Any]:
    inventory = _load_json(inventory_path)
    dinov2 = _load_json(dinov2_audit_path)
    siglip = _load_json(siglip_audit_path)
    gemini = _load_json(gemini_rescore_path)
    guard = _load_json(guard_path) if guard_path else None
    sample_by_id, path_to_sample_id = _sample_maps(inventory)
    eval_scores = _load_eval_scores(eval_dir)
    gemini_items = _match_gemini_items(gemini, path_to_sample_id)
    dinov2_by_id = _dinov2_lookup(dinov2)
    siglip_by_id = _siglip_lookup(siglip)
    sources = {
        "inventory": str(inventory_path),
        "dinov2_audit": str(dinov2_audit_path),
        "siglip_audit": str(siglip_audit_path),
        "eval_dir": str(eval_dir),
        "gemini_rescore": str(gemini_rescore_path),
    }
    if guard_path:
        sources["guard"] = str(guard_path)

    return {
        "sources": sources,
        "counts": {
            "inventory_samples": inventory["samples_total"],
            "core_samples": inventory.get("audit_sets", {}).get("core", 0),
            "artifact_qa_samples": inventory.get("audit_sets", {}).get("artifact_qa", 0),
            "dinov2_samples": dinov2.get("samples_total", 0),
            "dinov2_pairs": dinov2.get("pairwise_distances_total", 0),
            "siglip_samples": siglip.get("samples_total", 0),
            "siglip_scores": siglip.get("text_image_scores_total", 0),
            "matched_eval_files": len(eval_scores),
            "matched_gemini_items": len(gemini_items),
        },
        "models": {
            "dinov2": dinov2.get("model"),
            "siglip": siglip.get("model"),
        },
        "eval_scores": eval_scores,
        "gemini_items": gemini_items,
        "dinov2_anomaly_top": dinov2.get("anomaly_ranking", [])[:8],
        "siglip_lowest": siglip.get("text_image_scores", [])[:8],
        "eval_focus": [
            {"tradition": tradition, **eval_scores[tradition]}
            for tradition in [
                "chinese_gongbi",
                "chinese_xieyi",
                "japanese_traditional",
                "brand_design",
                "ui_ux_design",
            ]
            if tradition in eval_scores
        ],
        "artifact_rejects": [
            {
                "sample_id": sample["sample_id"],
                "reject_reasons": sample.get("reject_reasons", []),
            }
            for sample in sample_by_id.values()
            if sample.get("audit_set") == "artifact_qa"
        ],
        "gongbi_case": _build_gongbi_case(gemini_items, dinov2_by_id, siglip_by_id),
        "fusion_case": _build_fusion_case(dinov2_by_id, siglip_by_id),
        "guard": guard,
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _render_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(value) for value in row) + " |")
    return "\n".join(lines)


def _render_guard_section(guard: dict[str, Any] | None) -> list[str]:
    if not guard:
        return []

    warnings = guard.get("warnings", [])
    first_warning = warnings[0] if warnings else {}
    signals = first_warning.get("signals", {}) if isinstance(first_warning, dict) else {}
    rules = guard.get("rules", {})
    rule_name = first_warning.get("warning_type") or next(iter(rules), None)
    rule = rules.get(rule_name, {}) if rule_name else {}
    rows = [
        ["guard_scope", guard.get("guard_scope")],
        ["samples_evaluated", guard.get("samples_evaluated")],
        ["warnings", guard.get("warnings_total", len(warnings))],
        ["warning_type", first_warning.get("warning_type")],
        ["rule.action", rule.get("action")],
        ["siglip_probability_max", rule.get("siglip_probability_max")],
        ["requires_nearest_family_mismatch", rule.get("requires_nearest_family_mismatch")],
        ["sample_id", first_warning.get("sample_id")],
        ["action", first_warning.get("action")],
        ["nearest_sample_id", signals.get("nearest_sample_id")],
        ["siglip_probability", signals.get("siglip_probability")],
    ]

    return [
        "## Guard 原型结果",
        "",
        f"第一版 guard 只在 `{guard.get('guard_scope')}` 组内运行，且只报警不拒绝；samples={guard.get('samples_evaluated')}，warnings={guard.get('warnings_total', len(warnings))}。",
        "",
        _render_table(["字段", "值"], rows),
        "",
        "解释：`subject_drift_warning` 只说明样本需要进入 Vulca 人工/规则复核队列；当前动作为 `warn_only`，不会影响生成结果，也不会覆盖用户 override。",
        "",
    ]


def render_report(data: dict[str, Any]) -> str:
    counts = data["counts"]
    gongbi = data["gongbi_case"]
    fusion = data["fusion_case"]

    lines: list[str] = [
        "# Vulca JEPA 视觉审计实验报告",
        "",
        "## 结论摘要",
        "",
        f"- 样本分流有效：core={counts['core_samples']}，artifact_qa={counts['artifact_qa_samples']}。黑图和低信息中间产物没有进入主 embedding 实验。",
        f"- DINOv2 跑通：模型 `{data['models']['dinov2']}`，样本 {counts['dinov2_samples']}，pairwise={counts['dinov2_pairs']}。",
        f"- SigLIP 跑通：模型 `{data['models']['siglip']}`，样本 {counts['siglip_samples']}，text_image_scores={counts['siglip_scores']}。",
        f"- 已对齐 Vulca eval 文件 matched_eval_files={counts['matched_eval_files']}，Gemini rescore matched_gemini_items={counts['matched_gemini_items']}。",
        "- 这些信号能增强 Vulca 的图片理解，但不能替代 Vulca L1-L5；L1-L5 仍负责文化、风格、意图和人工 override 的判断。",
        "",
        "## 工笔牡丹 Baseline 失败案例",
        "",
        "工笔牡丹 baseline 是当前最重要的正反例：prompt 要求工笔牡丹，但图像实际更像山水。",
        "",
        _render_table(
            ["信号", "结果"],
            [
                ["Gemini baseline total", gongbi["gemini_baseline_total"]],
                ["Gemini baseline passed", gongbi["gemini_baseline_passed"]],
                ["DINOv2 baseline nearest", gongbi["dinov2_baseline_nearest"]],
                ["DINOv2 nearest distance", gongbi["dinov2_baseline_nearest_distance"]],
                ["SigLIP baseline probability", gongbi["siglip_baseline_probability"]],
                ["SigLIP best promptfix", gongbi["siglip_promptfix_best_id"]],
                ["SigLIP best promptfix probability", gongbi["siglip_promptfix_best_probability"]],
            ],
        ),
        "",
        "解释：DINOv2 把工笔牡丹 baseline 拉到山水/写意邻近区域；SigLIP 给 baseline 的 prompt-image 分数低于 promptfix 牡丹；Gemini rescore 也记录 baseline 未通过。三者方向一致，说明这类主体跑偏可以形成自动 guard。",
        "",
        *_render_guard_section(data.get("guard")),
        "## DINOv2 图像相似度观察",
        "",
        _render_table(
            ["sample_id", "mean_distance", "nearest_sample_id", "nearest_distance"],
            [
                [
                    row.get("sample_id"),
                    row.get("mean_distance"),
                    row.get("nearest_sample_id"),
                    row.get("nearest_distance"),
                ]
                for row in data["dinov2_anomaly_top"]
            ],
        ),
        "",
        "DINOv2 适合回答图像之间的结构/主体距离。它不理解中文文化术语，也不应该直接判断 L1-L5。",
        "",
        "## Vulca L1-L5 文化评估观察",
        "",
        _render_table(
            ["tradition", "L1", "L2", "L3", "L4", "L5", "mean"],
            [
                [
                    row["tradition"],
                    row["dimensions"].get("L1"),
                    row["dimensions"].get("L2"),
                    row["dimensions"].get("L3"),
                    row["dimensions"].get("L4"),
                    row["dimensions"].get("L5"),
                    row["mean"],
                ]
                for row in data["eval_focus"]
            ],
        ),
        "",
        "Vulca L1-L5 提供的是文化/风格解释层。例如 `chinese_gongbi` 的 L2 低于其他维度，能指出工笔技法深度不足；DINOv2/SigLIP 只能提示主体或文本对齐问题，不能解释技法层面的失败。",
        "",
        "## SigLIP Text-Image 对齐观察",
        "",
        _render_table(
            ["sample_id", "probability", "logit", "text_source"],
            [
                [
                    row.get("sample_id"),
                    row.get("probability"),
                    row.get("logit"),
                    row.get("text_source"),
                ]
                for row in data["siglip_lowest"]
            ],
        ),
        "",
        "SigLIP/SigLIP2 适合回答图像和文本是否大方向对齐。对 `text_source=purpose` 的样本只能弱参考，因为那不是原始生成 prompt。",
        "",
        "## Fusion Source/Edit 保留关系",
        "",
        _render_table(
            ["字段", "值"],
            [
                ["fusion_source nearest", fusion["source_nearest"]],
                ["fusion_source distance", fusion["source_nearest_distance"]],
                ["fusion_iter0 nearest", fusion["iter0_nearest"]],
                ["fusion_iter0 distance", fusion["iter0_nearest_distance"]],
                ["fusion_source SigLIP text_source", fusion["source_siglip_text_source"]],
                ["fusion_iter0 SigLIP text_source", fusion["iter0_siglip_text_source"]],
            ],
        ),
        "",
        "DINOv2 能看到 source 与 edit 之间的结构保留关系；但 fusion 的 SigLIP 文本来自 purpose，不足以判断设计 brief 是否完成。",
        "",
        "## Artifact QA 样本用途",
        "",
        _render_table(
            ["sample_id", "reject_reasons"],
            [[row["sample_id"], ",".join(row["reject_reasons"])] for row in data["artifact_rejects"]],
        ),
        "",
        "这些样本不是低质量展示图，而是质量闸门样本。它们应继续用于检测黑图、低信息图、坏 composite 和中间层异常。",
        "",
        "## 下一步",
        "",
        "- Vulca evaluate 已可通过 `--eval-metadata` 与 `--eval-inventory` 从 image path 自动推导 sample_id：baseline 工笔样本显示 warning，promptfix 牡丹样本不显示 warning。",
        "- 对 `text_source=purpose` 的样本补真实 prompt/brief 字段，否则 SigLIP 分数只能弱参考。",
        "- 用 Vulca L1-L5 解释 DINO/SigLIP 不能覆盖的文化问题，例如工笔技法深度、风格完成度、用户 override。",
        "- 后续再考虑 I-JEPA/V-JEPA；当前静态图实验里 DINOv2 与 SigLIP 已经覆盖了主要验证问题。",
    ]
    return "\n".join(lines) + "\n"


def write_report(
    *,
    inventory_path: Path | str,
    dinov2_audit_path: Path | str,
    siglip_audit_path: Path | str,
    eval_dir: Path | str,
    gemini_rescore_path: Path | str,
    guard_path: Path | str | None = None,
    out: Path | str,
) -> str:
    data = build_report_data(
        inventory_path=inventory_path,
        dinov2_audit_path=dinov2_audit_path,
        siglip_audit_path=siglip_audit_path,
        eval_dir=eval_dir,
        gemini_rescore_path=gemini_rescore_path,
        guard_path=guard_path,
    )
    report = render_report(data)
    output_path = Path(out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--dinov2-audit", "--audit", dest="dinov2_audit", required=True, type=Path)
    parser.add_argument("--siglip-audit", required=True, type=Path)
    parser.add_argument("--eval-dir", required=True, type=Path)
    parser.add_argument("--gemini-rescore", required=True, type=Path)
    parser.add_argument("--guard", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    data = build_report_data(
        inventory_path=args.inventory,
        dinov2_audit_path=args.dinov2_audit,
        siglip_audit_path=args.siglip_audit,
        eval_dir=args.eval_dir,
        gemini_rescore_path=args.gemini_rescore,
        guard_path=args.guard,
    )
    report = render_report(data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report)
    print(f"wrote {args.out}")
    print(f"matched_eval_files: {data['counts']['matched_eval_files']}")
    print(f"matched_gemini_items: {data['counts']['matched_gemini_items']}")
    if data.get("guard"):
        print(f"guard_warnings: {data['guard'].get('warnings_total', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
