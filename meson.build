project('firehose', 'cpp',
    version : '0.0.1',
    license : 'Apache 2.0',
    default_options : ['cpp_std=c++20']
)

firehose_root = meson.project_source_root()

# Add location of the firehose module to PYTHONPATH
firehose_env = environment()
firehose_env.append('PYTHONPATH', firehose_root)

cxxheaderparser_project = subproject('cxxheaderparser')

# Add location of the cxxheaderparser module to PYTHONPATH
cxxheaderparser_root = cxxheaderparser_project.get_variable('cxxheaderparser_root')
firehose_env.append('PYTHONPATH', cxxheaderparser_root)

subproject('fast-dds-gen')

# Could not find lcm installed, attempt to build subproject with cmake
cmake = import('cmake')
subproj_options = cmake.subproject_options()
subproj_options.append_compile_args('c', '-w') # Inhibit all warnings
# CMAKE_EXPORT_NO_PACKAGE_REGISTRY prevents CMake from adding the
# subproject build folder to the local package registry. This should
# prevent CMake from "discovering" the LCM build folder and should cause
# Meson to keep treating it like a subproject instead of a system library.
# LCM_ENABLE_JAVA will build allow building of lcm-spy, lcm-logplayer-gui;
# however it requires Java which we do not want to add as a dependency
# normally.
subproj_options.add_cmake_defines({
    'CMAKE_EXPORT_NO_PACKAGE_REGISTRY': true,
    'LCM_ENABLE_EXAMPLES': false,
    'LCM_ENABLE_GO': false,
    'LCM_ENABLE_JAVA': false,
    'LCM_ENABLE_LUA': false,
    'LCM_ENABLE_PYTHON': false,
    'LCM_ENABLE_TESTS': false,
})
lcm_subproj = cmake.subproject('lcm',
    options: subproj_options,
    required: false)


# Format python code
black_dep = find_program('black', required: false)
if black_dep.found()
    run_target('format', command: [black_dep,
                                '@CURRENT_SOURCE_DIR@',
                                '--skip-string-normalization',
                                '--skip-magic-trailing-comma',
                                '--line-length', '79'])
endif
