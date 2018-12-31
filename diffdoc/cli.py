import argparse

from . import compile


def main():
    args = _parse_args()
    args.execute(args)


class CompileCommand(object):
    name = "compile"

    def add_arguments(self, parser):
        parser.add_argument("source")

    def execute(self, args):
        with open(args.source, "rt", encoding="utf-8") as source_fileobj:
            source = source_fileobj.read()

        output = compile(source)

        print(output)


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for command in (
        CompileCommand(),
    ):
        subparser = subparsers.add_parser(command.name)
        command.add_arguments(subparser)
        subparser.set_defaults(execute=command.execute)

    return parser.parse_args()
