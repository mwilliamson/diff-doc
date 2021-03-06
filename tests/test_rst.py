from precisely import assert_that, equal_to, is_sequence, is_sequence as is_tuple

from diffdoc import rst
from .dedent import dedent
from .matchers import is_diffdoc_block, is_text


def test_can_parse_single_diffdoc_block_with_content():
    content = _load_elements(dedent("""
        .. diff-doc:: start example

            Example 1
    """))

    assert_that(content, is_sequence(
        is_diffdoc_block(
            arguments=is_sequence("start", "example"),
            options={},
            content="Example 1",
        ),
    ))


def test_can_parse_single_diffdoc_block_without_content():
    content = _load_elements(dedent("""
        .. diff-doc:: start example
    """))

    assert_that(content, is_sequence(
        is_diffdoc_block(
            arguments=is_sequence("start", "example"),
            options={},
            content="",
        ),
    ))


def test_can_parse_diffdoc_block_without_options_and_content_followed_by_text():
    content = _load_elements(dedent("""
        .. diff-doc:: start example

        Text
    """))

    assert_that(content, is_sequence(
        is_diffdoc_block(
            arguments=is_sequence("start", "example"),
            options={},
            content="",
        ),
        is_text("\n"),
        is_text("Text"),
    ))


def test_can_parse_diffdoc_block_with_options_and_without_content_followed_by_text():
    content = _load_elements(dedent("""
        .. diff-doc:: start example
            :language: python
            :render: True

        Text
    """))

    assert_that(content, is_sequence(
        is_diffdoc_block(
            arguments=is_sequence("start", "example"),
            options={"language": "python", "render": "True"},
            content="",
        ),
        is_text("\n"),
        is_text("Text"),
    ))


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
        is_tuple(1, is_text("Text one\n")),
        is_tuple(2, is_text("\n")),
        is_tuple(3, is_diffdoc_block(
            arguments=is_sequence("start", "example"),
            options={"language": "python", "render": "True"},
            content="Example 1\n\nExample 2\n",
        )),
        is_tuple(10, is_text("\n")),
        is_tuple(11, is_text("Text two\n")),
        is_tuple(12, is_text("\n")),
        is_tuple(13, is_text("Text three\n")),
        is_tuple(14, is_text("\n")),
        is_tuple(15, is_diffdoc_block(
            arguments=is_sequence("replace", "example"),
            options={},
            content="Example 3\n\nExample 4\n",
        )),
        is_tuple(20, is_text("\n")),
        is_tuple(21, is_text("Text four")),
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


def test_diffdoc_block_without_options_nor_content_is_serialised():
    code_block = rst.DiffdocBlock(arguments=("start", "example"), options={}, content="")

    assert_that(code_block.dumps(), equal_to(dedent("""
        .. diff-doc:: start example

    """)))


def test_diffdoc_block_with_options_and_no_content_is_serialised():
    code_block = rst.DiffdocBlock(
        arguments=("start", "example"),
        options={"language": "python", "render": "True"},
        content="",
    )

    assert_that(code_block.dumps(), equal_to(dedent("""
        .. diff-doc:: start example
            :language: python
            :render: True

    """)))


def test_diffdoc_block_with_content_is_serialised():
    code_block = rst.DiffdocBlock(
        arguments=("start", "example"),
        options={},
        content="Example 1\n\nExample 2\n",
    )

    assert_that(code_block.dumps(), equal_to(dedent("""
        .. diff-doc:: start example

            Example 1

            Example 2

    """)))


def test_literal_blocks_are_serialised():
    code_block = rst.LiteralBlock(content="print(1)\n\nprint(2)\nprint(3)\n")

    assert_that(code_block.dumps(), equal_to(dedent("""
        ::

            print(1)

            print(2)
            print(3)

    """)))


def _load_elements(text):
    return [element for line_number, element in rst.loads(text)]
