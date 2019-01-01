from . import compiler, parser, rst


def compile(source_text):
    source = parser.loads(source_text)
    output = compiler.compile(source)
    return rst.dumps(output)


def convert_block(source_text, line_number, block_type):
    source = parser.loads(source_text)
    output = compiler.convert_block(
        source=source,
        line_number=line_number,
        block_type=block_type,
    )
    return rst.dumps([element.to_rst() for element in output])
