from .services import NavigationService


def navigation(request):
    return {
        "navigation": NavigationService.get_navigation(request),
    }