from apps.rbac.models import RolePermission


MODULE = RolePermission.Module.ADMISSIONS


CREATE = {
    "module": MODULE,
    "action": RolePermission.Action.CREATE,
}


__all__ = [
    "MODULE",
    "CREATE",
]