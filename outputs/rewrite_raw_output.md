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
#  define _ACCL_OS_WINDOWS_() 1
#else
#  define _ACCL_OS_WINDOWS_() 0
#endif

#if defined(__linux__) || defined(__LP64__) /* __LP64__ for NVRTC */
#  define _ACCL_OS_LINUX_() 1
#else
#  define _ACCL_OS_LINUX_() 0
#endif

#if defined(__ANDROID__)
#  define _ACCL_OS_ANDROID_() 1
#else
#  define _ACCL_OS_ANDROID_() 0
#endif

#if defined(__QNX__) || defined(__QNXNTO__)
#  define _ACCL_OS_QNX_() 1
#else
#  define _ACCL_OS_QNX_() 0
#endif

#if defined(__APPLE__) || defined(__APPLE_CC__)
#  define _ACCL_OS_APPLE_() 1
#else
#  define _ACCL_OS_APPLE_() 0
#endif

#if defined(__OHOS__) || defined(__OPENHARMONY__)
#  define _ACCL_OS_HARMONY_() 1
#else
#  define _ACCL_OS_HARMONY_() 0
#endif

#define _ACCL_OS(...) _ACCL_OS_##__VA_ARGS__##_()

#endif  // LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_

【改写说明】
1. 修正了注释描述：将参考文件中从原始文件错误继承的 "host architecture" 修正为 "host OS"，因为该文件实际功能是判断操作系统而非架构。
2. 修正了头文件保护符：参考文件结尾的 `#endif` 注释中少了一个下划线（`STD__ACCL` vs `STD___ACCL`），已修正为与开头 `#ifndef` 保持一致。
3. 调整了宏定义顺序：保持与候选文件一致的逻辑顺序，将新增的 `_ACCL_OS_HARMONY` 放置在最后，符合扩展习惯，同时保留了原始文件中的缩进风格。
4. 保留了 ACCL 风格的版权声明和 `_ACCL_` 前缀命名规范。