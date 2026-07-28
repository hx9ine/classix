from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager for tenant-scoped users.
    """
    use_in_migrations = True

    def create_user(self, tenant, email, password=None, **extra_fields):
        if tenant is None:
            raise ValueError("Tenant is required.")

        if not email:
            raise ValueError("Email address is required.")

        email = self.normalize_email(email)

        user = self.model(
            tenant=tenant,
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.full_clean(
            exclude=["password"],
        )
        user.save(using=self._db)

        return user

    def create_superuser(self, *args, **kwargs):
        raise NotImplementedError(
            "Platform administration is handled separately. "
            "Tenant admins are provisioned during tenant onboarding."
        )