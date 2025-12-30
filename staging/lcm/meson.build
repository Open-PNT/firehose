if not get_option('lcm-generated-c').disabled() or not get_option('lcm-generated-cpp').disabled()
    required_lcm_version = '>=1.3.1'
    lcm_dep = dependency('lcm',
                            version: required_lcm_version,
                            required: false,
                            allow_fallback: false)

    # LCM doesn't reliably ship with a pkg-config file. Check whether an
    # appropriate version is in the default header/library path.
    if not lcm_dep.found()
        c_compiler = meson.get_compiler('c')
        if c_compiler.has_header('lcm/lcm.h')
            prefix = '#include <lcm/lcm.h>'
            lcm_major = c_compiler.get_define('LCM_MAJOR_VERSION', prefix: prefix)
            lcm_minor = c_compiler.get_define('LCM_MINOR_VERSION', prefix: prefix)
            lcm_micro = c_compiler.get_define('LCM_MICRO_VERSION', prefix: prefix)
            lcm_version = lcm_major + '.' + lcm_minor + '.' + lcm_micro
            if lcm_version.contains('..')
                error('lcm.h is missing LCM_*_VERSION defs')
            elif not lcm_version.version_compare(required_lcm_version)
                error('lcm version ' + lcm_version + ' is not ' +
                        required_lcm_version)
            else
                lcm_dep = c_compiler.find_library('lcm')
            endif
        endif
    endif

    if not lcm_dep.found()
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

        if lcm_subproj.found()
            lcm_dep = lcm_subproj.dependency('lcm')
        else
            error('lcm library not found')
        endif
    endif
endif

if not get_option('lcm-generated-c').disabled()
    subdir('c')
endif

if not get_option('lcm-generated-cpp').disabled()
    subdir('cpp')
endif
