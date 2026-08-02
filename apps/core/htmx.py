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
    Render a template partial.
    """

    return render(
        request,
        template,
        context or {},
    )


def trigger_event(
    *,
    response: HttpResponse,
    event: str,
    payload: dict | None = None,
):
    """
    Attach an HX-Trigger header.
    """

    response["HX-Trigger"] = json.dumps(
        {
            event: payload if payload is not None else True,
        }
    )

    return response


def render_htmx(
    *,
    request,
    template: str,
    context: dict | None = None,
    event: str | None = None,
    payload: dict | None = None,
):
    """
    Render an HTMX response.

    Optionally triggers a client-side event.
    """

    response = render_partial(
        request=request,
        template=template,
        context=context,
    )

    if event:

        response = trigger_event(
            response=response,
            event=event,
            payload=payload,
        )

    return response


def render_modal(
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