from apps.rbac.models import RolePermission


MODULE = RolePermission.Module.STUDENTS


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