from precisely import assert_that

from diffdoc import parser, rst
from .matchers import is_diff, is_output, is_render, is_replace, is_start, is_text


class TestReadElement(object):
    def test_text_element_is_unchanged(self):
        element = parser._read_rst_element(rst.Text("blah"))
        assert_that(element, is_text("blah"))

    def test_diffdoc_diff(self):
        element = parser._read_rst_element(rst.DiffdocBlock(
            arguments=("diff", "example"),
            options={
                "render": "True",
            },
            content="CONTENT",
        ))
        assert_that(element, is_diff(
            name="example",
            render=True,
            content="CONTENT",
        ))

    def test_diffdoc_output(self):
        element = parser._read_rst_element(rst.DiffdocBlock(
            arguments=("output", "example"),
            options={
                "render": "True",
            },
            content="CONTENT",
        ))
        assert_that(element, is_output(
            name="example",
            render=True,
            content="CONTENT",
        ))

    def test_diffdoc_render(self):
        element = parser._read_rst_element(rst.DiffdocBlock(
            arguments=("render", "example"),
            options={},
            content="CONTENT",
        ))
        assert_that(element, is_render(
            name="example",
            content="CONTENT",
        ))

    def test_diffdoc_replace(self):
        element = parser._read_rst_element(rst.DiffdocBlock(
            arguments=("replace", "example"),
            options={
                "render": "True",
            },
            content="CONTENT",
        ))
        assert_that(element, is_replace(
            name="example",
            render=True,
            content="CONTENT",
        ))

    def test_diffdoc_start(self):
        element = parser._read_rst_element(rst.DiffdocBlock(
            arguments=("start", "example"),
            options={
                "language": "python",
                "render": "True",
            },
            content="CONTENT",
        ))
        assert_that(element, is_start(
            name="example",
            language="python",
            render=True,
            content="CONTENT",
        ))
