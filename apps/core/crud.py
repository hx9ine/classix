from django.http import HttpResponse

from apps.core.htmx import render_htmx


def render_success(
    *,
    request,
    template: str,
    context: dict,
    event: str | None = None,
):
    """
    Standard CRUD success response.

    Renders an HTMX partial and optionally triggers
    a client-side event.
    """

    return render_htmx(
        request=request,
        template=template,
        context=context,
        event=event,
    )


def render_redirect(
    *,
    url: str,
    event: str | None = "modal:close",
):
    """
    HTMX redirect response.

    Optionally triggers a client-side event before
    redirecting.
    """

    response = HttpResponse()

    response["HX-Redirect"] = url

    if event:
        response["HX-Trigger"] = event

    return response