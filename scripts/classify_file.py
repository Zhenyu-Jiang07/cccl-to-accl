from pathlib import Path
from typing import Dict


def is_os_h_like(filename: str, text: str) -> bool:
    """
    判断文件是否属于 os.h 这一类配置/宏工具头。
    不只看文件名，也看内容特征。
    """
    os_name_hits = [
        filename == "os.h",
        filename.endswith("_os.h"),
        "os.h" in filename,
    ]

    os_content_hits = [
        "_cccl_os(" in text,
        "_cccl_os_" in text,
        "__cccl_os_h" in text,
        "_accl_os(" in text,
        "_accl_os_" in text,
        "determine the host os" in text,
        "determine the host architecture" in text,
    ]

    return any(os_name_hits) or any(os_content_hits)


def classify_file(file_path: str, content: str) -> Dict[str, str]:
    """
    对输入文件做一个轻量分类。
    当前只做第一版启发式分类，后续可以再增强。
    """
    path = Path(file_path)
    filename = path.name.lower()
    text = content.lower()

    # 1. 专项支持：os.h 及其样例/变体
    if is_os_h_like(filename, text):
        return {
            "file_type": "os_h",
            "category": "config_macro_header",
            "support_level": "full",
            "reason": "检测到 os.h 类配置/宏工具头特征，当前版本已支持该专项文件的完整迁移流程。",
        }

    # 2. traits / type utilities
    if (
        "is_" in filename
        or "make_" in filename
        or "__type_traits" in text
        or "type trait" in text
        or "integral_constant" in text
    ):
        return {
            "file_type": "traits_utility",
            "category": "type_traits_or_utility",
            "support_level": "analysis_only",
            "reason": "检测到 traits / 类型工具类特征，当前版本仅建议进入分析与候选改写阶段。",
        }

    # 3. algorithm / math-like utilities
    if (
        filename in {"neg.h", "ceil_div.h", "round_up.h", "round_down.h", "pow2.h", "ilog.h", "isqrt.h"}
        or "constexpr" in text
        or "nodiscard" in text
        or "__cccl_is_integer_v" in text
    ):
        return {
            "file_type": "algorithm_like_header",
            "category": "algorithm_or_small_impl",
            "support_level": "analysis_only",
            "reason": "检测到小型实现/算法类头文件特征，当前版本建议先进行候选改写，不直接进入仓库验证。",
        }

    # 4. 默认未知类型
    return {
        "file_type": "unknown",
        "category": "unknown",
        "support_level": "unsupported",
        "reason": "当前规则无法可靠识别该文件类型，暂不支持自动迁移。",
    }


if __name__ == "__main__":
    sample_path = "examples/input_cccl_os.h"
    text = Path(sample_path).read_text(encoding="utf-8")
    result = classify_file(sample_path, text)

    print("=== 分类结果 ===")
    for k, v in result.items():
        print(f"{k}: {v}")