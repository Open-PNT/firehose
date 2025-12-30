#!/usr/bin/env python3

import os
import sys
import subprocess
import tempfile
from shutil import rmtree


def compile_c_files(directory):
    # Create the temporary folder if it doesn't exist
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    successes = 0
    failures = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.c'):
                file_path = os.path.join(root, file)
                object_file = os.path.join(
                    temp_dir, os.path.splitext(file)[0] + '.o'
                )
                print(f"Compiling {file}...")
                passed = subprocess.run(
                    [
                        'gcc',
                        '-std=c89',
                        '-O3',
                        '-Wall',
                        '-Werror',
                        '-pedantic',
                        '-c',
                        file_path,
                        '-o',
                        object_file,
                    ]
                ).returncode
                if passed == 0:
                    print(f"{file} compiles: ✅\n")
                    successes += 1
                else:
                    failures.append(file)

    rmtree(temp_dir)

    total_pounds = 80

    if len(failures) == 0:
        succ_msg = "All files compiled successfully!"
        surround_pounds = "#" * ((total_pounds - len(succ_msg) - 2) // 2)
        print("\n" + "#" * total_pounds)
        print(f"{surround_pounds} {succ_msg} {surround_pounds}")
    else:
        for failure in failures:
            print(f"❌ {failure} failed")
        fail_msg = f"{len(failures)}/{successes} files did NOT compile"
        surround_pounds = "#" * ((total_pounds - len(fail_msg) - 2) // 2)
        print("\n" + "#" * total_pounds)
        print(f"{surround_pounds} {fail_msg} {surround_pounds}")

    print("#" * total_pounds + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: test_c.py <source_directory>")
        sys.exit(1)

    directory = sys.argv[1]

    compile_c_files(directory)
