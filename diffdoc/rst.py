class CodeBlock(object):
    def __init__(self, language, content):
        self.language = language
        self.content = content

    def dumps(self):
        return ".. code-block:: {}\n{}".format(self.language, _indent("\n" + self.content))


class LiteralBlock(object):
    def __init__(self, content):
        self.content = content

    def dumps(self):
        return "::\n{}".format(_indent("\n" + self.content))


class DiffdocBlock(object):
    def __init__(self, arguments, options, content):
        self.arguments = arguments
        self.options = options
        self.content = content

    def dumps(self):
        options = "".join(
            _indent("\n:{}: {}".format(option_name, option_value))
            for option_name, option_value in self.options.items()
        )
        if self.content:
            content = _indent("\n" + self.content)
        else:
            content = ""
        return ".. diff-doc:: {}{}\n{}".format(" ".join(self.arguments), options, content)


class Text(object):
    def __init__(self, text):
        self.text = text

    def dumps(self):
        return self.text


def dumps(elements):
    return "".join(element.dumps() for element in elements)


def loads(value):
    block_prefix = ".. diff-doc::"
    # TODO: handle other indentation
    result = []

    lines = value.splitlines(keepends=True)
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith(block_prefix):
            arguments = tuple(filter(None, map(
                lambda argument: argument.strip(),
                line[len(block_prefix):].split(" "),
            )))
            index += 1

            options = {}
            while index < len(lines) and _is_indented_line(lines[index]) and not _is_blank_line(lines[index]):
                key, value = _read_option(_unindent(lines[index]))
                assert key not in options
                options[key] = value
                index += 1

            last_block_line_index = index - 1
            while index < len(lines) and _is_blank_line(lines[index]):
                index += 1

            block_start_index = index
            while index < len(lines) and (_is_blank_line(lines[index]) or _is_indented_line(lines[index])):
                if _is_indented_line(lines[index]):
                    last_block_line_index = index
                index += 1

            index = last_block_line_index + 1
            content = "".join(map(
                lambda line: _unindent(line)    ,
                lines[block_start_index:last_block_line_index + 1],
            ))

            result.append(DiffdocBlock(
                arguments=arguments,
                options=options,
                content=content,
            ))
        else:
            result.append(Text(line))
            index += 1

    return result


def _read_option(text):
    key, value = text.split(" ", 1)
    assert key.startswith(":")
    assert key.endswith(":")
    return key[1:-1], value.strip()


def _is_blank_line(line):
    return line.strip() == ""


def _is_indented_line(line):
    return line.startswith(indentation)


def _unindent(line):
    if _is_indented_line(line):
        return line[len(indentation):]
    else:
        return line


def _indent(value):
    return "\n".join(
        line.rstrip()
        for line in value.replace("\n", "\n" + indentation).splitlines(keepends=False)
    )


indentation = " " * 4
