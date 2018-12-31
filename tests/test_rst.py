from precisely import all_of, assert_that, equal_to, has_attrs, is_instance, is_sequence
import textwrap

from diffdoc import rst


def test_parsing_rst_splits_file_into_text_and_diffdoc_blocks():
    content = rst.loads(dedent("""
        Text one

        .. diff-doc:: start example
            :language: python
            :render: True

            Example 1

            Example 2

        Text two

        Text three

        .. diff-doc:: replace example

            Example 3

            Example 4

        Text four
    """))

    assert_that(content, is_sequence(
        is_text("Text one\n"),
        is_text("\n"),
        is_diffdoc_block(
            arguments=is_sequence("start", "example"),
            options={"language": "python", "render": "True"},
            content="Example 1\n\nExample 2\n",
        ),
        is_text("\n"),
        is_text("Text two\n"),
        is_text("\n"),
        is_text("Text three\n"),
        is_text("\n"),
        is_diffdoc_block(
            arguments=is_sequence("replace", "example"),
            options={},
            content="Example 3\n\nExample 4\n",
        ),
        is_text("\n"),
        is_text("Text four"),
    ))


def test_writing_rst_turns_elements_into_strings():
    elements = [
        rst.Text("Text one\n"),
        rst.Text("\n"),
        rst.Text("Text two\n"),
        rst.Text("\n"),
    ]

    assert_that(rst.dumps(elements), equal_to(dedent("""
        Text one

        Text two


    """)))


def test_code_blocks_are_serialised():
    code_block = rst.CodeBlock(language="python", content="print(1)\n\nprint(2)\nprint(3)\n")

    assert_that(code_block.dumps(), equal_to(dedent("""
        .. code-block:: python

            print(1)

            print(2)
            print(3)

    """)))


def is_diffdoc_block(arguments, options, content):
    return all_of(
        is_instance(rst.DiffdocBlock),
        has_attrs(arguments=arguments, options=options, content=content),
    )


def is_text(text):
    return all_of(
        is_instance(rst.Text),
        has_attrs(text=text),
    )


def dedent(value):
    lines = textwrap.dedent(value).splitlines(keepends=True)
    assert lines[0].strip() == ""
    return "".join(lines[1:-1]) + lines[-1].rstrip("\r\n")
