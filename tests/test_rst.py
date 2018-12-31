from precisely import all_of, assert_that, has_attrs, is_instance, is_sequence
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
    return textwrap.dedent(value).strip("\r\n")
