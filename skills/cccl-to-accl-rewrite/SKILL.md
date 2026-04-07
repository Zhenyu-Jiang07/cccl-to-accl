---
name: cccl-to-accl-rewrite
description: 将 CCCL 的 os.h 改写为 ACCL 风格的目标文件，并输出改写说明
---

# CCCL → ACCL Rewrite Skill

## 1. Skill 简介
本 Skill 面向华为昇腾代码迁移场景，负责将单个 CCCL 文件改写为对应的 ACCL 文件。

当前第一版仅聚焦于 `os.h` 的迁移，目标是基于规则和模型辅助，生成一个候选 ACCL `os.h` 文件，用于后续写入 `mylearn` 并执行 host 编译验证。

---

## 2. 第一版范围
当前版本仅支持：

- 单个 `os.h` 文件输入
- 从 CCCL `os.h` 到 ACCL `os.h` 的改写
- 输出候选目标文件内容
- 输出改写说明

当前版本暂不支持：

- 其他 CCCL 文件类型
- 多文件联动改写
- 仓库级批量迁移
- 直接自动修复编译错误

---

## 3. 输入
本 Skill 的输入包括：

- 原始 CCCL `os.h` 文件内容
- 目标输出相对路径
- 规则模板
- 可选的参考 ACCL `os.h` 文件内容

---

## 4. 输出
本 Skill 的输出包括：

- 候选 ACCL `os.h` 文件内容
- 改写说明
- 静态检查结果

---

## 5. 当前目标
当前版本的主要目标是：

**输入 CCCL `os.h` → 输出候选 ACCL `os.h`**

为后续编译验证 Skill 提供输入基础。