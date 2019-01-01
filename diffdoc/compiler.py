import difflib
import subprocess
import tempfile

from . import parser, rst


def compile(source):
    state = {}
    result = []

    for line_number, element in source:
        state, transformed_element = _execute(state, element)
        result.append(transformed_element)

    return tuple(result)


def convert_block(source, line_number, block_type):
    state = {}
    result = []

    for element_line_number, element in source:
        if element_line_number < line_number:
            state, transformed_element = _execute(state, element)
        elif element_line_number == line_number:
            if isinstance(element, parser.Diff) and block_type == "replace":
                state, transformed_element = _execute(state, element)
                element = parser.Replace(
                    name=element.name,
                    render=element.render,
                    content=state[element.name].content,
                )
            elif isinstance(element, parser.Replace) and block_type == "diff":
                diff = _generate_diff(
                    state[element.name].content,
                    element.content,
                )
                element = parser.Diff(
                    name=element.name,
                    render=element.render,
                    content=diff,
                )
            else:
                # TODO: raise a better exception
                raise Exception("cannot convert from {} to {}".format(type(element), block_type))

        # TODO: raise error if element not found
        result.append(element)

    return tuple(result)

def _execute(state, element):
    if isinstance(element, parser.Text):
        return state, element

    elif isinstance(element, parser.Diff):
        code = state[element.name].patch(element.content)
        new_state = {
            **state,
            element.name: code,
        }

        if element.render:
            new_element = rst.LiteralBlock(element.content)
        else:
            new_element = empty

        return new_state, new_element

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


def _generate_diff(old, new):
    diff = tuple(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
    ))
    assert diff[0].startswith("---")
    assert diff[1].startswith("+++")
    return "---\n+++\n" + "".join(diff[2:])


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

    def patch(self, patch):
        with tempfile.NamedTemporaryFile("w+t") as content_fileobj:
            content_fileobj.write(self.content)
            content_fileobj.flush()

            with tempfile.NamedTemporaryFile("w+t") as patch_fileobj:
                patch_fileobj.write(patch)
                patch_fileobj.flush()

                subprocess.run(["patch", content_fileobj.name, patch_fileobj.name, "--quiet"], check=True)

            with open(content_fileobj.name, "rt") as new_content_fileobj:
                content = new_content_fileobj.read()

        return self.replace(content)

    def replace(self, content):
        return Code(language=self.language, content=content)

    def run(self):
        return subprocess.run(["python", "-c", self.content], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)


empty = parser.Text("")
