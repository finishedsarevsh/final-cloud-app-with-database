from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Enrollment, Question, Choice, Submission


class ExamTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', first_name='Test')
        self.course = Course.objects.create(name='Test Course', description='Test Description')
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)

        # Question 1: single choice, 50 points
        self.q1 = Question.objects.create(course=self.course, question_text="What is Django?", grade=50)
        self.c1_1 = Choice.objects.create(question=self.q1, choice_text="A Python web framework", is_correct=True)
        self.c1_2 = Choice.objects.create(question=self.q1, choice_text="A database", is_correct=False)

        # Question 2: multi choice, 50 points
        self.q2 = Question.objects.create(course=self.course, question_text="Which are HTTP methods?", grade=50)
        self.c2_1 = Choice.objects.create(question=self.q2, choice_text="GET", is_correct=True)
        self.c2_2 = Choice.objects.create(question=self.q2, choice_text="POST", is_correct=True)
        self.c2_3 = Choice.objects.create(question=self.q2, choice_text="INVALID", is_correct=False)

    def test_is_get_score(self):
        # Q1: correct
        self.assertTrue(self.q1.is_get_score([self.c1_1.id]))
        # Q1: incorrect
        self.assertFalse(self.q1.is_get_score([self.c1_2.id]))
        # Q1: both selected (incorrect selected)
        self.assertFalse(self.q1.is_get_score([self.c1_1.id, self.c1_2.id]))
        # Q1: empty
        self.assertFalse(self.q1.is_get_score([]))

        # Q2: all correct
        self.assertTrue(self.q2.is_get_score([self.c2_1.id, self.c2_2.id]))
        # Q2: partial
        self.assertFalse(self.q2.is_get_score([self.c2_1.id]))
        # Q2: correct plus incorrect
        self.assertFalse(self.q2.is_get_score([self.c2_1.id, self.c2_2.id, self.c2_3.id]))

    def test_submission_and_result_passed(self):
        client = Client()
        client.login(username='testuser', password='password123')

        # Submit full score
        submit_url = reverse('onlinecourse:submit', args=[self.course.id])
        post_data = {
            f'choice_{self.c1_1.id}': self.c1_1.id,
            f'choice_{self.c2_1.id}': self.c2_1.id,
            f'choice_{self.c2_2.id}': self.c2_2.id,
        }
        response = client.post(submit_url, post_data)
        self.assertEqual(response.status_code, 302)

        # Follow redirect to exam result
        submission = Submission.objects.filter(enrollment=self.enrollment).last()
        self.assertIsNotNone(submission)
        result_url = reverse('onlinecourse:show_exam_result', args=[self.course.id, submission.id])
        self.assertRedirects(response, result_url)

        res_page = client.get(result_url)
        self.assertEqual(res_page.status_code, 200)
        self.assertContains(res_page, "Congratulations, Test!")
        self.assertContains(res_page, "score 100/100")
        self.assertIn('possible', res_page.context)

    def test_submission_and_result_failed(self):
        client = Client()
        client.login(username='testuser', password='password123')

        # Submit partial score (only Q1 correct: 50%)
        submit_url = reverse('onlinecourse:submit', args=[self.course.id])
        post_data = {
            f'choice_{self.c1_1.id}': self.c1_1.id,
        }
        response = client.post(submit_url, post_data)
        self.assertEqual(response.status_code, 302)

        submission = Submission.objects.filter(enrollment=self.enrollment).last()
        result_url = reverse('onlinecourse:show_exam_result', args=[self.course.id, submission.id])
        res_page = client.get(result_url)
        self.assertEqual(res_page.status_code, 200)
        self.assertContains(res_page, "Failed!")
        self.assertContains(res_page, "score 50/100")
        self.assertContains(res_page, "Re-test")
