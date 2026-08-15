from datetime import date
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from apps.academic_structure.models import (
    AcademicSession,
    ClassLevel,
    Section,
)
from apps.academics.models import Subject
from apps.core.choices import Gender
from apps.students.models import Student
from apps.tenants.models import Tenant

from ..models import Exam, GradeEntry


class ExamModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            school_name="Grades Test School",
            subdomain_slug="grades-model-test",
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

    def test_exam_string_representation(self):
        exam = Exam.objects.create(
            tenant=self.tenant,
            academic_session=self.academic_session,
            name="Term 1 Final",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        self.assertEqual(
            str(exam),
            "Term 1 Final",
        )

    def test_exam_belongs_to_tenant(self):
        exam = Exam.objects.create(
            tenant=self.tenant,
            academic_session=self.academic_session,
            name="Term 1 Final",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        self.assertEqual(
            exam.tenant_id,
            self.tenant.pk,
        )

    def test_exam_belongs_to_academic_session(self):
        exam = Exam.objects.create(
            tenant=self.tenant,
            academic_session=self.academic_session,
            name="Term 1 Final",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        self.assertEqual(
            exam.academic_session_id,
            self.academic_session.pk,
        )


class GradeEntryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            school_name="Grade Entry Test School",
            subdomain_slug="grade-entry-model-test",
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

        cls.subject = Subject.objects.create(
            tenant=cls.tenant,
            name="English",
            code="ENG",
        )

        cls.student = Student.objects.create(
            tenant=cls.tenant,
            student_code="STU-001",
            first_name="Hasan",
            last_name="Student",
            dob=date(2019, 1, 1),
            gender=Gender.MALE,
            academic_session=cls.academic_session,
            section=cls.section,
            enrollment_date=date(2026, 9, 1),
        )

        cls.exam = Exam.objects.create(
            tenant=cls.tenant,
            academic_session=cls.academic_session,
            name="Term 1 Final",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

    def test_grade_entry_string_representation(self):
        grade_entry = GradeEntry.objects.create(
            tenant=self.tenant,
            student=self.student,
            exam=self.exam,
            subject=self.subject,
            marks_obtained=Decimal("85.00"),
            max_marks=Decimal("100.00"),
            grade_letter="A",
        )

        self.assertEqual(
            str(grade_entry),
            (
                f"{self.student} - "
                f"{self.subject} - "
                f"{self.exam}"
            ),
        )

    def test_grade_entry_belongs_to_tenant(self):
        grade_entry = GradeEntry.objects.create(
            tenant=self.tenant,
            student=self.student,
            exam=self.exam,
            subject=self.subject,
            marks_obtained=Decimal("85.00"),
            max_marks=Decimal("100.00"),
        )

        self.assertEqual(
            grade_entry.tenant_id,
            self.tenant.pk,
        )

    def test_grade_entry_stores_marks(self):
        grade_entry = GradeEntry.objects.create(
            tenant=self.tenant,
            student=self.student,
            exam=self.exam,
            subject=self.subject,
            marks_obtained=Decimal("85.50"),
            max_marks=Decimal("100.00"),
            grade_letter="A",
            remarks="Good work.",
        )

        self.assertEqual(
            grade_entry.marks_obtained,
            Decimal("85.50"),
        )

        self.assertEqual(
            grade_entry.max_marks,
            Decimal("100.00"),
        )

        self.assertEqual(
            grade_entry.grade_letter,
            "A",
        )

        self.assertEqual(
            grade_entry.remarks,
            "Good work.",
        )

    def test_student_exam_subject_combination_is_unique(self):
        GradeEntry.objects.create(
            tenant=self.tenant,
            student=self.student,
            exam=self.exam,
            subject=self.subject,
            marks_obtained=Decimal("80.00"),
            max_marks=Decimal("100.00"),
        )

        with self.assertRaises(IntegrityError):
            GradeEntry.objects.create(
                tenant=self.tenant,
                student=self.student,
                exam=self.exam,
                subject=self.subject,
                marks_obtained=Decimal("90.00"),
                max_marks=Decimal("100.00"),
            )

    def test_grade_letter_and_remarks_can_be_blank(self):
        grade_entry = GradeEntry.objects.create(
            tenant=self.tenant,
            student=self.student,
            exam=self.exam,
            subject=self.subject,
            marks_obtained=Decimal("70.00"),
            max_marks=Decimal("100.00"),
        )

        self.assertEqual(
            grade_entry.grade_letter,
            "",
        )

        self.assertEqual(
            grade_entry.remarks,
            "",
        )