from apps.core.htmx import htmx_success


def crud_success(
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