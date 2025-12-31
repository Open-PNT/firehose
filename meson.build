project('firehose', 'cpp',
    version : '0.0.1',
    license : 'Apache 2.0',
    default_options : ['cpp_std=c++20']
)

firehose_root = meson.project_source_root()

# Add location of the firehose module to PYTHONPATH
firehose_env = environment()
firehose_env.append('PYTHONPATH', firehose_root)

subproject('fast-dds-gen')
