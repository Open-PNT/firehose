import subprocess
import shutil
import os
from os.path import abspath, join, dirname
import sys
import uuid

FIREHOSE_ROOT = abspath(join(dirname(__file__), '..', '..', '..', '..'))
BUILD_DIR = join(FIREHOSE_ROOT, 'build')


def get_current_branch():
    result = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def stash_changes():
    unique_id = str(uuid.uuid4())
    stash_message = f"temp-stash-for-script-{unique_id}"
    result = subprocess.run(
        ['git', 'stash', 'push', '-u', '-m', stash_message],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    stash_output = result.stdout.strip()
    print(f"Stashed changes: {stash_output}")

    # Find the stash with the unique message
    result = subprocess.run(
        ['git', 'stash', 'list'], stdout=subprocess.PIPE, text=True, check=True
    )
    stashes = result.stdout.strip().split('\n')
    for stash in stashes:
        if stash_message in stash:
            stash_name = stash.split(':')[0]
            return stash_name
    print("Error: Stash not found after stashing.")
    return None


def pop_stash(stash_name):
    subprocess.run(['git', 'stash', 'pop', stash_name], check=True)


def generate_outputs(branch, temp_dir):
    subprocess.run(['git', 'checkout', branch], check=True)
    output_dir = join(BUILD_DIR, 'output')

    # Remove the old build directory
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)

    # Run generate.py and store outputs in the temporary directory
    subprocess.check_call(
        [
            'python',
            './generate.py',
            '--all',
            '--build-dir',
            BUILD_DIR,
            '--output-dir',
            output_dir,
        ],
        cwd=FIREHOSE_ROOT,
    )
    shutil.move(f'{output_dir}/', temp_dir)


def diffcheck_outputs_against_main(BUILD_DIR):
    current_branch = get_current_branch()

    temp_dir1 = abspath(join(BUILD_DIR, 'temp_outputs_main'))
    temp_dir2 = abspath(join(BUILD_DIR, f'temp_outputs_{current_branch}'))

    shutil.rmtree(temp_dir1, ignore_errors=True)
    shutil.rmtree(temp_dir2, ignore_errors=True)
    os.makedirs(temp_dir1, exist_ok=True)
    os.makedirs(temp_dir2, exist_ok=True)
    failed = False

    # Save the Git state
    stash_name = None
    try:
        # Stash any uncommitted changes and get the stash name
        stash_name = stash_changes()

        # Switch to 'main' branch and generate outputs
        generate_outputs('main', temp_dir1)

        # Switch back to the original branch and pop the stash
        subprocess.run(['git', 'checkout', current_branch], check=True)
        if stash_name:
            pop_stash(stash_name)
            stash_name = None  # Stash has been popped

        # Generate outputs on the current branch
        generate_outputs(current_branch, temp_dir2)
    except Exception as e:
        print("❌ An error occurred during processing.")
        print(e)
        failed = True
    finally:
        # Restore the Git state
        if stash_name:
            try:
                pop_stash(stash_name)
            except subprocess.CalledProcessError as e:
                print(f"Error popping stash: {e}")
        try:
            subprocess.run(['git', 'checkout', current_branch], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error checking out original branch: {e}")
        if failed:
            exit(-1)

    # Compare the outputs
    output = (
        subprocess.run(
            ['diff', '-ur', temp_dir1, temp_dir2],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        .stdout.strip()
        .split('\n')
    )

    if not output or (len(output) == 1 and not output[0]):
        print("\n\n✅ Success: No differences found!")
        exit(0)
    else:
        print(f"❌ Failure: {len(output)} differences found")
        exit(-1)


if __name__ == "__main__":
    if len(sys.argv) < 2 and not os.path.isdir(BUILD_DIR):
        print(
            f"Default build directory: '{BUILD_DIR}' does not exist.",
            "Pass in build dir as an argument if different from the default directory.",
        )
        exit(-1)
    else:
        if len(sys.argv) >= 2:
            BUILD_DIR = sys.argv[1]
        diffcheck_outputs_against_main(BUILD_DIR)
