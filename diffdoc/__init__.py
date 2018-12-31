from . import compiler, parser, rst


def compile(source_text):
    source = parser.loads(source_text)
    output = compiler.compile(source)
    return rst.dumps(output)
