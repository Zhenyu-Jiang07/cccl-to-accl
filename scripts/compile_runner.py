from pathlib import Path
import subprocess
import yaml


def load_settings(settings_path: Path) -> dict:
    with settings_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def run_host_build(settings: dict) -> tuple[int, str, str]:
    mylearn_repo = Path(settings["paths"]["mylearn_repo"])
    workdir = mylearn_repo / settings["build"]["workdir"]
    conda_env = settings["build"]["conda_env"]
    setup_script = settings["build"]["setup_script"]
    build_script = settings["build"]["build_script"]

    command = f"""
source ~/.bashrc
conda activate {conda_env}
cd "{workdir}"
bash "{setup_script}"
bash "{build_script}"
"""

    result = subprocess.run(
        ["bash", "-lc", command],
        capture_output=True,
        text=True,
    )

    return result.returncode, result.stdout, result.stderr


def save_build_logs(project_root: Path, stdout: str, stderr: str) -> tuple[Path, Path]:
    output_dir = project_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = output_dir / "build_stdout.log"
    stderr_path = output_dir / "build_stderr.log"

    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")

    return stdout_path, stderr_path


def main():
    project_root = Path(__file__).resolve().parent.parent
    settings = load_settings(project_root / "config" / "settings.yaml")

    target_file_path = write_target_file(project_root, settings)
    print(f"已写入目标文件: {target_file_path}")

    returncode, stdout, stderr = run_host_build(settings)
    stdout_path, stderr_path = save_build_logs(project_root, stdout, stderr)

    print(f"build stdout 日志已保存到: {stdout_path}")
    print(f"build stderr 日志已保存到: {stderr_path}")
    print(f"构建返回码: {returncode}")

    if returncode == 0:
        print("host 编译验证成功")
    else:
        print("host 编译验证失败")


if __name__ == "__main__":
    main()