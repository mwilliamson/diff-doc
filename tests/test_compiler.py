from precisely import assert_that, equal_to, has_attrs, is_mapping, is_sequence

from diffdoc import compiler, parser
from .matchers import is_code_block, is_empty_element


def test_text_is_preserved_without_state_change():
    element = parser.Text("CONTENT")
    state = {}

    assert_that(compiler._execute(state, element), is_result({}, element))


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


def is_code(language, content):
    return has_attrs(language=language, content=content)


def is_result(state, element):
    return is_sequence(
        state,
        element
    )
