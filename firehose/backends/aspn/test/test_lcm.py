#!/usr/bin/env python3

import os
import sys
import subprocess
from os.path import join


def generate_lcm_input_files(meson_dir):
    subprocess.run(
        ['ninja', 'generate_aspn_lcm'], shell=True, check=True, cwd=meson_dir
    )


# def generate_lcm_output_files(directory, temp_folder):
#     # Create the temporary folder if it doesn't exist
#     c_tmp_dir = join(temp_folder, 'aspn-lcm-c')
#     cpp_tmp_dir = join(temp_folder, 'aspn-lcm-cpp')
#     for d in [c_tmp_dir, cpp_tmp_dir]:
#         os.makedirs(d, exist_ok=True)

#     c_args = ['-c', '--c-cpath', c_tmp_dir, '--c-hpath', c_tmp_dir]
#     c_args = []
#     cpp_args = ['-cpp', '--cpp-hpath', cpp_tmp_dir]

#     successes = 0
#     failures = []

#     for root, _, files in os.walk(directory):
#         for file in files:
#             if file.endswith('.lcm'):
#                 file_path = os.path.join(root, file)
#                 print(f"Generating LCM from file {file}...")
#                 cmd = ['lcm-gen'] + [file_path] + c_args + cpp_args
#                 passed = subprocess.run(cmd).returncode
#                 if passed == 0:
#                     print(f"{file} generates LCM: ✅\n")
#                     successes += 1
#                 else:
#                     failures.append(file)

#     # # Delete the .o files
#     # for file in os.listdir(temp_folder):
#     #     if file.endswith('.o'):
#     #         file_path = os.path.join(temp_folder, file)
#     #         os.remove(file_path)

#     total_pounds = 80

#     if len(failures) == 0:
#         succ_msg = "All files generated successfully!"
#         surround_pounds = "#" * ((total_pounds - len(succ_msg) - 2) // 2)
#         print("\n" + "#" * total_pounds)
#         print(f"{surround_pounds} {succ_msg} {surround_pounds}")
#     else:
#         for failure in failures:
#             print(f"❌ {failure} failed")
#         fail_msg = f"{len(failures)}/{successes + len(failures)} files did NOT generate"
#         surround_pounds = "#" * ((total_pounds - len(fail_msg) - 2) // 2)
#         print("\n" + "#" * total_pounds)
#         print(f"{surround_pounds} {fail_msg} {surround_pounds}")

#     print("#" * total_pounds + "\n")


def generate_lcm_output_files(directory, temp_folder):
    print("Generating LCM ...")

    C_PATH = join(directory, 'lcm-c')
    CPP_PATH = join(directory, 'lcm-cpp')
    CSHARP_PATH = join(directory, 'lcm-cs')
    JAVA_PATH = join(directory, 'lcm-java')
    LUA_PATH = join(directory, 'lcm-lua')
    PY_PATH = join(directory, 'lcm-py')

    OUTPUT_DIRS = [C_PATH, CSHARP_PATH, CPP_PATH, JAVA_PATH, PY_PATH, LUA_PATH]

    lcm_gen_command = [
        "lcm-gen",
        join(directory, '*.lcm'),
        "--c",
        "--csharp",
        "--cpp",
        "--java",
        "--lua",
        "--python",
        "--c-cpath",
        C_PATH,
        "--c-hpath",
        C_PATH,
        "--csharp-path",
        CSHARP_PATH,
        "--cpp-hpath",
        CPP_PATH,
        "--jpath",
        JAVA_PATH,
        "--lpath",
        LUA_PATH,
        "--ppath",
        PY_PATH,
    ]

    print("Running the following command:")
    print(' '.join(lcm_gen_command))

    for output_dir in OUTPUT_DIRS:
        if os.path.isdir(output_dir):
            os.rmdir(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    # File expansion isn't working in subprocess, so using os.system :/
    # passed = subprocess.run(lcm_gen_command, shell=True).returncode
    passed = os.system(' '.join(lcm_gen_command))

    total_pounds = 80

    if passed == 0:
        succ_msg = "✅ All files generated successfully!"
        surround_pounds = "#" * ((total_pounds - len(succ_msg) - 2) // 2)
        print("\n" + "#" * total_pounds)
        print(f"{surround_pounds} {succ_msg} {surround_pounds}")
    else:
        fail_msg = "LCM generation FAILED"
        surround_pounds = "#" * ((total_pounds - len(fail_msg) - 2) // 2)
        print("\n" + "#" * total_pounds)
        print(f"{surround_pounds} {fail_msg} {surround_pounds}")

    print("#" * total_pounds + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: test_lcm.py <meson_build_dir>")
        sys.exit(1)

    root_output_dir = sys.argv[1]

    lcm_inputs_dir = join(root_output_dir, 'aspn-lcm')
    lcm_outputs_dir = join(root_output_dir, 'aspn-lcm-gen')

    # generate_lcm_input_files(root_output_dir)
    generate_lcm_output_files(lcm_inputs_dir, lcm_outputs_dir)
