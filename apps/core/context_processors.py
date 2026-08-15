from .services import NavigationService


def navigation(request):
    if not request.user.is_authenticated:
        return {
            "navigation": [],
        }

    return {
        "navigation": NavigationService.get_navigation(request),
    }