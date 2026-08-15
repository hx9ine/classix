from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic_structure.models import (
    AcademicSession,
    ClassLevel,
    Section,
)
from apps.academics.models import Subject, TimetablePeriod
from apps.core.choices import Gender
from apps.rbac.models import Role
from apps.staff.models import Staff
from apps.students.models import Student
from apps.tenants.models import Tenant

from ..forms import ExamForm, GradeEntryForm
from ..models import Exam


class ExamFormTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            school_name="Exam Form Test School",
            subdomain_slug="exam-form-test",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        cls.academic_session = AcademicSession.objects.create(
            tenant=cls.tenant,
            name="2026-2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
        )

    def test_valid_exam_form(self):
        form = ExamForm(
            data={
                "name": "Term 1 Final",
                "academic_session": self.academic_session.pk,
                "start_date": "2026-12-01",
                "end_date": "2026-12-10",
            },
            tenant=self.tenant,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

    def test_exam_name_is_stripped(self):
        form = ExamForm(
            data={
                "name": "  Term 1 Final  ",
                "academic_session": self.academic_session.pk,
                "start_date": "2026-12-01",
                "end_date": "2026-12-10",
            },
            tenant=self.tenant,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        self.assertEqual(
            form.cleaned_data["name"],
            "Term 1 Final",
        )

    def test_end_date_cannot_be_before_start_date(self):
        form = ExamForm(
            data={
                "name": "Invalid Exam",
                "academic_session": self.academic_session.pk,
                "start_date": "2026-12-10",
                "end_date": "2026-12-01",
            },
            tenant=self.tenant,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "End date cannot be earlier than start date.",
            form.non_field_errors(),
        )

    def test_academic_session_queryset_is_tenant_scoped(self):
        other_tenant = Tenant.objects.create(
            school_name="Other School",
            subdomain_slug="other-exam-form-test",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        other_session = AcademicSession.objects.create(
            tenant=other_tenant,
            name="2026-2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
        )

        form = ExamForm(
            tenant=self.tenant,
        )

        self.assertTrue(
            form.fields["academic_session"]
            .queryset
            .filter(pk=self.academic_session.pk)
            .exists()
        )

        self.assertFalse(
            form.fields["academic_session"]
            .queryset
            .filter(pk=other_session.pk)
            .exists()
        )


class GradeEntryFormTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            school_name="Grade Form Test School",
            subdomain_slug="grade-form-test",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        cls.academic_session = AcademicSession.objects.create(
            tenant=cls.tenant,
            name="2026-2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
        )

        cls.class_level = ClassLevel.objects.create(
            tenant=cls.tenant,
            name="Grade 1",
            sort_order=1,
        )

        cls.section = Section.objects.create(
            tenant=cls.tenant,
            academic_session=cls.academic_session,
            class_level=cls.class_level,
            name="A",
        )

        cls.other_section = Section.objects.create(
            tenant=cls.tenant,
            academic_session=cls.academic_session,
            class_level=cls.class_level,
            name="B",
        )

        cls.subject = Subject.objects.create(
            tenant=cls.tenant,
            name="English",
            code="ENG",
        )

        cls.other_subject = Subject.objects.create(
            tenant=cls.tenant,
            name="Mathematics",
            code="MATH",
        )

        gender_value = Gender.choices[0][0]

        cls.student = Student.objects.create(
            tenant=cls.tenant,
            student_code="STU-001",
            first_name="Hasan",
            last_name="Student",
            dob=date(2019, 1, 1),
            gender=gender_value,
            academic_session=cls.academic_session,
            section=cls.section,
            enrollment_date=date(2026, 9, 1),
        )

        cls.other_student = Student.objects.create(
            tenant=cls.tenant,
            student_code="STU-002",
            first_name="Other",
            last_name="Student",
            dob=date(2019, 2, 1),
            gender=gender_value,
            academic_session=cls.academic_session,
            section=cls.other_section,
            enrollment_date=date(2026, 9, 1),
        )

        cls.exam = Exam.objects.create(
            tenant=cls.tenant,
            academic_session=cls.academic_session,
            name="Term 1 Final",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        cls.teacher_role = Role.objects.create(
            tenant=cls.tenant,
            name="Teacher",
            is_admin_role=False,
            license_category=Role.LicenseCategory.FACULTY,
        )

        cls.teacher = Staff._base_manager.create(
            tenant=cls.tenant,
            first_name="Demo",
            last_name="Teacher",
            role=cls.teacher_role,
            joining_date=date(2026, 9, 1),
        )

        TimetablePeriod.objects.create(
            tenant=cls.tenant,
            section=cls.section,
            subject=cls.subject,
            staff=cls.teacher,
            day_of_week=0,
            start_time="09:00",
            end_time="10:00",
        )

    def _valid_data(self):
        return {
            "student": self.student.pk,
            "exam": self.exam.pk,
            "subject": self.subject.pk,
            "marks_obtained": "85.00",
            "max_marks": "100.00",
            "grade_letter": "A",
            "remarks": "Good work.",
        }

    def test_valid_grade_entry_form(self):
        form = GradeEntryForm(
            data=self._valid_data(),
            tenant=self.tenant,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

    def test_marks_obtained_cannot_be_negative(self):
        data = self._valid_data()
        data["marks_obtained"] = "-1"

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "Marks obtained cannot be negative.",
            form.errors["marks_obtained"],
        )

    def test_max_marks_must_be_greater_than_zero(self):
        data = self._valid_data()
        data["max_marks"] = "0"

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "Maximum marks must be greater than zero.",
            form.errors["max_marks"],
        )

    def test_marks_obtained_cannot_exceed_max_marks(self):
        data = self._valid_data()
        data["marks_obtained"] = "101"
        data["max_marks"] = "100"

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "Marks obtained cannot exceed maximum marks.",
            form.errors["marks_obtained"],
        )

    def test_grade_letter_is_stripped(self):
        data = self._valid_data()
        data["grade_letter"] = "  A  "

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        self.assertEqual(
            form.cleaned_data["grade_letter"],
            "A",
        )

    def test_remarks_are_stripped(self):
        data = self._valid_data()
        data["remarks"] = "  Good work.  "

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        self.assertEqual(
            form.cleaned_data["remarks"],
            "Good work.",
        )

    def test_student_queryset_is_tenant_scoped(self):
        other_tenant = Tenant.objects.create(
            school_name="Other School",
            subdomain_slug="other-grade-form-test",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        other_session = AcademicSession.objects.create(
            tenant=other_tenant,
            name="2026-2027",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
        )

        other_class_level = ClassLevel.objects.create(
            tenant=other_tenant,
            name="Grade 1",
            sort_order=1,
        )

        other_section = Section.objects.create(
            tenant=other_tenant,
            academic_session=other_session,
            class_level=other_class_level,
            name="A",
        )

        other_student = Student.objects.create(
            tenant=other_tenant,
            student_code="OTHER-001",
            first_name="Other",
            last_name="Tenant",
            dob=date(2019, 1, 1),
            gender=Gender.choices[0][0],
            academic_session=other_session,
            section=other_section,
            enrollment_date=date(2026, 9, 1),
        )

        form = GradeEntryForm(
            tenant=self.tenant,
        )

        self.assertTrue(
            form.fields["student"]
            .queryset
            .filter(pk=self.student.pk)
            .exists()
        )

        self.assertFalse(
            form.fields["student"]
            .queryset
            .filter(pk=other_student.pk)
            .exists()
        )

    def test_exam_queryset_is_tenant_scoped(self):
        form = GradeEntryForm(
            tenant=self.tenant,
        )

        self.assertTrue(
            form.fields["exam"]
            .queryset
            .filter(pk=self.exam.pk)
            .exists()
        )

    def test_subject_queryset_is_tenant_scoped(self):
        form = GradeEntryForm(
            tenant=self.tenant,
        )

        self.assertTrue(
            form.fields["subject"]
            .queryset
            .filter(pk=self.subject.pk)
            .exists()
        )

        self.assertTrue(
            form.fields["subject"]
            .queryset
            .filter(pk=self.other_subject.pk)
            .exists()
        )

    def test_teacher_student_queryset_is_assignment_scoped(self):
        form = GradeEntryForm(
            tenant=self.tenant,
            staff=self.teacher,
        )

        self.assertTrue(
            form.fields["student"]
            .queryset
            .filter(pk=self.student.pk)
            .exists()
        )

        self.assertFalse(
            form.fields["student"]
            .queryset
            .filter(pk=self.other_student.pk)
            .exists()
        )

    def test_teacher_subject_queryset_is_assignment_scoped(self):
        form = GradeEntryForm(
            tenant=self.tenant,
            staff=self.teacher,
        )

        self.assertTrue(
            form.fields["subject"]
            .queryset
            .filter(pk=self.subject.pk)
            .exists()
        )

        self.assertFalse(
            form.fields["subject"]
            .queryset
            .filter(pk=self.other_subject.pk)
            .exists()
        )

    def test_teacher_cannot_submit_unassigned_subject(self):
        data = self._valid_data()
        data["subject"] = self.other_subject.pk

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
            staff=self.teacher,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "subject",
            form.errors,
        )

    def test_teacher_cannot_submit_student_from_unassigned_section(self):
        data = self._valid_data()
        data["student"] = self.other_student.pk

        form = GradeEntryForm(
            data=data,
            tenant=self.tenant,
            staff=self.teacher,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "student",
            form.errors,
        )