from importlib import import_module

from traceback import format_exc

import syst.tools.getfiles as gf    # I don't have it
from syst.tools.output import println


# load modules
modules = gf.from_folder('modules/')

for module in modules:
    module_name = module[:-3]   # remove .py extension

    try:
        import_module('modules.' + module_name)

        println('INIT-MODULE:' + module_name, 'Loaded')
    except Exception as exc:
        print(format_exc())
        println('INIT-MODULE:' + module_name, 'Failed: ' + str(exc))


# init wrappers
wrappers = gf.from_folder('wrappers/')

for wrapper in wrappers:
    wrapper_name = wrapper[:-3]

    try:
        import_module('wrappers.' + wrapper_name).init()

        println('INIT-WRAPPER:' + wrapper_name, 'Loaded')
    except Exception as exc:
        println('INIT-WRAPPER:' + wrapper_name, 'Failed: ' + str(exc))
