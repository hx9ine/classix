from django.http import HttpResponse

from apps.core.htmx import htmx_success


def render_success(
    *,
    request,
    template: str,
    context: dict,
    event: str = "modal:close",
):
    """
    Standard CRUD success response.

    Used after successful create, update,
    and delete operations.
    """

    return htmx_success(
        request=request,
        template=template,
        context=context,
        event=event,
    )


def redirect_success(
    *,
    url: str,
    event: str = "modal:close",
):
    """
    HTMX success response that closes the modal
    and redirects the browser.
    """

    response = HttpResponse()

    response["HX-Redirect"] = url
    response["HX-Trigger"] = event

    return response