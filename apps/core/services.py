from copy import deepcopy
from django.urls import reverse
from django.urls import NoReverseMatch

from .navigation import NAVIGATION


class NavigationService:
    """
    Builds navigation for templates.

    Future responsibilities:
    - URL resolution
    - Active item detection
    - Subscription filtering
    - Permission filtering
    """

    @classmethod
    def get_navigation(cls, request):
        navigation = deepcopy(NAVIGATION)

        cls._resolve_urls(navigation)

        return navigation

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