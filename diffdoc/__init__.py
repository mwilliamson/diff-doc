from . import parser, rst


def compile(source_text):
    source = parser.loads(source_text)

    output = _transform_blocks(source)

    return rst.dumps(output)


def _transform_blocks(source):
    return source
