from django import template
from django.template.base import (
    FilterExpression,
    Node,
    TemplateSyntaxError,
)
from django.template.loader import render_to_string

register = template.Library()


class ComponentNode(Node):
    """
    Renders a reusable template component.

    Available inside every component:

    - slot
    - any keyword arguments passed to the component
    """

    def __init__(
        self,
        component_name: FilterExpression,
        kwargs: dict[str, FilterExpression],
        nodelist,
    ):
        self.component_name = component_name
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context):
        component_name = self.component_name.resolve(context)

        component_context = context.flatten()
        component_context["slot"] = self.nodelist.render(context)

        for key, value in self.kwargs.items():
            component_context[key] = value.resolve(context)

        request = context.get("request")

        return render_to_string(
            f"components/{component_name}.html",
            component_context,
            request=request,
        )


@register.tag(name="component")
def component(parser, token):
    """
    Usage:

        {% component "layout/card" %}
            ...
        {% endcomponent %}

        {% component "layout/modal" title="Create Student" subtitle="Basic information" %}
            ...
        {% endcomponent %}
    """

    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError(
            'Usage: {% component "component_name" %}'
        )

    component_name = parser.compile_filter(bits[1])

    kwargs = {}

    for bit in bits[2:]:
        if "=" not in bit:
            raise TemplateSyntaxError(
                f'Invalid argument "{bit}". Expected key=value.'
            )

        key, value = bit.split("=", 1)
        kwargs[key] = parser.compile_filter(value)

    nodelist = parser.parse(("endcomponent",))
    parser.delete_first_token()

    return ComponentNode(
        component_name=component_name,
        kwargs=kwargs,
        nodelist=nodelist,
    )