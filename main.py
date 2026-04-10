from pathlib import Path
import os
import re
import yaml
import argparse
from dotenv import load_dotenv

from zai import ZhipuAiClient
from scripts.classify_file import classify_file
from scripts.apply_rules import generate_candidate_from_os_h
from scripts.repo_verify import run_repo_verify_pipeline


def load_settings(settings_path: Path) -> dict:
    with settings_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_sections(model_output: str):
    file_content = ""
    notes = ""

    file_match = re.search(
        r"【目标文件内容】\s*(.*?)\s*【改写说明】",
        model_output,
        flags=re.DOTALL,
    )
    notes_match = re.search(
        r"【改写说明】\s*(.*)",
        model_output,
        flags=re.DOTALL,
    )

    if file_match:
        file_content = file_match.group(1).strip()
    if notes_match:
        notes = notes_match.group(1).strip()

    return file_content, notes


def normalize_generated_os_text(text: str) -> str:
    text = text.lstrip()
    text = re.sub(r"^#\s+define", "#define", text, flags=re.MULTILINE)
    text = re.sub(r"^#\s+else", "#else", text, flags=re.MULTILINE)
    text = re.sub(r"^#\s+endif", "#endif", text, flags=re.MULTILINE)
    text = text.rstrip() + "\n"
    return text


def parse_args():
    parser = argparse.ArgumentParser(description="CCCL -> ACCL migration prototype")
    parser.add_argument("--input", required=True, help="待迁移的 CCCL 文件路径")
    parser.add_argument(
        "--repo-verify",
        action="store_true",
        help="如果输入文件已支持完整流程，则继续执行 repo verify（创建分支、commit、push）",
    )
    return parser.parse_args()


def save_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_os_h_full_pipeline(project_root: Path, settings: dict, input_path: Path, do_repo_verify: bool):
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError("未读取到 ZHIPU_API_KEY，请检查 .env 文件")

    expected_path = project_root / settings["paths"]["expected_file"]
    prompt_path = project_root / "skills" / "cccl-to-accl-rewrite" / "prompts" / "rewrite_prompt.md"
    rule_path = project_root / "skills" / "cccl-to-accl-rewrite" / "rules" / "os_h_rules.yaml"
    candidate_path = project_root / settings["paths"]["output_dir"] / "candidate_accl_os.h"

    if not input_path.exists():
        raise FileNotFoundError(f"找不到输入文件: {input_path}")
    if not expected_path.exists():
        raise FileNotFoundError(f"找不到参考目标文件: {expected_path}")

    generate_candidate_from_os_h(input_path, rule_path, candidate_path)

    source_text = input_path.read_text(encoding="utf-8")
    expected_text = expected_path.read_text(encoding="utf-8")
    candidate_text = candidate_path.read_text(encoding="utf-8")
    prompt_text = prompt_path.read_text(encoding="utf-8")

    user_content = f"""下面是本次改写任务的三份输入内容，请你严格按照 system prompt 的要求输出。

【原始 CCCL os.h】
{source_text}

【规则生成的候选 ACCL os.h】
{candidate_text}

【参考 ACCL os.h】
{expected_text}
"""

    client = ZhipuAiClient(api_key=api_key)

    response = client.chat.completions.create(
        model=settings["model"]["model_name"],
        messages=[
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )

    model_output = response.choices[0].message.content
    final_file_text, rewrite_notes = extract_sections(model_output)

    if not final_file_text:
        raise ValueError("未能从模型输出中提取【目标文件内容】部分，请检查 prompt 或模型返回内容。")

    final_file_text = normalize_generated_os_text(final_file_text)

    output_dir = project_root / settings["paths"]["output_dir"]
    save_text(output_dir / "final_accl_os.h", final_file_text)
    save_text(output_dir / "rewrite_notes.md", rewrite_notes)
    save_text(output_dir / "rewrite_raw_output.md", model_output)

    print("已完成 os.h 全流程改写：")
    print(f"- candidate: {output_dir / 'candidate_accl_os.h'}")
    print(f"- final: {output_dir / 'final_accl_os.h'}")
    print(f"- notes: {output_dir / 'rewrite_notes.md'}")

    if do_repo_verify:
        print("\n开始执行 repo verify...")
        verify_result = run_repo_verify_pipeline(project_root, settings)

        print("\n=== repo verify 结果 ===")
        for k, v in verify_result.items():
            print(f"{k}: {v}")


def main():
    load_dotenv()
    args = parse_args()

    project_root = Path(__file__).resolve().parent
    settings = load_settings(project_root / "config" / "settings.yaml")

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    content = input_path.read_text(encoding="utf-8")
    classification = classify_file(str(input_path), content)

    output_dir = project_root / settings["paths"]["output_dir"]
    save_text(output_dir / "classification_result.md", "\n".join(f"{k}: {v}" for k, v in classification.items()))

    print("=== 文件分类结果 ===")
    for k, v in classification.items():
        print(f"{k}: {v}")

    if classification["support_level"] == "full" and classification["file_type"] == "os_h":
        run_os_h_full_pipeline(project_root, settings, input_path, args.repo_verify)
    else:
        print("\n当前文件尚未接入完整自动迁移流程。")
        print("当前系统已完成：分类与支持状态判定。")
        print("后续可扩展为：分析模式 / 候选改写模式 / 全自动验证模式。")


if __name__ == "__main__":
    main()