from pathlib import Path
import re
import yaml


def load_rules(rule_path: Path) -> dict:
    with rule_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def replace_header_guard(text: str, old_guard: str, new_guard: str) -> str:
    text = text.replace(f"#ifndef {old_guard}", f"#ifndef {new_guard}  // NOLINT(build/header_guard)")
    text = text.replace(f"#define {old_guard}", f"#define {new_guard}")
    text = text.replace(f"#endif // {old_guard}", f"#endif  // {new_guard}")
    return text


def replace_macro_prefixes(text: str, rules: dict) -> str:
    for item in rules.get("macro_prefix_replacements", []):
        text = text.replace(item["from"], item["to"])
    return text


def apply_text_replacements(text: str, rules: dict) -> str:
    for item in rules.get("text_replacements", []):
        text = text.replace(item["from"], item["to"])
    return text


def insert_comment_lines(text: str, rules: dict) -> str:
    for item in rules.get("insert_after_lines", []):
        anchor = item["after"]
        content = item["content"]
        if anchor in text and content not in text:
            text = text.replace(anchor, f"{anchor}\n{content}")
    return text


def insert_harmony_block(text: str, rules: dict) -> str:
    harmony_block = rules.get("extra_blocks", {}).get("harmony_block")
    if not harmony_block:
        return text

    if "_ACCL_OS_HARMONY_()" in text:
        return text

    qnx_anchor = """#if defined(__QNX__) || defined(__QNXNTO__)
#define _ACCL_OS_QNX_() 1
#else
#define _ACCL_OS_QNX_() 0
#endif"""

    if qnx_anchor in text:
        text = text.replace(qnx_anchor, harmony_block.strip() + "\n\n" + qnx_anchor)

    return text


def normalize_format(text: str) -> str:
    text = re.sub(r"#\s{2,}define", "#define", text)
    text = re.sub(r"#\s{2,}else", "#else", text)
    text = re.sub(r"#\s{2,}endif", "#endif", text)
    return text


def replace_file_header(text: str) -> str:
    accl_header = """/******************************************************************************
 * Copyright (c) 2026 Xiong Shengwu Group at Wuhan University of Technology. All Rights Reserved.
 * Author: Zhenyu Jiang <2786369597@qq.com>
 * Create: 2026-01-23
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *****************************************************************************/
"""

    return re.sub(
        r"//===-+.*?//===-+==\n\n",
        accl_header + "\n",
        text,
        flags=re.DOTALL,
    )


def apply_os_h_rules(source_text: str, rules: dict) -> str:
    result = source_text

    result = replace_file_header(result)

    result = replace_header_guard(
        result,
        rules["header_guard"]["from"],
        rules["header_guard"]["to"],
    )

    result = replace_macro_prefixes(result, rules)
    result = apply_text_replacements(result, rules)
    result = insert_comment_lines(result, rules)
    result = insert_harmony_block(result, rules)
    result = normalize_format(result)

    return result


def main():
    project_root = Path(__file__).resolve().parent.parent
    source_path = project_root / "examples" / "input_cccl_os.h"
    rule_path = project_root / "skills" / "cccl-to-accl-rewrite" / "rules" / "os_h_rules.yaml"
    output_path = project_root / "outputs" / "candidate_accl_os.h"

    source_text = source_path.read_text(encoding="utf-8")
    rules = load_rules(rule_path)
    result = apply_os_h_rules(source_text, rules)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")

    print(f"候选文件已生成: {output_path}")


if __name__ == "__main__":
    main()