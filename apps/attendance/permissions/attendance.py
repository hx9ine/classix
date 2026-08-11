from apps.rbac.models import RolePermission


# ============================================================================
# Attendance Permissions
# ============================================================================

MODULE = RolePermission.Module.ATTENDANCE


VIEW = {
    "module": MODULE,
    "action": RolePermission.Action.VIEW,
}


CREATE = {
    "module": MODULE,
    "action": RolePermission.Action.CREATE,
}


EDIT = {
    "module": MODULE,
    "action": RolePermission.Action.EDIT,
}


DELETE = {
    "module": MODULE,
    "action": RolePermission.Action.DELETE,
}