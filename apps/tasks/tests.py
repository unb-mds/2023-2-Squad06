from datetime import timedelta

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from apps.contests.models import Contest
from apps.tasks.admin import TaskAdmin
from apps.tasks.models import Task
from apps.tasks.views import DetailView


class TaskTestCase(TestCase):
    def test_task_to_string(self) -> None:
        task = Task(title="Test Task")
        self.assertEqual(str(task), "Test Task")

    def test_running_contest_is_accessible(self) -> None:
        now = timezone.now()

        start_time = now - timedelta(hours=1)
        end_time = now + timedelta(hours=1)

        contest = Contest(start_time=start_time, end_time=end_time)
        task = Task(contest=contest)

        self.assertTrue(task.is_accessible)

    def test_past_contest_is_accessible(self) -> None:
        now = timezone.now()

        start_time = now - timedelta(hours=2)
        end_time = now - timedelta(hours=1)

        contest = Contest(start_time=start_time, end_time=end_time)
        task = Task(contest=contest)

        self.assertTrue(task.is_accessible)

    def test_future_contest_is_not_accessible(self) -> None:
        now = timezone.now()

        start_time = now + timedelta(hours=1)
        end_time = now + timedelta(hours=2)

        contest = Contest(start_time=start_time, end_time=end_time)
        task = Task(contest=contest)

        self.assertFalse(task.is_accessible)

    def test_cancelled_contest_is_not_accessible(self) -> None:
        now = timezone.now()

        start_time = now - timedelta(hours=1)
        end_time = now + timedelta(hours=1)

        contest = Contest(
            start_time=start_time,
            end_time=end_time,
            cancelled=True,
        )
        task = Task(contest=contest)

        self.assertFalse(task.is_accessible)


class TaskAdminTestCase(TestCase):
    def setUp(self) -> None:
        now = timezone.now()
        self.site = AdminSite()
        self.admin = TaskAdmin(Task, self.site)

        self.contest = Contest._default_manager.create(
            title="Test Contest 1",
            description="This is a test contest",
            start_time=now,
            end_time=now + timedelta(hours=1),
            cancelled=False,
        )
        self.contest.save()

    def test_list_display(self) -> None:
        list_display = self.admin.list_display
        expected = ("title", "contest", "memory_limit", "time_limit")

        self.assertEqual(list_display, expected)

    def test_list_filter(self) -> None:
        list_filter = self.admin.list_filter
        expected = ("contest", "score")

        self.assertEqual(list_filter, expected)

    def test_fieldsets(self) -> None:
        fieldsets = self.admin.fieldsets
        expected = [
            (("General"), {"fields": ("title", "description")}),
            (("Meta"), {"fields": ("contest", "score")}),
            (("Limits"), {"fields": ("memory_limit", "time_limit")}),
        ]

        self.assertEqual(fieldsets, expected)


class TaskURLTestCase(TestCase):
    def test_detail_url_to_view_name(self) -> None:
        url = reverse("tasks:detail", args=[1])

        view_name = resolve(url).view_name
        expected = "tasks:detail"

        self.assertEqual(view_name, expected)

    def test_detail_url_reverse(self) -> None:
        url = reverse("tasks:detail", args=[1])
        expected = "/tasks/1/"

        self.assertEqual(url, expected)


class DetailViewTestCase(TestCase):
    def test_detail_view_model_is_task(self) -> None:
        self.assertEqual(DetailView.model, Task)

    def test_detail_view_template_name_is_correct(self) -> None:
        self.assertEqual(DetailView.template_name, "tasks/detail.html")