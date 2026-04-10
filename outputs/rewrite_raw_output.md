【目标文件内容】
/******************************************************************************
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


#ifndef LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_  // NOLINT(build/header_guard)
#define LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_

// The header provides the following macros to determine the host OS:
//
// _ACCL_OS(WINDOWS)
// _ACCL_OS(LINUX)
// _ACCL_OS(ANDROID)
// _ACCL_OS(QNX)
// _ACCL_OS(APPLE)
// _ACCL_OS(HARMONY)

// Determine the host OS
#if defined(_WIN32) || defined(_WIN64) /* _WIN64 for NVRTC */
#define _ACCL_OS_WINDOWS_() 1
#else
#define _ACCL_OS_WINDOWS_() 0
#endif

#if defined(__linux__) || defined(__LP64__) /* __LP64__ for NVRTC */
#define _ACCL_OS_LINUX_() 1
#else
#define _ACCL_OS_LINUX_() 0
#endif

#if defined(__ANDROID__)
#define _ACCL_OS_ANDROID_() 1
#else
#define _ACCL_OS_ANDROID_() 0
#endif

#if defined(__OHOS__) || defined(__OPENHARMONY__)
#define _ACCL_OS_HARMONY_() 1
#else
#define _ACCL_OS_HARMONY_() 0
#endif

#if defined(__QNX__) || defined(__QNXNTO__)
#define _ACCL_OS_QNX_() 1
#else
#define _ACCL_OS_QNX_() 0
#endif

#if defined(__APPLE__) || defined(__APPLE_CC__)
#define _ACCL_OS_APPLE_() 1
#else
#define _ACCL_OS_APPLE_() 0
#endif

#define _ACCL_OS(...) _ACCL_OS_##__VA_ARGS__##_()

#endif  // LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_

【改写说明】
1. **宏命名替换**：将所有 CCCL 风格的宏前缀 `_CCCL_OS` 替换为 ACCL 风格的 `_ACCL_OS`，包括内部判断宏（如 `_ACCL_OS_WINDOWS_`）和外部调用宏 `_ACCL_OS(...)`。
2. **新增 Harmony OS 支持**：根据 ACCL 项目需求，新增了 `_ACCL_OS_HARMONY_` 宏定义，检测 `__OHOS__` 或 `__OPENHARMONY__` 宏，以支持鸿蒙系统。
3. **修正注释错误**：原始文件和参考文件中注释写为 "determine the host architecture"（确定宿主架构），但实际代码逻辑是确定操作系统，已修正为 "determine the host OS"。
4. **修正头文件保护符**：参考文件中的 `#endif` 注释存在拼写错误（少了一个下划线），已修正为与 `#ifndef` 一致的 `LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_`。
5. **调整代码顺序**：参考参考文件的结构，将 Harmony OS 的定义移至 Android 定义之后，逻辑上更为紧凑（移动/嵌入式操作系统分组）。