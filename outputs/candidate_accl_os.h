//===----------------------------------------------------------------------===//
//
// Part of libcu++, the C++ Standard Library for your entire system,
// under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES.
//
//===----------------------------------------------------------------------===//

#ifndef LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_  // NOLINT(build/header_guard)
#define LIBASCENDCXX_INCLUDE_ASCEND_STD___ACCL_OS_H_

// The header provides the following macros to determine the host architecture:
//
// _ACCL_OS(WINDOWS)
// _ACCL_OS(LINUX)
// _ACCL_OS(ANDROID)
// _ACCL_OS(QNX)
// _ACCL_OS(APPLE)
// _ACCL_OS(HARMONY)

// Determine the host compiler and its version
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
