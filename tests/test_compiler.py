from precisely import assert_that, equal_to, has_attrs, is_mapping, is_sequence
import pytest

from diffdoc import compiler, parser
from .dedent import dedent
from .matchers import is_code_block, is_diff, is_empty_element, is_literal_block, is_replace, is_start


def test_text_is_preserved_without_state_change():
    element = parser.Text("CONTENT")
    state = {}

    assert_that(compiler._execute(state, element), is_result({}, element))


class TestDiff(object):
    def test_diff_updates_code_using_content_as_patch(self):
        element = parser.Diff(
            name="example",
            content=dedent("""
                --- old
                +++ new

                @@ -1,2 +1,2 @@
                -x = 1
                +x = 2
                 print(x)

            """),
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)\n",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_state, is_mapping({
            "example": is_code(
                language="python",
                content="x = 2\nprint(x)\n",
            ),
        }))

    def test_diff_with_render_false_renders_nothing(self):
        element = parser.Diff(
            name="example",
            content=dedent("""
                --- old
                +++ new

                @@ -1,2 +1,2 @@
                -x = 1
                +x = 2
                 print(x)

            """),
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)\n",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_empty_element)

    def test_diff_with_render_true_renders_content(self):
        content = dedent("""
            --- old
            +++ new

            @@ -1,2 +1,2 @@
            -x = 1
            +x = 2
             print(x)

        """)
        element = parser.Diff(
            name="example",
            content=content,
            render=True,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)\n",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_literal_block(content=content))


class TestOutput(object):
    def test_output_does_not_change_state(self):
        element = parser.Output(
            name="example",
            content="1",
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_state, equal_to(state))

    def test_output_renders_nothing_when_render_is_false(self):
        element = parser.Output(
            name="example",
            content="1",
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_empty_element)

    def test_output_renders_content_when_render_is_true(self):
        element = parser.Output(
            name="example",
            content="1",
            render=True,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_literal_block(content="1"))

    def test_when_output_is_incorrect_then_error_is_raised(self):
        element = parser.Output(
            name="example",
            content="2",
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)",
            ),
        }

        error = pytest.raises(ValueError, lambda: compiler._execute(state, element))
        assert_that(str(error.value), equal_to("Documented output:\n2\nActual output:\n1\n"))

    def test_output_includes_stderr(self):
        element = parser.Output(
            name="example",
            content="2",
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="import sys\nx = 1\nprint(x, file=sys.stderr)",
            ),
        }

        error = pytest.raises(ValueError, lambda: compiler._execute(state, element))
        assert_that(str(error.value), equal_to("Documented output:\n2\nActual output:\n1\n"))


class TestRender(object):
    def test_render_does_not_change_state(self):
        element = parser.Render(
            name="example",
            content="print(x)",
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_state, equal_to(state))

    def test_render_renders_content(self):
        element = parser.Render(
            name="example",
            content="print(x)",
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1\nprint(x)",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_code_block(
            language="python",
            content="print(x)",
        ))


class TestReplace(object):
    def test_replace_replaces_content_for_code(self):
        element = parser.Replace(
            name="example",
            content="x = 2",
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_state, is_mapping({
            "example": is_code(
                language="python",
                content="x = 2",
            ),
        }))

    def test_replace_with_render_false_renders_nothing(self):
        element = parser.Replace(
            name="example",
            content="x = 2",
            render=False,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_empty_element)

    def test_replace_with_render_true_renders_content(self):
        element = parser.Replace(
            name="example",
            content="x = 2",
            render=True,
        )
        state = {
            "example": compiler.Code(
                language="python",
                content="x = 1",
            ),
        }

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_code_block(
            language="python",
            content="x = 2",
        ))


class TestStart(object):
    def test_start_initialises_state_for_name(self):
        # TODO: error if name already taken
        element = parser.Start(
            name="example",
            language="python",
            content="x = 1",
            render=False,
        )
        state = {}

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_state, is_mapping({
            "example": is_code(
                language="python",
                content="x = 1",
            ),
        }))

    def test_start_with_render_false_renders_nothing(self):
        element = parser.Start(
            name="example",
            language="python",
            content="x = 1",
            render=False,
        )
        state = {}

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_empty_element)

    def test_start_with_render_true_renders_content(self):
        element = parser.Start(
            name="example",
            language="python",
            content="x = 1",
            render=True,
        )
        state = {}

        new_state, new_element = compiler._execute(state, element)
        assert_that(new_element, is_code_block(
            language="python",
            content="x = 1",
        ))


class TestConvertBlock(object):
    def test_converting_from_diff_to_replace_generates_replace_block(self):
        start = parser.Start(
            name="example",
            language="python",
            render=True,
            content=dedent("""
                x = 1
                print(x)

            """),
        )
        diff = parser.Diff(
            name="example",
            render=False,
            content=dedent("""
                --- old
                +++ new

                @@ -1,2 +1,2 @@
                -x = 1
                +x = 2
                 print(x)

            """),
        )

        output = compiler.convert_block(
            source=(
                (1, start),
                (2, diff),
            ),
            line_number=2,
            block_type="replace",
        )

        assert_that(output, is_sequence(
            is_start(),
            is_replace(
                name="example",
                render=False,
                content=dedent("""
                    x = 2
                    print(x)

                """)
            ),
        ))

    def test_converting_from_replace_to_diff_generates_diff_block(self):
        start = parser.Start(
            name="example",
            language="python",
            render=True,
            content=dedent("""
                x = 1
                print(x)

            """),
        )
        diff = parser.Replace(
            name="example",
            render=False,
            content=dedent("""
                x = 2
                print(x)

            """),
        )

        output = compiler.convert_block(
            source=(
                (1, start),
                (2, diff),
            ),
            line_number=2,
            block_type="diff",
        )

        assert_that(output, is_sequence(
            is_start(),
            is_diff(
                name="example",
                render=False,
                content=dedent("""
                    ---
                    +++
                    @@ -1,2 +1,2 @@
                    -x = 1
                    +x = 2
                     print(x)

                """)
            ),
        ))


def is_code(language, content):
    return has_attrs(language=language, content=content)


def is_result(state, element):
    return is_sequence(
        state,
        element
    )
