import json

from django.http import HttpResponse
from django.shortcuts import render


def is_htmx(request) -> bool:
    """
    Returns True if the request originated from HTMX.
    """
    return request.headers.get("HX-Request") == "true"


def render_partial(
    *,
    request,
    template: str,
    context: dict | None = None,
):
    """
    Render a partial template.
    """
    return render(
        request,
        template,
        context or {},
    )


def trigger_client_event(
    response: HttpResponse,
    event_name: str,
    payload: dict | None = None,
) -> HttpResponse:
    """
    Attach an HX-Trigger header to the response.
    """

    response["HX-Trigger"] = json.dumps(
        {
            event_name: payload if payload is not None else True,
        }
    )

    return response


def htmx_success(
    *,
    request,
    template: str,
    context: dict | None = None,
    event: str = "modal:close",
    payload: dict | None = None,
):
    """
    Render a successful HTMX response.
    """

    response = render_partial(
        request=request,
        template=template,
        context=context,
    )

    return trigger_client_event(
        response=response,
        event_name=event,
        payload=payload,
    )


def htmx_refresh(
    *,
    request,
    template: str,
    context: dict | None = None,
):
    """
    Render a refreshed partial.
    """

    return render_partial(
        request=request,
        template=template,
        context=context,
    )


def htmx_modal(
    *,
    request,
    template: str,
    context: dict | None = None,
):
    """
    Render modal content.
    """

    return render(
        request,
        template,
        context or {},
    )