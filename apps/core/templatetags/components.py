from django import template
from django.template.loader import render_to_string

register = template.Library()


class ComponentNode(template.Node):
    def __init__(self, component_name, nodelist):
        self.component_name = component_name
        self.nodelist = nodelist

    def render(self, context):
        component_name = self.component_name.resolve(context)

        slot = self.nodelist.render(context)

        component_context = context.flatten()
        component_context["slot"] = slot

        return render_to_string(
            f"components/{component_name}.html",
            component_context,
        )


@register.tag(name="component")
def component(parser, token):
    bits = token.split_contents()

    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "Usage: {% component \"name\" %}"
        )

    component_name = parser.compile_filter(bits[1])

    nodelist = parser.parse(("endcomponent",))
    parser.delete_first_token()

    return ComponentNode(component_name, nodelist)