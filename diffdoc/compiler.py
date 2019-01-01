import subprocess

from . import parser, rst
from .diff import apply_patch, generate_diff


def compile(source):
    state = {}
    result = []

    for line_number, element in source:
        state, transformed_element = _execute(state, element, line_number=line_number)
        result.append(transformed_element)

    return tuple(result)


def convert_block(source, line_number, block_type):
    state = {}
    result = []

    for element_line_number, element in source:
        if element_line_number < line_number:
            state, transformed_element = _execute(state, element, line_number=element_line_number)
        elif element_line_number == line_number:
            if isinstance(element, parser.Diff) and block_type == "replace":
                state, transformed_element = _execute(state, element, line_number=element_line_number)
                element = parser.Replace(
                    name=element.name,
                    render=element.render,
                    content=state[element.name].content,
                )
            elif isinstance(element, parser.Replace) and block_type == "diff":
                diff = generate_diff(
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

def _execute(state, element, line_number):
    if isinstance(element, parser.Text):
        return state, element

    elif isinstance(element, parser.Diff):
        old_code = state[element.name]
        old_code.raise_if_pending(operation="apply diff", line_number=line_number)

        code = old_code.patch(element.content)

        if element.render:
            code = code.render_content()
            new_element = rst.LiteralBlock(element.content)
        else:
            new_element = empty

        new_state = {
            **state,
            element.name: code,
        }

        return new_state, new_element

    elif isinstance(element, parser.Output):
        code = state[element.name]
        code.raise_if_pending(operation="render output", line_number=line_number)

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

        new_state = {
            **state,
            element.name: code.render(element.content),
        }

        return new_state, rst.CodeBlock(
            language=code.language,
            content=element.content,
        )

    elif isinstance(element, parser.Replace):
        old_code = state[element.name]
        old_code.raise_if_pending(operation="replace", line_number=line_number)

        code = old_code.replace(element.content)

        if element.render:
            code = code.render_content()
            new_element = rst.CodeBlock(
                language=code.language,
                content=code.content,
            )
        else:
            new_element = empty

        new_state = {
            **state,
            element.name: code,
        }

        return new_state, new_element

    elif isinstance(element, parser.Start):
        code = Code.blank(language=element.language).replace(element.content)

        if element.render:
            code = code.render_content()
            new_element = rst.CodeBlock(
                language=code.language,
                content=code.content,
            )
        else:
            new_element = empty

        new_state = {
            **state,
            element.name: code,
        }

        return new_state, new_element

    else:
        raise Exception("Unhandled element: {}".format(element))


class Code(object):
    @staticmethod
    def blank(language):
        return Code(language=language, content="", pending_lines=())

    def __init__(self, language, content, pending_lines):
        self.language = language
        self.content = content
        self.pending_lines = pending_lines

    def raise_if_pending(self, operation, line_number):
        if self.pending_lines:
            pending_lines_str = "".join(
                "\n" + pending_line
                for pending_line in self.pending_lines
            )
            raise ValueError("cannot {} on line number {}, pending lines:{}".format(
                operation,
                line_number,
                pending_lines_str,
            ))

    def patch(self, patch):
        return self.replace(apply_patch(self.content, patch))

    def replace(self, new_content):
        old_lines = self.content.splitlines()
        new_lines = new_content.splitlines()
        pending_lines = tuple(filter(
            lambda new_line: new_line not in old_lines,
            new_lines,
        ))
        return Code(language=self.language, content=new_content, pending_lines=pending_lines)

    def render(self, rendered_content):
        rendered_lines = rendered_content.splitlines()
        pending_lines = tuple(filter(
            lambda pending_line: pending_line not in rendered_lines,
            self.pending_lines,
        ))
        return Code(language=self.language, content=self.content, pending_lines=pending_lines)

    def render_content(self):
        return self.render(self.content)

    def run(self):
        return subprocess.run(["python", "-c", self.content], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)


empty = parser.Text("")
