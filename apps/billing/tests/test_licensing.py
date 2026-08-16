from datetime import date

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academic_structure.models import (
    AcademicSession,
    ClassLevel,
    Section,
)
from apps.billing.selectors.licensing import (
    count_active_admins,
    count_active_faculty,
    count_active_staff,
    count_active_students,
    get_license_limits,
    get_license_status,
)
from apps.billing.services.licensing import (
    ensure_staff_license_available,
    ensure_staff_role_change_available,
    ensure_student_license_available,
)
from apps.billing.models import (
    LicenseAddon,
    LicenseAddonType,
)
from apps.rbac.models import Role
from apps.staff.models import EmploymentStatus, Staff
from apps.students.models import Student, StudentStatus
from apps.tenants.models import Tenant


class LicensingTestCase(TestCase):
    """
    Shared fixtures for billing licensing tests.
    """

    def setUp(self):
        self.tenant = Tenant.objects.create(
            school_name="Demo School",
            subdomain_slug="demo",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=2,
            staff_license_limit=2,
            student_license_limit=2,
        )

        self.other_tenant = Tenant.objects.create(
            school_name="Other School",
            subdomain_slug="other",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=1,
            staff_license_limit=1,
            student_license_limit=1,
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

        self.other_teacher_role = Role.objects.create(
            tenant=self.other_tenant,
            name="Teacher",
            is_admin_role=False,
            license_category=Role.LicenseCategory.FACULTY,
        )

        self.academic_session = AcademicSession.objects.create(
            tenant=self.tenant,
            name="2026-2027",
            start_date=date(2026, 4, 1),
            end_date=date(2027, 3, 31),
            is_current=True,
        )

        self.class_level = ClassLevel.objects.create(
            tenant=self.tenant,
            name="Grade 1",
            sort_order=1,
        )

        self.section = Section.objects.create(
            tenant=self.tenant,
            academic_session=self.academic_session,
            class_level=self.class_level,
            name="A",
        )

    # ========================================================================
    # Selector Tests
    # ========================================================================

    def test_empty_tenant_has_zero_license_usage(self):
        self.assertEqual(
            count_active_admins(
                tenant=self.tenant,
            ),
            0,
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
            0,
        )

        self.assertEqual(
            count_active_students(
                tenant=self.tenant,
            ),
            0,
        )

    def test_active_staff_is_counted_by_license_category(self):
        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Admin",
            last_name="User",
            role=self.admin_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Teacher",
            last_name="One",
            role=self.teacher_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Accountant",
            last_name="One",
            role=self.staff_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        self.assertEqual(
            count_active_admins(
                tenant=self.tenant,
            ),
            1,
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
            1,
        )

    def test_inactive_staff_does_not_consume_license(self):
        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Inactive",
            last_name="Teacher",
            role=self.teacher_role,
            employment_status=EmploymentStatus.INACTIVE,
            joining_date=date.today(),
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            0,
        )

    def test_active_students_are_counted(self):
        Student._base_manager.create(
            tenant=self.tenant,
            student_code="STU-001",
            first_name="Hasan",
            last_name="One",
            dob=date(2019, 1, 1),
            gender="male",
            academic_session=self.academic_session,
            section=self.section,
            enrollment_date=date.today(),
            status=StudentStatus.ACTIVE,
        )

        Student._base_manager.create(
            tenant=self.tenant,
            student_code="STU-002",
            first_name="Hasan",
            last_name="Two",
            dob=date(2019, 2, 1),
            gender="male",
            academic_session=self.academic_session,
            section=self.section,
            enrollment_date=date.today(),
            status=StudentStatus.ACTIVE,
        )

        self.assertEqual(
            count_active_students(
                tenant=self.tenant,
            ),
            2,
        )

    def test_inactive_student_does_not_consume_license(self):
        Student._base_manager.create(
            tenant=self.tenant,
            student_code="STU-001",
            first_name="Inactive",
            last_name="Student",
            dob=date(2019, 1, 1),
            gender="male",
            academic_session=self.academic_session,
            section=self.section,
            enrollment_date=date.today(),
            status=StudentStatus.INACTIVE,
        )

        self.assertEqual(
            count_active_students(
                tenant=self.tenant,
            ),
            0,
        )

    def test_license_usage_is_tenant_scoped(self):
        Staff._base_manager.create(
            tenant=self.other_tenant,
            first_name="Other",
            last_name="Teacher",
            role=self.other_teacher_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.tenant,
            ),
            0,
        )

        self.assertEqual(
            count_active_faculty(
                tenant=self.other_tenant,
            ),
            1,
        )

    def test_license_status_contains_usage_limit_and_availability(self):
        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Teacher",
            last_name="One",
            role=self.teacher_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        status = get_license_status(
            tenant=self.tenant,
        )

        self.assertEqual(
            status[Role.LicenseCategory.FACULTY]["used"],
            1,
        )

        self.assertEqual(
            status[Role.LicenseCategory.FACULTY]["limit"],
            2,
        )

        self.assertEqual(
            status[Role.LicenseCategory.FACULTY]["available"],
            1,
        )

        self.assertFalse(
            status[Role.LicenseCategory.FACULTY]["at_capacity"],
        )

    # ========================================================================
    # Student License Tests
    # ========================================================================

    def test_student_license_available_when_capacity_exists(self):
        ensure_student_license_available(
            tenant=self.tenant,
        )

    def test_student_license_blocked_at_capacity(self):
        for index in range(2):
            Student._base_manager.create(
                tenant=self.tenant,
                student_code=f"STU-{index + 1:03d}",
                first_name="Student",
                last_name=str(index + 1),
                dob=date(2019, 1, 1),
                gender="male",
                academic_session=self.academic_session,
                section=self.section,
                enrollment_date=date.today(),
                status=StudentStatus.ACTIVE,
            )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Student license limit",
        ):
            ensure_student_license_available(
                tenant=self.tenant,
            )

    # ========================================================================
    # Staff License Tests
    # ========================================================================

    def test_staff_license_available_when_capacity_exists(self):
        ensure_staff_license_available(
            tenant=self.tenant,
            role=self.teacher_role,
        )

    def test_staff_license_blocked_at_capacity(self):
        for index in range(2):
            Staff._base_manager.create(
                tenant=self.tenant,
                first_name="Teacher",
                last_name=str(index + 1),
                role=self.teacher_role,
                employment_status=EmploymentStatus.ACTIVE,
                joining_date=date.today(),
            )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Faculty license limit",
        ):
            ensure_staff_license_available(
                tenant=self.tenant,
                role=self.teacher_role,
            )

    def test_staff_license_category_is_independent(self):
        for index in range(2):
            Staff._base_manager.create(
                tenant=self.tenant,
                first_name="Teacher",
                last_name=str(index + 1),
                role=self.teacher_role,
                employment_status=EmploymentStatus.ACTIVE,
                joining_date=date.today(),
            )

        ensure_staff_license_available(
            tenant=self.tenant,
            role=self.staff_role,
        )

    def test_inactive_staff_does_not_block_role_change(self):
        staff = Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Inactive",
            last_name="Teacher",
            role=self.teacher_role,
            employment_status=EmploymentStatus.INACTIVE,
            joining_date=date.today(),
        )

        for index in range(2):
            Staff._base_manager.create(
                tenant=self.tenant,
                first_name="Accountant",
                last_name=str(index + 1),
                role=self.staff_role,
                employment_status=EmploymentStatus.ACTIVE,
                joining_date=date.today(),
            )

        ensure_staff_role_change_available(
            tenant=self.tenant,
            staff=staff,
            new_role=self.staff_role,
        )

    def test_same_license_category_does_not_consume_extra_license(self):
        staff = Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Teacher",
            last_name="One",
            role=self.teacher_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        replacement_teacher_role = Role.objects.create(
            tenant=self.tenant,
            name="Senior Teacher",
            is_admin_role=False,
            license_category=Role.LicenseCategory.FACULTY,
        )

        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Teacher",
            last_name="Two",
            role=self.teacher_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        ensure_staff_role_change_available(
            tenant=self.tenant,
            staff=staff,
            new_role=replacement_teacher_role,
        )

    def test_role_change_to_full_category_is_blocked(self):
        staff = Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Teacher",
            last_name="One",
            role=self.teacher_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Accountant",
            last_name="One",
            role=self.staff_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        Staff._base_manager.create(
            tenant=self.tenant,
            first_name="Accountant",
            last_name="Two",
            role=self.staff_role,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=date.today(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You've reached your 2 Staff license limit",
        ):
            ensure_staff_role_change_available(
                tenant=self.tenant,
                staff=staff,
                new_role=self.staff_role,
            )

    def test_role_from_another_tenant_is_rejected(self):
        with self.assertRaisesMessage(
            ValidationError,
            "The selected role does not belong to the current tenant.",
        ):
            ensure_staff_license_available(
                tenant=self.tenant,
                role=self.other_teacher_role,
            )

    def test_license_limits_include_addons(self):
        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.FACULTY,
            quantity=10,
            stripe_line_item_id="li_faculty_123",
            purchased_at=timezone.now(),
        )

        limits = get_license_limits(
            tenant=self.tenant,
        )

        self.assertEqual(
            limits["admin"],
            self.tenant.admin_license_limit,
        )

        self.assertEqual(
            limits["faculty"],
            self.tenant.faculty_license_limit + 10,
        )

        self.assertEqual(
            limits["staff"],
            self.tenant.staff_license_limit,
        )

        self.assertEqual(
            limits["student"],
            self.tenant.student_license_limit,
        )


    def test_license_limits_include_addons_only_for_current_tenant(self):
        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=timezone.now(),
        )

        LicenseAddon.objects.create(
            tenant=self.other_tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=100,
            stripe_line_item_id="li_other_123",
            purchased_at=timezone.now(),
        )

        limits = get_license_limits(
            tenant=self.tenant,
        )

        self.assertEqual(
            limits["student"],
            self.tenant.student_license_limit + 25,
        )


    def test_license_status_uses_addon_adjusted_limits(self):
        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_student_123",
            purchased_at=timezone.now(),
        )

        status = get_license_status(
            tenant=self.tenant,
        )

        self.assertEqual(
            status["student"]["limit"],
            self.tenant.student_license_limit + 25,
        )