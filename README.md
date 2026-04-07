# CCCL → ACCL Migration Prototype

## 1. 项目简介
本项目是一个面向华为昇腾代码迁移场景的原型工程，目标是辅助完成 **CCCL 文件到 ACCL 文件** 的迁移，并在目标仓库中完成编译验证。

当前第一版（MVP）聚焦于：

- 仅支持 `os.h`
- 输入 CCCL `os.h`
- 输出候选 ACCL `os.h`
- 将结果写入 `mylearn` 指定位置
- 在 host 环境下执行编译验证
- 最多进行一次修复循环

---

## 2. 当前结构
当前原型采用：

- 一个主流程（orchestrator）
- 两个 Skill

### Skill 1：`cccl-to-accl-rewrite`
负责：
- 读取 CCCL `os.h`
- 应用迁移规则
- 生成候选 ACCL `os.h`
- 输出改写说明

### Skill 2：`accl-compile-fix`
负责：
- 将候选 ACCL 文件写入 `mylearn`
- 调用 host 编译脚本
- 收集编译日志
- 在失败时执行一次修复循环

---

## 3. 当前目录结构

```text
cccl-to-accl/
├── README.md
├── .env
├── main.py
├── config/
│   └── settings.yaml
├── skills/
│   ├── cccl-to-accl-rewrite/
│   │   ├── SKILL.md
│   │   ├── prompts/
│   │   │   └── rewrite_prompt.md
│   │   └── rules/
│   │       └── os_h_rules.yaml
│   └── accl-compile-fix/
│       ├── SKILL.md
│       └── prompts/
│           └── compile_fix_prompt.md
├── scripts/
│   ├── apply_rules.py
│   ├── static_check.py
│   ├── compile_runner.py
│   ├── parse_build_log.py
│   └── format_report.py
├── examples/
│   ├── input_cccl_os.h
│   ├── expected_accl_os.h
│   └── sample_report.md
└── outputs/
```

---

## 4. 当前版本范围
当前版本仅用于验证流程可行性，主要限制包括：

- 仅支持 `os.h`
- 仅支持固定目标路径
- 仅支持 host 编译验证
- 仅支持一次修复循环
- 不支持多文件迁移
- 不支持仓库级批量处理

---

## 5. 配置文件说明
核心配置文件位于：

```text
config/settings.yaml
```

当前配置主要包括以下内容：

- 项目名称与模式
- `mylearn` 仓库路径
- 输入样例路径
- 参考目标文件路径
- 固定目标输出相对路径
- host 编译模式
- 编译环境名称
- 编译脚本名称
- 最大修复轮数
- 模型提供方与模型名称

---

## 6. 当前样例文件
当前原型使用以下样例文件：

### 输入样例
```text
examples/input_cccl_os.h
```

该文件用于存放原始 CCCL `os.h`。

### 参考目标样例
```text
examples/expected_accl_os.h
```

该文件用于存放已经人工改写并成功编译通过的 ACCL `os.h`，作为第一版规则设计和结果对照的参考。

### 示例报告
```text
examples/sample_report.md
```

该文件用于后续放置示例迁移报告。

---

## 7. 运行环境
当前原型涉及两个环境：

### 1）原型运行环境
用于运行原型项目本身，例如：

- `main.py`
- 规则改写脚本
- 模型调用
- 报告输出

当前使用的环境为：

```text
accl_skill
```

### 2）目标仓库编译环境
用于在 `mylearn` 中执行 host 编译验证。

当前使用的环境为：

```text
asc_cccl_env
```

说明：
- 原型项目运行在 `accl_skill`
- 编译验证运行在 `asc_cccl_env`
- 二者分离，后续通过脚本进行协调

---

## 8. 当前 host 编译验证方式
第一版原型后续将通过 `mylearn` 中已有脚本完成 host 编译验证，当前约定流程为：

1. 激活 `asc_cccl_env`
2. 进入 `mylearn/libascendcxx`
3. 执行 `000_set_env.sh`
4. 执行 `002_only_make_host.sh`

当前版本只验证 host 编译，不做 kernel 或全量项目验证。

---

## 9. 当前状态
当前已经完成：

- 项目目录搭建
- `settings.yaml` 配置文件
- 两个 Skill 的基础定义
- 输入/输出样例文件准备

接下来将进入：

- `os.h` 规则改写实现
- 静态检查实现
- 编译验证流程接入

---

## 10. 后续实现路线
后续开发将按照以下顺序推进：

1. 实现 `os.h` 的规则改写
2. 生成候选 ACCL `os.h`
3. 对候选文件进行静态检查
4. 将候选文件写入 `mylearn` 指定路径
5. 调用 host 编译脚本进行验证
6. 若失败，则根据日志进行一次修复循环
7. 输出最终结果与报告

---

## 11. 当前版本结论
当前项目已经完成原型第一阶段的结构搭建，明确了：

- 目标场景
- MVP 范围
- Skill 划分
- 配置文件
- 输入输出样例
- 后续实现路径

后续将从 `os.h` 的规则改写开始，逐步实现完整的：

**输入 CCCL 文件 → 输出 ACCL 文件 → 写入目标仓库 → 编译验证 → 一次修复循环**

流程原型。