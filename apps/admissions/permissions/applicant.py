from apps.rbac.models import RolePermission


MODULE = RolePermission.Module.ADMISSIONS


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


__all__ = [
    "MODULE",
    "VIEW",
    "CREATE",
    "EDIT",
    "DELETE",
]