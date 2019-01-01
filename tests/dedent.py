import textwrap


def dedent(value):
    lines = textwrap.dedent(value).splitlines(keepends=True)
    assert lines[0].strip() == ""
    return "".join(lines[1:-1]) + lines[-1].rstrip("\r\n")
