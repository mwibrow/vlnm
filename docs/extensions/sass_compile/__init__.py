"""
    Sphinx Interface
    ~~~~~~~~~~~~~~~~

"""

import os

import sass


def run_sass(app, _exception):
    """Setup sass."""
    configs = app.config.sass_configs
    for config in configs.values():
        compile_sass_config(app, config)


def compile_sass_config(app, config):
    """Compile sass for a particular configuration."""
    build_dir = app.outdir
    static_dir = app.config.html_static_path[0]
    output = os.path.join(build_dir, static_dir, config['output'])

    compile_sass(
        config['entry'],
        output,
        config.get('compile_options', {}),
        config.get('variables', {}))


def compile_sass(entry, output, compile_options, sass_vars):
    """Compile sass."""
    os.makedirs(os.path.dirname(output), exist_ok=True)

    sass_vars = ['${}:{};'.format(var, val) for var, val in sass_vars.items()]
    header = '\n'.join(sass_vars)
    with open(entry, 'r') as file_in:
        source = header + '\n' + file_in.read()

    if source.strip():
        compile_options.pop('filename', None)
        compile_options.pop('dirname', None)
        compile_options.pop('string', None)
        include_paths = [os.path.dirname(entry)]
        include_paths.extend(compile_options.pop('include_paths', []))
        css = sass.compile(
            string=source,
            include_paths=include_paths,
            **compile_options)
    else:
        css = ''

    if css:
        with open(output, 'w') as file_out:
            file_out.write(css)


def setup(app):
    """Setup the app."""
    app.add_config_value('sass_configs', {}, 'env')
    app.connect('build-finished', run_sass)
