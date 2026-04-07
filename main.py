from pathlib import Path
import os
import re
import yaml
from dotenv import load_dotenv

from zai import ZhipuAiClient


def load_settings(settings_path: Path) -> dict:
    with settings_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_sections(model_output: str) -> tuple[str, str]:
    """
    从模型输出中提取：
    1. 目标文件内容
    2. 改写说明
    """
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


def main():
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError("未读取到 ZHIPU_API_KEY，请检查 .env 文件")

    project_root = Path(__file__).resolve().parent
    settings = load_settings(project_root / "config" / "settings.yaml")

    source_path = project_root / settings["paths"]["source_file"]
    expected_path = project_root / settings["paths"]["expected_file"]
    candidate_path = project_root / settings["paths"]["output_dir"] / "candidate_accl_os.h"
    prompt_path = project_root / "skills" / "cccl-to-accl-rewrite" / "prompts" / "rewrite_prompt.md"

    if not source_path.exists():
        raise FileNotFoundError(f"找不到原始输入文件: {source_path}")
    if not expected_path.exists():
        raise FileNotFoundError(f"找不到参考目标文件: {expected_path}")
    if not candidate_path.exists():
        raise FileNotFoundError(f"找不到规则生成的候选文件: {candidate_path}")

    source_text = source_path.read_text(encoding="utf-8")
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

    output_dir = project_root / settings["paths"]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    final_file_path = output_dir / "final_accl_os.h"
    notes_path = output_dir / "rewrite_notes.md"
    raw_output_path = output_dir / "rewrite_raw_output.md"

    final_file_path.write_text(final_file_text, encoding="utf-8")
    notes_path.write_text(rewrite_notes, encoding="utf-8")
    raw_output_path.write_text(model_output, encoding="utf-8")

    print(f"最终目标文件已保存到: {final_file_path}")
    print(f"改写说明已保存到: {notes_path}")
    print(f"原始模型输出已保存到: {raw_output_path}")


if __name__ == "__main__":
    main()