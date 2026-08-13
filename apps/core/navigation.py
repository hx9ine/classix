"""
Central navigation definition for the application.

This file contains only the menu structure.
It must not contain business logic, permission checks,
or URL resolution.
"""


NAVIGATION = [
    {
        "title": "Students",
        "items": [
            {
                "label": "Students",
                "url_name": "students:student_list",
                "icon": "students",
            },
        ],
    },
    {
        "title": "Academics",
        "items": [
            {
                "label": "Subjects",
                "url_name": "academics:subject_list",
                "icon": "subject",
            },
            {
                "label": "Timetable",
                "url_name": "academics:timetable_list",
                "icon": "schedule",
            },
            {
                "label": "Homework",
                "url_name": "academics:homework_list",
                "icon": "homework",
            },
            {
                "label": "Attendance",
                "url_name": "attendance:attendance_list",
                "icon": "attendance",
            },
        ],
    },
    {
        "title": "Staff",
        "items": [
            {
                "label": "Staff",
                "url_name": "staff:staff_list",
                "icon": "staff",
            },
        ],
    },
    {
        "title": "RBAC",
        "items": [
            {
                "label": "Roles",
                "url_name": "rbac:role_list",
                "icon": "roles",
                "admin_only": True,
            },
        ],
    },
]