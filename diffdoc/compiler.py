import subprocess

from . import parser, rst


def compile(source):
    state = {}
    result = []

    for element in source:
        state, transformed_element = _execute(state, element)
        result.append(transformed_element)

    return tuple(result)


def _execute(state, element):
    if isinstance(element, parser.Text):
        return state, element

    elif isinstance(element, parser.Diff):
        return state, empty
        code = state[element.name]

        if element.render:
            new_element = rst.LiteralBlock(element.content)
        else:
            new_element = empty

        return state, new_element

    elif isinstance(element, parser.Output):
        code = state[element.name]
        result = code.run()
        actual_output = result.stdout.decode("utf-8")
        if actual_output.strip() != element.content.strip():
            raise ValueError("Documented output:\n{}\nActual output:\n{}".format(
                element.content,
                actual_output,
            ))

        if element.render:
            new_element = rst.LiteralBlock(element.content)
        else:
            new_element = empty

        return state, new_element

    elif isinstance(element, parser.Render):
        # TODO: check render content is consistent with content, and includes unrendered diffs
        code = state[element.name]

        return state, rst.CodeBlock(
            language=code.language,
            content=element.content,
        )

    elif isinstance(element, parser.Replace):
        code = state[element.name].replace(element.content)
        new_state = {
            **state,
            element.name: code,
        }
        new_element = _render(code, element)
        return new_state, new_element

    elif isinstance(element, parser.Start):
        code = Code(language=element.language, content=element.content)
        new_state = {
            **state,
            element.name: code,
        }
        new_element = _render(code, element)
        return new_state, new_element
    else:
        raise Exception("Unhandled element: {}".format(element))


def _render(code, element):
    if element.render:
        return rst.CodeBlock(
            language=code.language,
            content=code.content,
        )
    else:
        return empty


class Code(object):
    def __init__(self, language, content):
        self.language = language
        self.content = content

    def replace(self, content):
        return Code(language=self.language, content=content)

    def run(self):
        return subprocess.run(["python", "-c", self.content], stdout=subprocess.PIPE)


empty = parser.Text("")
