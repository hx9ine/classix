"""
Central navigation definition for the application.

This file contains only the menu structure.
It must not contain business logic, permission checks,
or URL resolution.
"""

NAVIGATION = [
    {
        "title": "Home",
        "items": [
            {
                "label": "Dashboard",
                "url_name": "app_preview",
                "icon": "dashboard",
            },
        ],
    },
    {
        "title": "Academics",
        "items": [
            {
                "label": "Students",
                "url_name": None,
                "icon": "students",
            },
            {
                "label": "Attendance",
                "url_name": None,
                "icon": "attendance",
            },
            {
                "label": "Grades",
                "icon": "grades",
                "children": [
                    {
                        "label": "Exam Grades",
                        "url_name": None,
                    },
                    {
                        "label": "Report Cards",
                        "url_name": None,
                    },
                ],
            },
        ],
    },
]