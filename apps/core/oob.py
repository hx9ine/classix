from django.http import HttpResponse
from django.template.loader import render_to_string


def render_oob(
    *,
    html: str,
    close_container: str | None = None,
):
    """
    Return an HTMX Out-Of-Band response.

    Optionally clears an HTMX container.
    """

    if close_container:

        html += (
            f'<div id="{close_container}" '
            'hx-swap-oob="true"></div>'
        )

    return HttpResponse(html)


def render_select_oob(
    *,
    request,
    field_id: str,
    field_name: str,
    options,
    selected,
    close_container: str = "nested-modal-container",
):
    """
    Render an HTMX OOB response for a dependent select.
    """

    html = render_to_string(
        "components/forms/select_options.html",
        {
            "field_id": field_id,
            "field_name": field_name,
            "options": options,
            "selected": selected,
        },
        request=request,
    )

    return render_oob(
        html=html,
        close_container=close_container,
    )