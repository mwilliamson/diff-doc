import argparse

from . import compile, convert_block


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


class ConvertBlockCommand(object):
    name = "convert-block"

    def add_arguments(self, parser):
        parser.add_argument("source")
        parser.add_argument("line_number", metavar="line-number", type=int)
        parser.add_argument("block_type", metavar="block-type")

    def execute(self, args):
        with open(args.source, "rt", encoding="utf-8") as source_fileobj:
            source = source_fileobj.read()

        output = convert_block(
            source_text=source,
            line_number=args.line_number,
            block_type=args.block_type,
        )

        with open(args.source, "wt", encoding="utf-8") as source_fileobj:
            source_fileobj.write(output)


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for command in (
        CompileCommand(),
        ConvertBlockCommand(),
    ):
        subparser = subparsers.add_parser(command.name)
        command.add_arguments(subparser)
        subparser.set_defaults(execute=command.execute)

    return parser.parse_args()
