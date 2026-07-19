cmake_minimum_required(VERSION 3.16)

project(lab3_simple_llvm_compiler LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# LLVM 21 on some systems exports a dependency on zstd::libzstd_shared, but the
# distro package may install only the runtime libzstd.so.1 without zstd's CMake
# package files. Define the imported target ourselves before loading LLVM.
find_library(ZSTD_RUNTIME_LIBRARY NAMES zstd libzstd.so.1)
if(ZSTD_RUNTIME_LIBRARY AND NOT TARGET zstd::libzstd_shared)
    add_library(zstd::libzstd_shared UNKNOWN IMPORTED)
    set_target_properties(zstd::libzstd_shared PROPERTIES
        IMPORTED_LOCATION "${ZSTD_RUNTIME_LIBRARY}"
    )
endif()

find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

add_executable(lab3 src/main.cpp)

target_include_directories(lab3 PRIVATE ${LLVM_INCLUDE_DIRS})
target_compile_options(lab3 PRIVATE ${LLVM_DEFINITIONS} -fexceptions -Wno-unused-parameter)

llvm_map_components_to_libnames(LLVM_LIBS Core Support)
target_link_libraries(lab3 PRIVATE ${LLVM_LIBS})
