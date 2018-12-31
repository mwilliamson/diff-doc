from precisely import all_of, has_attrs, is_instance

from diffdoc import parser, rst


def is_code_block(**kwargs):
    return all_of(
        is_instance(rst.CodeBlock),
        has_attrs(**kwargs),
    )


def is_diffdoc_block(arguments, options, content):
    return all_of(
        is_instance(rst.DiffdocBlock),
        has_attrs(arguments=arguments, options=options, content=content),
    )


def is_diff(**kwargs):
    return all_of(
        is_instance(parser.Diff),
        has_attrs(**kwargs),
    )


def is_literal_block(**kwargs):
    return all_of(
        is_instance(rst.LiteralBlock),
        has_attrs(**kwargs),
    )


def is_output(**kwargs):
    return all_of(
        is_instance(parser.Output),
        has_attrs(**kwargs),
    )


def is_render(**kwargs):
    return all_of(
        is_instance(parser.Render),
        has_attrs(**kwargs),
    )


def is_replace(**kwargs):
    return all_of(
        is_instance(parser.Replace),
        has_attrs(**kwargs),
    )


def is_start(**kwargs):
    return all_of(
        is_instance(parser.Start),
        has_attrs(**kwargs),
    )


def is_text(text):
    return all_of(
        is_instance(rst.Text),
        has_attrs(text=text),
    )


is_empty_element = is_text("")
