from copy import deepcopy

from django.urls import NoReverseMatch, reverse

from .navigation import NAVIGATION


class NavigationService:
    """
    Builds navigation for templates.

    Responsibilities:
    - URL resolution
    - Active item detection
    - Admin-only item filtering

    Future responsibilities:
    - Subscription filtering
    - Permission filtering
    """

    @classmethod
    def get_navigation(cls, request):
        navigation = deepcopy(NAVIGATION)

        cls._filter_admin_only_items(
            navigation=navigation,
            is_admin=request.user.is_admin,
        )

        cls._resolve_urls(navigation)

        cls._mark_active_items(
            navigation=navigation,
            request_path=request.path,
        )

        return navigation

    @staticmethod
    def _filter_admin_only_items(
        *,
        navigation,
        is_admin,
    ):
        if is_admin:
            return

        for group in navigation:

            group["items"] = [
                item
                for item in group["items"]
                if not item.get("admin_only", False)
            ]

    @staticmethod
    def _resolve_urls(groups):
        for group in groups:

            for item in group["items"]:

                NavigationService._resolve_item(item)

    @staticmethod
    def _resolve_item(item):
        url_name = item.get("url_name")

        if url_name:

            try:
                item["url"] = reverse(url_name)

            except NoReverseMatch:
                item["url"] = "#"

        else:

            item["url"] = "#"

        for child in item.get("children", []):

            NavigationService._resolve_item(child)

    @staticmethod
    def _mark_active_items(
        *,
        navigation,
        request_path,
    ):
        for group in navigation:

            for item in group["items"]:

                NavigationService._mark_active_item(
                    item=item,
                    request_path=request_path,
                )

    @staticmethod
    def _mark_active_item(
        *,
        item,
        request_path,
    ):
        item["active"] = False

        if item.get("url") != "#":

            item["active"] = (
                item["url"] == request_path
            )

        has_active_child = False

        for child in item.get("children", []):

            NavigationService._mark_active_item(
                item=child,
                request_path=request_path,
            )

            if child.get("active"):

                has_active_child = True

        if has_active_child:

            item["active"] = True
            item["expanded"] = True

        else:

            item["expanded"] = False