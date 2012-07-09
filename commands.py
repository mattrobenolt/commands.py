import os
import sys
from optparse import OptionParser, make_option


class CLI(object):
    @staticmethod
    def make_option(*args, **kwargs):
        return make_option(*args, **kwargs)

    def __init__(self, packages, argv=None):
        if not isinstance(packages, (list, tuple, set, frozenset)):
            packages = (packages,)

        if argv is None:
            argv = sys.argv
        self.argv = argv

        self.props = {}

        self._commands = dict()
        for package in packages:
            # Add the package directory to the sys path so we can import commands
            package = os.path.abspath(os.path.expanduser(package))
            sys.path.insert(0, package)
            files = os.listdir(package)
            # Reduce list to just *.py files
            pys = filter(lambda x: x.endswith('.py') and not x.startswith('_'), files)
            # Strip off all ending .py
            commands = map(lambda x: x[:-3], pys)

            # Now that we've determined the possible modules to be imported, we need
            # to import them specifically into local scope to be accessed via the package
            # at runtime
            for command in commands:
                module = __import__(command)
                module.__cli__ = self
                self._commands[command] = \
                    Command(
                        module=module,
                        main=module.main,
                        help=module.help,
                        doc=module.__doc__,
                    )

            # Clean up the path
            sys.path.remove(package)

        self.main()

    def main(self):
        usage = 'usage: %prog <command> <args>'
        parser = OptionParser(
            usage=usage,
            add_help_option=False,
            option_list=self.__class__.option_list
        )

        options, args = parser.parse_args(self.argv[1:])
        if len(self.argv) == 1:
            parser.print_help()
            self.usage()
            sys.exit(1)

        command = self.argv[1]
        if command in self._commands:
            self._commands[command].main(self.props)
            sys.exit(0)

        self.usage()
        sys.exit(1)

    def usage(self):
        usage = '\nAvailable commands:\n'
        sys.stdout.write(usage)
        for command in self._commands:
            sys.stdout.write('    %s\t%s\n' % (command, self._commands[command].doc))

    def __repr__(self):
        return u'<%s>' % self.__class__.__name__


class Command(object):
    def __init__(self, module, main, help, doc):
        self.module = module
        self.main = main
        self.help = help
        self.doc = doc

    def __repr__(self):
        return u'<Command: %s>' % self.doc
