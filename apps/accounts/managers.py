from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        tenant,
        email,
        password=None,
        **extra_fields,
    ):
        """
        Create a tenant-scoped user.

        If no password is supplied, an unusable password is set.
        """

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

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_system_user(
        self,
        tenant,
        email,
        **extra_fields,
    ):
        """
        Creates a user with an unusable password.

        Intended for internal provisioning only.
        """

        return self.create_user(
            tenant=tenant,
            email=email,
            password=None,
            **extra_fields,
        )

    def create_superuser(self, *args, **kwargs):
        """
        Platform superusers are intentionally unsupported.

        Tenant administrators are provisioned during
        tenant onboarding.
        """

        raise NotImplementedError(
            "Platform administration is handled separately. "
            "Tenant admins are provisioned during tenant onboarding."
        )