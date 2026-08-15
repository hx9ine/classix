from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.billing.selectors.licensing import (
    count_active_admins,
    count_active_faculty,
    count_active_staff,
)
from apps.rbac.models import Role
from apps.staff.forms import StaffForm
from apps.staff.models import EmploymentStatus, Staff
from apps.staff.services.staff import (
    activate_staff,
    create_staff,
    deactivate_staff,
    update_staff,
)
from apps.tenants.models import Tenant


class StaffServiceTests(TestCase):
    """
    Tests for Staff services, including live license enforcement.
    """

    def setUp(self):
        self.tenant = Tenant.objects.create(
            school_name="Demo School",
            subdomain_slug="demo",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=2,
            staff_license_limit=2,
            student_license_limit=50,
        )

        self.admin_role = Role.objects.create(
            tenant=self.tenant,
            name="Admin",
            is_admin_role=True,
            license_category=Role.LicenseCategory.ADMIN,
        )

        self.teacher_role = Role.objects.create(
            tenant=self.tenant,
            name="Teacher",
            is_admin_role=False,
            license_category=Role.LicenseCategory.FACULTY,
        )

        self.staff_role = Role.objects.create(
            tenant=self.tenant,
            name="Accountant",
            is_admin_role=False,
            license_category=Role.LicenseCategory.STAFF,
        )

    # ========================================================================
    # Helpers
    # ========================================================================

    def build_form(
        self,
        *,
        role,
        first_name="Demo",
        last_name="Staff",
    ):
        return StaffForm(
            data={
                "first_name": first_name,
                "last_name": last_name,
                "role": role.pk,
                "joining_date": date.today(),
                "phone": "",
            },
            tenant=self.tenant,
        )

    def create_staff_directly(
        self,
        *,
        role,
        status=EmploymentStatus.ACTIVE,
        first_name="Existing",
        last_name="Staff",
    ):
        return Staff._base_manager.create(
            tenant=self.tenant,
            first_name=first_name,
            last_name=last_name,
            role=role,
            employment_status=status,
            joining_date=date.today(),
        )

    # ========================================================================
    # Create
    # ========================================================================

    def test_create_active_faculty_consumes_faculty_license(self):
        form = self.build_form(
            role=self.teacher_role,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        staff = create_staff(
            tenant=self.tenant,
            form=form,
        )

        self.assertEqual(
            staff.employment_status,
            EmploymentStatus.ACTIVE,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            1,
        )

    def test_create_active_staff_consumes_staff_license(self):
        form = self.build_form(
            role=self.staff_role,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        create_staff(
            tenant=self.tenant,
            form=form,
        )

        self.assertEqual(
            count_active_staff(
                tenant=self.tenant,
            ),
            1,
        )

    def test_create_active_admin_consumes_admin_license(self):
        form = self.build_form(
            role=self.admin_role,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        create_staff(
            tenant=self.tenant,
            form=form,
        )

        self.assertEqual(
            count_active_admins(
                tenant=self.tenant,
            ),
            1,
        )

    def test_create_active_faculty_is_blocked_when_faculty_pool_is_full(self):
        self.create_staff_directly(
            role=self.teacher_role,
            first_name="Teacher",
            last_name="One",
        )

        self.create_staff_directly(
            role=self.teacher_role,
            first_name="Teacher",
            last_name="Two",
        )

        form = self.build_form(
            role=self.teacher_role,
            first_name="Teacher",
            last_name="Three",
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Faculty license limit",
        ):
            create_staff(
                tenant=self.tenant,
                form=form,
            )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            2,
        )

    def test_create_active_staff_is_blocked_when_staff_pool_is_full(self):
        self.create_staff_directly(
            role=self.staff_role,
            first_name="Accountant",
            last_name="One",
        )

        self.create_staff_directly(
            role=self.staff_role,
            first_name="Accountant",
            last_name="Two",
        )

        form = self.build_form(
            role=self.staff_role,
            first_name="Accountant",
            last_name="Three",
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Staff license limit",
        ):
            create_staff(
                tenant=self.tenant,
                form=form,
            )

        self.assertEqual(
            count_active_staff(
                tenant=self.tenant,
            ),
            2,
        )

    # ========================================================================
    # Deactivation
    # ========================================================================

    def test_deactivate_staff_releases_license(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            1,
        )

        deactivate_staff(
            instance=staff,
        )

        staff.refresh_from_db()

        self.assertEqual(
            staff.employment_status,
            EmploymentStatus.INACTIVE,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            0,
        )

    def test_deactivate_already_inactive_staff_is_noop(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
            status=EmploymentStatus.INACTIVE,
        )

        result = deactivate_staff(
            instance=staff,
        )

        self.assertEqual(
            result.pk,
            staff.pk,
        )

        self.assertEqual(
            result.employment_status,
            EmploymentStatus.INACTIVE,
        )

    # ========================================================================
    # Activation
    # ========================================================================

    def test_activate_inactive_staff_consumes_license(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
            status=EmploymentStatus.INACTIVE,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            0,
        )

        activate_staff(
            instance=staff,
        )

        staff.refresh_from_db()

        self.assertEqual(
            staff.employment_status,
            EmploymentStatus.ACTIVE,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            1,
        )

    def test_activate_staff_is_blocked_when_license_pool_is_full(self):
        self.create_staff_directly(
            role=self.teacher_role,
            first_name="Teacher",
            last_name="One",
        )

        self.create_staff_directly(
            role=self.teacher_role,
            first_name="Teacher",
            last_name="Two",
        )

        inactive_staff = self.create_staff_directly(
            role=self.teacher_role,
            status=EmploymentStatus.INACTIVE,
            first_name="Teacher",
            last_name="Inactive",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Faculty license limit",
        ):
            activate_staff(
                instance=inactive_staff,
            )

        inactive_staff.refresh_from_db()

        self.assertEqual(
            inactive_staff.employment_status,
            EmploymentStatus.INACTIVE,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            2,
        )

    def test_activate_already_active_staff_is_noop(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
        )

        result = activate_staff(
            instance=staff,
        )

        self.assertEqual(
            result.pk,
            staff.pk,
        )

        self.assertEqual(
            result.employment_status,
            EmploymentStatus.ACTIVE,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            1,
        )

    # ========================================================================
    # Role Reassignment
    # ========================================================================

    def test_active_faculty_to_faculty_role_does_not_consume_extra_license(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
        )

        senior_teacher_role = Role.objects.create(
            tenant=self.tenant,
            name="Senior Teacher",
            is_admin_role=False,
            license_category=Role.LicenseCategory.FACULTY,
        )

        form = self.build_form(
            role=senior_teacher_role,
            first_name=staff.first_name,
            last_name=staff.last_name,
        )

        form.instance = staff

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        updated = update_staff(
            form=form,
        )

        self.assertEqual(
            updated.pk,
            staff.pk,
        )

        self.assertEqual(
            updated.role_id,
            senior_teacher_role.pk,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            1,
        )

    def test_active_faculty_to_staff_role_consumes_staff_license(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
        )

        form = self.build_form(
            role=self.staff_role,
            first_name=staff.first_name,
            last_name=staff.last_name,
        )

        form.instance = staff

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        updated = update_staff(
            form=form,
        )

        self.assertEqual(
            updated.pk,
            staff.pk,
        )

        self.assertEqual(
            updated.role_id,
            self.staff_role.pk,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            0,
        )

        self.assertEqual(
            count_active_staff(
                tenant=self.tenant,
            ),
            1,
        )

    def test_active_faculty_to_full_staff_pool_is_blocked(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
            first_name="Teacher",
            last_name="One",
        )

        self.create_staff_directly(
            role=self.staff_role,
            first_name="Accountant",
            last_name="One",
        )

        self.create_staff_directly(
            role=self.staff_role,
            first_name="Accountant",
            last_name="Two",
        )

        form = self.build_form(
            role=self.staff_role,
            first_name=staff.first_name,
            last_name=staff.last_name,
        )

        form.instance = staff

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Staff license limit",
        ):
            update_staff(
                form=form,
            )

        staff.refresh_from_db()

        self.assertEqual(
            staff.role_id,
            self.teacher_role.pk,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            1,
        )

        self.assertEqual(
            count_active_staff(
                tenant=self.tenant,
            ),
            2,
        )

    def test_inactive_staff_can_change_to_full_license_category(self):
        staff = self.create_staff_directly(
            role=self.teacher_role,
            status=EmploymentStatus.INACTIVE,
        )

        self.create_staff_directly(
            role=self.staff_role,
            first_name="Accountant",
            last_name="One",
        )

        self.create_staff_directly(
            role=self.staff_role,
            first_name="Accountant",
            last_name="Two",
        )

        form = self.build_form(
            role=self.staff_role,
            first_name=staff.first_name,
            last_name=staff.last_name,
        )

        form.instance = staff

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        updated = update_staff(
            form=form,
        )

        self.assertEqual(
            updated.pk,
            staff.pk,
        )

        self.assertEqual(
            updated.role_id,
            self.staff_role.pk,
        )

        self.assertEqual(
            updated.employment_status,
            EmploymentStatus.INACTIVE,
        )

    # ========================================================================
    # Tenant Safety
    # ========================================================================

    def test_update_staff_rejects_staff_from_different_tenant(self):
        other_tenant = Tenant.objects.create(
            school_name="Other School",
            subdomain_slug="other",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=1,
            staff_license_limit=1,
            student_license_limit=10,
        )

        other_role = Role.objects.create(
            tenant=other_tenant,
            name="Other Teacher",
            is_admin_role=False,
            license_category=Role.LicenseCategory.FACULTY,
        )

        staff = Staff._base_manager.create(
            tenant=other_tenant,
            first_name="Other",
            last_name="Teacher",
            role=other_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        form = self.build_form(
            role=self.teacher_role,
            first_name=staff.first_name,
            last_name=staff.last_name,
        )

        form.instance = staff

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "The staff member does not belong to the current tenant.",
        ):
            update_staff(
                form=form,
            )