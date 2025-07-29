# **Firehose - Environment Setup**

> [!NOTE]
> If developing with ASPN-ROS, see
> [Generate ROS Ubuntu Development Packages via Docker](https://git.aspn.us/pntos/firehose/-/tree/feature/aspn-ros?ref_type=heads#generate-ros-ubuntu-development-packages-via-docker).

## **Option 1:** VS Code with Dev Containers extension

A container exists in the docker folder to assist with code generation and
library building. If you are using VS Code, install the Microsoft "Dev
Containers" extension and it should prompt you to build and run in the
container, which has all dependencies already installed.

### **SSH keys**

In order to use SSH over git, the SSH keys need to be forwarded to the
container. The VS Code DevContainer extension will forward the current SSH
agent session automatically. As long as your keys are loaded into the agent,
they should be accessible by the container. Many OSes start `ssh-agent`
automatically.

To test whether your SSH keys are loaded on a Linux host, do the following:

```sh
ssh-add -l
```

You should see a result list with at least 1 entry. Something like this:
```bash
2048 SHA256:abc123abc123abc123abc123abc123abc123abc1 user@host (RSA)
256 SHA256:def456def456def456def456def456def456def4 user@host (ECDSA)
521 SHA256:ghi789ghi789ghi789ghi789ghi789ghi789ghi7 user@host (ED25519)
```

### **Troubleshooting**
---

```
Error connecting to agent: No such file or directory
```
The SSH agent is not running. See documentation for your operating system for
the expected way to start an SSH agent.

```
The agent has no identities.
```
No SSH keys are loaded. One way to load them on Linux is simply:
```sh
ssh-add
```

You will be prompted for your SSH passphrase. Once that is successful,
`ssh-add -l` will list your key(s). Now they should be accessible in the
container as well. A container rebuild may be needed.

## **Option 2:** Use Docker manually

An alternate way to use Docker is to build your own container manually with
the file `docker/Dockerfile`.

In Linux you would do the following **from the root of the firehose repo**
```bash
docker build -f docker/Dockerfile -t firehose-codegen docker
```

Now you should have an image called `firehose-codegen` available for use.

Again, from the root of the firehose repo, use the following command to
2-way-bind the firehose repo on your host machine to an `firehose-codegen`
container.

We will also enable ssh-agent forwarding from the host system so that you can
use git over ssh inside of the container. See the "SSH Keys" section under
**Option 1** above.

```bash
docker run \
    --privileged \
    -it \
    -e SSH_AUTH_SOCK=/ssh-agent \
    -e GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" \
    -v "$SSH_AUTH_SOCK:/ssh-agent" \
    -v "$HOME/.ssh:/root/.ssh" \
    -v $(pwd):/firehose firehose-codegen \
    bash
```

This will put you in the working directory of the docker image, which is
`/firehose`.

## **Option 3:** Use bare metal (at your own risk)

Install the packages from `docker/Dockerfile` on your operating system,
modifying as necessary if you aren't using the Ubuntu LTS version in the
`firehose-codegen` image. This is brittle and **not recommended** as
dependencies from elsewhere could cause some hard-to-find bugs.

# **Code Generation [`generate.py`]**

Use the convenience wrapper script `generate.py` in the root directory to
easily build, generate, and stage outputs all at once.

```
python3 generate.py --help

usage: generate.py [-h] [--aspn-icd-dir] [--extra-icd-files-dir] [-b] [-o] [-s] [-a] [--list-targets] [--targets [...]] [--interactive]

Convenience script for generating code from ASPN ICD files and optionally staging the output for use in firehose-outputs

options:
  -h, --help                show this help message and exit

  -a, --all                 Generate all output formats

  -b , --build-dir          Build directory. Defaults to $PWD/build

  -o , --output-dir         Directory to place generated output files.
                            Defaults to [build_dir]/output
  -s , --staging-input-dir  Staging directory containing any additional non-generated
                            files to push to firehose-outputs. Defaults to $PWD/staging

  --aspn-icd-dir            Directory containing input Aspn YAML files for generation.
                            Defaults to $PWD/subprojects/aspn-icd-release-2023
  --extra-icd-files-dir     Directory containing any additional input Aspn YAML files
                            for generation. Defaults to None

  --interactive             Interactive mode to select output formats

  --list-targets            Show a list of all available targets to generate

  --targets [ ...]          List of specific targets to generate.
                            Alternatively use --interactive to select one by one
```

Some examples of how to use the script for various scenarios follow:

## **Interactive mode**

A good place to start familiarizing yourself is to use the interactive mode.

If you don't specify any `--targets` or `--all`, you will be automatically put
into `--interactive` mode.

This will hold your hand through all of the parameters and allow you to pick
and choose what codegen output you want.

```bash
python3 generate.py
```

## **Default settings**

```bash
python3 generate.py --all
```
This is equivalent to running:
```bash
python3 generate.py \
    --aspn-icd-dir ./subprojects/aspn-icd-release-2023 \
    --build-dir ./build \
    --output-dir ./build/output \
    --staging-input-dir ./build/staging \
    --targets \
        aspn_c \
        aspn_dds_idl \
        aspn_dds_cpp \
        aspn_cpp \
        aspn_lcm \
        aspn_py \
        aspn_lcm_translations \
        aspn_c_marshaling \
        aspn_ros \
        aspn_ros_translations
```

## **Custom ASPN ICD directory**

```bash
python3 generate.py --aspn-icd-dir /some/path/to/custom/dir --targets aspn_cpp
```
This will look for all `*.yaml` files inside of `/some/path/to/custom/dir` and
generate only the c++ output for the files in your custom ASPN ICD directory.

## **Extending/Adding ASPN messages**

If you still want to generate the full normal suite of Aspn messages, but just
want to **add** your own custom extension messages, simply put the YAML files
for the extension messages in their own directory or directories like so:
```bash
python3 generate.py --extra-icd-files-dir /path/to/custom_yamls --targets aspn_cpp aspn_c aspn_py
```
This will look for all `*.yaml` files inside of `dir1` and `dir2` and generate
all of the standard ASPN C/C++ and python code, along with your extension
messages.

All output (including all files in `./staging`) will still be placed in the
default output directory `./build/output`

## **Adding custom ASPN messages to repo that uses firehose-outputs**
If you'd like to add your own custom messages you can follow the example below, substituting values
when necessary.

### **Assumptions**
- Your CWD is the firehose root.
- All YAML files for the messages that you'd like to add or overwrite are in `./custom_messages`.
- You have downstream project checked out at `../<project>`.

### **Steps**
1.   Generate the new firehose-outputs locally the steps above. For example:
     ```bash
     python3 generate.py -b ./build -o ./build/output --extra-icd-files-dir ./custom_messages --all
      ```
2.  Copy the new outputs over the existing ones in the `firehose-outputs` subproject in the
    downstream project.
    ```bash
    cp -r ./build/output/* ../<project>/subprojects/firehose-outputs/
    ```
3.  Rebuild the downstream project and the new custom messages should be available.

**Note-** Once you are satisfied with the results after testing, if you have
push rights for `firehose`, you can create a new branch and point at the
proper aspn-icd branch with your custom messages on it. Then wait for the CI
to build the subsequent `firehose-outputs` branch and point the
`firehose-outputs.wrap` `revision` to that new commit in the project.

# Building ASPN-ROS

## Explanation

In the main container, the `aspn_ros` subdirectory is created in the output
directory by `generate.py` (see below). It is populated with auto-generated
ROS `.msg` files and staged Python ROS packages. To actually use these,
however, they must be built by `colcon`, ROS's build tool (even though it's
mostly Python, ROS's messaging system requires C extensions). Often, this will
be done by the user (targeting their specific platform). For example,
`smartcables` does this in a ROS Docker container.

## Using CI's ASPN-ROS Ubuntu x86 development packages (easiest)

To ease Python development, however, the CI also automatically builds our ROS
packages for use with Ubuntu 22.04 (ROS Humble) and 24.04 (ROS Jazzy) on x86
machines. Due to the complexity of the ROS build system, the builds occur in
isolated Docker containers. These invoke `colcon build` on the stuff in
`[output-dir]/aspn-ros` and generate installable ROS packages under
`[output-dir]/ros_devel/humble` and `[output-dir]/ros_devel/jazzy`. To use
them (whether inside or outside of a Docker container), simply `source
firehose-outputs/ros_devel/humble/setup.bash`, for example (source whichever
one matches your shell; sourcing `setup.sh` from `bash` will fail).

## Building with Docker

If you want ASPN-ROS and aren't using Ubuntu on x86, you'll need to build it
yourself. You can use the same Docker container that the CI uses.

> [!WARNING]
> Before you run a ROS Docker container, make sure you've already run the main
> Docker container (see above), which generated the `[output-dir]/aspn-ros`
> folder. In particular, you'll need to have built targets `aspn_ros` and
> `aspn_ros_translations` (i.e. `python3 generate.py --targets aspn_ros
> aspn_ros_translations` or `python3 generate.py -a`).

To manually build one of these ROS containers, do
```bash
docker build -t firehose-ros:humble --build-arg ROS_DISTRO=humble -f docker/Dockerfile.ros docker
```
or
```bash
docker build -t firehose-ros:jazzy --build-arg ROS_DISTRO=jazzy -f docker/Dockerfile.ros docker
```

To run it (which builds the ROS stuff; this can take several minutes), do
```bash
docker run -it -v $(pwd)/build/output:/output firehose-ros:humble
```
or
```bash
docker run -it -v $(pwd)/build/output:/output firehose-ros:jazzy
```

Now the `[output-dir]/ros_devel/humble` or `[output-dir]/ros_devel/jazzy`
directory should exist, and its `setup.*` files can be sourced. If you're
trying to *use* ASPN-ROS within a Docker container with ROS (on a non-Ubuntu
system, for example), the directory can be copied into the container before
sourcing.

## Building manually without Docker

> [!WARNING]
> To run `colcon build`, you must either not use a virtual environment, or
> create it with `--system-site-packages` (e.g., `uv venv
> --system-site-packages` or `python3 -m venv .venv --system-site-packages`.
> Otherwise, ROS won't be able to find its Python dependencies installed to the
> system, and you'll get an error.

If you have ROS (including `colcon`) installed locally (see [Humble
Installation Guide](https://docs.ros.org/en/humble/Installation.html) or
[Jazzy Installation Guide](https://docs.ros.org/en/jazzy/Installation.html)),
you can build ASPN-ROS directly. First, make sure the ROS environment is
sourced:

```bash
source /opt/ros/[humble/jazzy]/setup.[sh/bash/zsh]
```

Now, either run the main container (see above) or clone `firehose-outputs`.
Then:

```bash
cd [output-dir]/aspn-ros
colcon build
```

This will create an `install/` directory in the current directory with setup
files. To activate the ASPN-ROS environment, `source
install/setup.[sh/bash/zsh]`.
