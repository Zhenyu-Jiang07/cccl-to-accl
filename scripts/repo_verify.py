from pathlib import Path
from datetime import datetime
import subprocess
import yaml
import re


CONDA_SH = "/home/zhenyu/miniconda3/etc/profile.d/conda.sh"


def load_settings(settings_path: Path) -> dict:
    with settings_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_branch_name(prefix: str, filename: str) -> str:
    stem = Path(filename).stem
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stem}-{timestamp}"


def build_commit_message(template: str, filename: str) -> str:
    return template.format(filename=filename)


def run_bash_command(command: str, capture: bool = True):
    if capture:
        return subprocess.run(
            ["bash", "-lc", command],
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["bash", "-lc", command],
        text=True,
    )


def save_text(project_root: Path, filename: str, content: str) -> Path:
    output_dir = project_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def checkout_new_branch(settings: dict, branch_name: str):
    repo = settings["paths"]["mylearn_repo"]
    conda_env = settings["repo_verify"]["conda_env"]

    command = f"""
source "{CONDA_SH}"
conda activate {conda_env}
cd "{repo}"
git checkout -b "{branch_name}"
"""
    return run_bash_command(command, capture=True)


def write_target_file(project_root: Path, settings: dict) -> Path:
    mylearn_repo = Path(settings["paths"]["mylearn_repo"])
    target_relpath = Path(settings["paths"]["target_relpath"])
    source_generated_file = project_root / settings["paths"]["output_dir"] / "final_accl_os.h"

    if not source_generated_file.exists():
        raise FileNotFoundError(f"找不到生成文件: {source_generated_file}")

    target_file_path = mylearn_repo / target_relpath
    target_file_path.parent.mkdir(parents=True, exist_ok=True)

    content = source_generated_file.read_text(encoding="utf-8")
    target_file_path.write_text(content, encoding="utf-8")

    return target_file_path


def run_clang_format_on_target(settings: dict) -> subprocess.CompletedProcess:
    conda_env = settings["repo_verify"]["conda_env"]
    mylearn_repo = Path(settings["paths"]["mylearn_repo"])
    target_relpath = Path(settings["paths"]["target_relpath"])
    target_file = mylearn_repo / target_relpath

    command = f"""
source "{CONDA_SH}"
conda activate {conda_env}
clang-format-14 -i "{target_file}"
"""
    return run_bash_command(command, capture=True)


def git_add_and_commit(settings: dict, commit_message: str):
    repo = settings["paths"]["mylearn_repo"]
    conda_env = settings["repo_verify"]["conda_env"]

    command = f"""
source "{CONDA_SH}"
conda activate {conda_env}
cd "{repo}"
git add .
git commit -s -m "{commit_message}"
"""
    return run_bash_command(command, capture=True)


def check_commit_passed(commit_output: str) -> tuple[bool, bool]:
    license_passed = bool(
        re.search(r"Add Apache 2\.0 license header.*Passed", commit_output)
    )
    style_passed = bool(
        re.search(r"CANN code style check \(clang-format \+ cpplint\).*Passed", commit_output)
    )
    return license_passed, style_passed


def git_push(settings: dict, branch_name: str):
    repo = settings["paths"]["mylearn_repo"]
    conda_env = settings["repo_verify"]["conda_env"]
    remote = settings["repo_verify"]["push_remote"]

    command = f"""
source "{CONDA_SH}"
conda activate {conda_env}
cd "{repo}"
git push {remote} "{branch_name}"
"""
    # push 可能要求输入用户名/密码或 token，这里不捕获输出，让终端直接显示
    return run_bash_command(command, capture=False)


def main():
    project_root = Path(__file__).resolve().parent.parent
    settings = load_settings(project_root / "config" / "settings.yaml")

    target_filename = Path(settings["paths"]["target_relpath"]).name
    branch_name = build_branch_name(settings["repo_verify"]["branch_prefix"], target_filename)
    commit_message = build_commit_message(
        settings["repo_verify"]["commit_message_template"],
        target_filename,
    )

    print(f"准备创建分支: {branch_name}")
    branch_result = checkout_new_branch(settings, branch_name)

    branch_log = (branch_result.stdout or "") + "\n" + (branch_result.stderr or "")
    branch_log_path = save_text(project_root, "git_checkout.log", branch_log)

    if branch_result.returncode != 0:
        print("创建分支失败")
        print(f"checkout 日志已保存到: {branch_log_path}")
        print(branch_log)
        return

    print("分支创建成功")
    print(f"checkout 日志已保存到: {branch_log_path}")

    target_file_path = write_target_file(project_root, settings)
    print(f"已写入目标文件: {target_file_path}")

    format_result = run_clang_format_on_target(settings)
    format_log = (format_result.stdout or "") + "\n" + (format_result.stderr or "")
    format_log_path = save_text(project_root, "clang_format.log", format_log)

    print(f"clang-format 日志已保存到: {format_log_path}")

    if format_result.returncode != 0:
        print("clang-format 执行失败")
        print(format_log)
        return

    print("clang-format 执行成功")

    commit_result = git_add_and_commit(settings, commit_message)
    commit_log = (commit_result.stdout or "") + "\n" + (commit_result.stderr or "")
    commit_log_path = save_text(project_root, "git_commit.log", commit_log)

    print(f"commit 日志已保存到: {commit_log_path}")

    license_passed, style_passed = check_commit_passed(commit_log)
    print(f"Add Apache 2.0 license header Passed: {license_passed}")
    print(f"CANN code style check Passed: {style_passed}")

    if commit_result.returncode != 0:
        print("git commit 失败")
        print(commit_log)
        return

    if not (license_passed and style_passed):
        print("本地 hook 检查未全部通过，停止 push")
        return

    print("本地 hook 检查全部通过，开始 push...")
    push_result = git_push(settings, branch_name)

    push_status = "push success" if push_result.returncode == 0 else "push failed"
    push_status_path = save_text(
        project_root,
        "git_push_status.log",
        f"{push_status}: {branch_name}\n",
    )

    if push_result.returncode == 0:
        print(f"push 成功，分支已上传: {branch_name}")
    else:
        print(f"push 失败，分支名: {branch_name}")

    print(f"push 状态日志已保存到: {push_status_path}")


if __name__ == "__main__":
    main()