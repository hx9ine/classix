from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
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
from ..models import Exam, GradeEntry
from ..services import (
    create_exam,
    create_grade_entry,
    delete_exam,
    update_exam,
    update_grade_entry,
)


class GradesServiceTestMixin:
    @classmethod
    def create_tenant(cls, slug):
        return Tenant.objects.create(
            school_name=slug,
            subdomain_slug=slug,
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

    @classmethod
    def create_academic_session(
        cls,
        tenant,
        name="2026-2027",
    ):
        return AcademicSession.objects.create(
            tenant=tenant,
            name=name,
            start_date=date(2026, 9, 1),
            end_date=date(2027, 6, 30),
        )


class ExamServiceTests(
    GradesServiceTestMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = cls.create_tenant(
            "exam-service-test",
        )

        cls.other_tenant = cls.create_tenant(
            "other-exam-service-test",
        )

        cls.academic_session = cls.create_academic_session(
            cls.tenant,
        )

        cls.other_academic_session = cls.create_academic_session(
            cls.other_tenant,
        )

    def exam_form(
        self,
        *,
        tenant=None,
        instance=None,
        name="Term 1 Final",
        academic_session=None,
        start_date="2026-12-01",
        end_date="2026-12-10",
    ):
        tenant = tenant or self.tenant

        academic_session = (
            academic_session
            or self.academic_session
        )

        return ExamForm(
            data={
                "name": name,
                "academic_session": academic_session.pk,
                "start_date": start_date,
                "end_date": end_date,
            },
            instance=instance,
            tenant=tenant,
        )

    def create_exam_instance(self):
        form = self.exam_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        return create_exam(
            tenant=self.tenant,
            form=form,
        )

    def test_create_exam(self):
        exam = self.create_exam_instance()

        self.assertIsNotNone(
            exam.pk,
        )

        self.assertEqual(
            exam.tenant_id,
            self.tenant.pk,
        )

        self.assertEqual(
            exam.name,
            "Term 1 Final",
        )

    def test_create_exam_rejects_cross_tenant_academic_session(self):
        form = self.exam_form(
            academic_session=self.other_academic_session,
        )

        self.assertFalse(
            form.is_valid(),
        )

        self.assertIn(
            "academic_session",
            form.errors,
        )

    def test_update_exam(self):
        exam = self.create_exam_instance()

        form = self.exam_form(
            instance=exam,
            name="Term 1 Assessment",
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        updated = update_exam(
            exam=exam,
            form=form,
        )

        self.assertEqual(
            updated.pk,
            exam.pk,
        )

        self.assertEqual(
            updated.name,
            "Term 1 Assessment",
        )

        self.assertEqual(
            updated.tenant_id,
            self.tenant.pk,
        )

    def test_update_exam_rejects_exam_from_other_tenant(self):
        exam = Exam.objects.create(
            tenant=self.other_tenant,
            academic_session=self.other_academic_session,
            name="Other Exam",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        form = self.exam_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "The exam does not belong to the current tenant.",
        ):
            update_exam(
                exam=exam,
                form=form,
            )

    def test_delete_exam(self):
        exam = self.create_exam_instance()

        exam_id = exam.pk

        delete_exam(
            tenant=self.tenant,
            exam=exam,
        )

        self.assertFalse(
            Exam._base_manager.filter(
                pk=exam_id,
            ).exists(),
        )

    def test_delete_exam_rejects_other_tenant_exam(self):
        exam = Exam.objects.create(
            tenant=self.other_tenant,
            academic_session=self.other_academic_session,
            name="Other Exam",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "The exam does not belong to the current tenant.",
        ):
            delete_exam(
                tenant=self.tenant,
                exam=exam,
            )

        self.assertTrue(
            Exam._base_manager.filter(
                pk=exam.pk,
            ).exists(),
        )


class GradeEntryServiceTests(
    GradesServiceTestMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = cls.create_tenant(
            "grade-service-test",
        )

        cls.other_tenant = cls.create_tenant(
            "other-grade-service-test",
        )

        cls.academic_session = cls.create_academic_session(
            cls.tenant,
        )

        cls.other_academic_session = cls.create_academic_session(
            cls.other_tenant,
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

        cls.other_class_level = ClassLevel.objects.create(
            tenant=cls.other_tenant,
            name="Grade 1",
            sort_order=1,
        )

        cls.other_tenant_section = Section.objects.create(
            tenant=cls.other_tenant,
            academic_session=cls.other_academic_session,
            class_level=cls.other_class_level,
            name="A",
        )

        cls.student = Student.objects.create(
            tenant=cls.tenant,
            student_code="STU-001",
            first_name="Hasan",
            last_name="Student",
            dob=date(2019, 1, 1),
            gender=Gender.choices[0][0],
            academic_session=cls.academic_session,
            section=cls.section,
            enrollment_date=date(2026, 9, 1),
        )

        cls.other_section_student = Student.objects.create(
            tenant=cls.tenant,
            student_code="STU-002",
            first_name="Other",
            last_name="Section",
            dob=date(2019, 2, 1),
            gender=Gender.choices[0][0],
            academic_session=cls.academic_session,
            section=cls.other_section,
            enrollment_date=date(2026, 9, 1),
        )

        cls.other_tenant_student = Student.objects.create(
            tenant=cls.other_tenant,
            student_code="OTHER-001",
            first_name="Other",
            last_name="Tenant",
            dob=date(2019, 3, 1),
            gender=Gender.choices[0][0],
            academic_session=cls.other_academic_session,
            section=cls.other_tenant_section,
            enrollment_date=date(2026, 9, 1),
        )

        cls.exam = Exam.objects.create(
            tenant=cls.tenant,
            academic_session=cls.academic_session,
            name="Term 1 Final",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 10),
        )

        cls.other_exam = Exam.objects.create(
            tenant=cls.other_tenant,
            academic_session=cls.other_academic_session,
            name="Other Tenant Exam",
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

    def grade_form(
        self,
        *,
        tenant=None,
        instance=None,
        student=None,
        exam=None,
        subject=None,
        marks_obtained="85.00",
        max_marks="100.00",
        grade_letter="A",
        remarks="Good work.",
        staff=None,
    ):
        tenant = tenant or self.tenant
        student = student or self.student
        exam = exam or self.exam
        subject = subject or self.subject

        return GradeEntryForm(
            data={
                "student": student.pk,
                "exam": exam.pk,
                "subject": subject.pk,
                "marks_obtained": marks_obtained,
                "max_marks": max_marks,
                "grade_letter": grade_letter,
                "remarks": remarks,
            },
            instance=instance,
            tenant=tenant,
            staff=staff,
        )

    def create_grade_instance(
        self,
        *,
        staff=None,
    ):
        form = self.grade_form(
            staff=staff,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        return create_grade_entry(
            tenant=self.tenant,
            form=form,
            staff=staff,
        )

    def test_create_grade_entry(self):
        grade_entry = self.create_grade_instance()

        self.assertIsNotNone(
            grade_entry.pk,
        )

        self.assertEqual(
            grade_entry.tenant_id,
            self.tenant.pk,
        )

        self.assertEqual(
            grade_entry.marks_obtained,
            Decimal("85.00"),
        )

    def test_create_grade_entry_allows_teacher_assigned_scope(self):
        form = self.grade_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        grade_entry = create_grade_entry(
            tenant=self.tenant,
            form=form,
            staff=self.teacher,
        )

        self.assertEqual(
            grade_entry.student_id,
            self.student.pk,
        )

    def test_create_grade_entry_rejects_teacher_unassigned_scope(self):
        form = self.grade_form(
            student=self.other_section_student,
            subject=self.subject,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You can only manage grades for your assigned "
            "sections and subjects.",
        ):
            create_grade_entry(
                tenant=self.tenant,
                form=form,
                staff=self.teacher,
            )

    def test_create_grade_entry_rejects_cross_tenant_student(self):
        form = self.grade_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        form.instance.student = self.other_tenant_student

        with self.assertRaisesMessage(
            ValidationError,
            "The selected student does not belong to the current tenant.",
        ):
            create_grade_entry(
                tenant=self.tenant,
                form=form,
            )

    def test_create_grade_entry_rejects_cross_tenant_exam(self):
        form = self.grade_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        form.instance.exam = self.other_exam

        with self.assertRaisesMessage(
            ValidationError,
            "The selected exam does not belong to the current tenant.",
        ):
            create_grade_entry(
                tenant=self.tenant,
                form=form,
            )

    def test_create_grade_entry_rejects_cross_tenant_subject(self):
        other_subject = Subject.objects.create(
            tenant=self.other_tenant,
            name="Other English",
            code="OTHER-ENG",
        )

        form = self.grade_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        form.instance.subject = other_subject

        with self.assertRaisesMessage(
            ValidationError,
            "The selected subject does not belong to the current tenant.",
        ):
            create_grade_entry(
                tenant=self.tenant,
                form=form,
            )

    def test_update_grade_entry(self):
        grade_entry = self.create_grade_instance()

        form = self.grade_form(
            instance=grade_entry,
            marks_obtained="92.00",
            grade_letter="A+",
            remarks="Excellent work.",
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        updated = update_grade_entry(
            grade_entry=grade_entry,
            form=form,
        )

        self.assertEqual(
            updated.pk,
            grade_entry.pk,
        )

        self.assertEqual(
            updated.marks_obtained,
            Decimal("92.00"),
        )

        self.assertEqual(
            updated.grade_letter,
            "A+",
        )

        self.assertEqual(
            updated.remarks,
            "Excellent work.",
        )

    def test_update_grade_entry_rejects_cross_tenant_grade_entry(self):
        other_subject = Subject.objects.create(
            tenant=self.other_tenant,
            name="Other Subject",
            code="OTHER-SUB",
        )

        other_grade_entry = GradeEntry.objects.create(
            tenant=self.other_tenant,
            student=self.other_tenant_student,
            exam=self.other_exam,
            subject=other_subject,
            marks_obtained="80.00",
            max_marks="100.00",
            grade_letter="B",
            remarks="Other tenant.",
        )

        form = self.grade_form()

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "The grade entry does not belong to the current tenant.",
        ):
            update_grade_entry(
                grade_entry=other_grade_entry,
                form=form,
            )

    def test_update_grade_entry_enforces_resulting_teacher_scope(self):
        grade_entry = self.create_grade_instance()

        form = self.grade_form(
            instance=grade_entry,
            student=self.other_section_student,
            subject=self.subject,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "You can only manage grades for your assigned "
            "sections and subjects.",
        ):
            update_grade_entry(
                grade_entry=grade_entry,
                form=form,
                staff=self.teacher,
            )