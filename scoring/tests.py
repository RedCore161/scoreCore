from django.test import TestCase
from .models import *


def create_ImageScore(project, idx, image_file, data):
    image_score = ImageScore.objects.create(project=project,
                                            user=User.objects.get(username=f"Tester{idx}"),
                                            file=image_file,
                                            s_eye=data[0],
                                            s_nose=data[1],
                                            s_cheek=data[2],
                                            s_ear=data[3],
                                            s_whiskers=data[4],
                                            date=timezone.now())
    image_score.save()


class GeneralTestCase(TestCase):
    _name = "Test"

    def setUp(self):

        for i in range(10):
            user = User.objects.create(username=f"Tester{i}", password="geheim")
            user.save()

        project = Project.objects.create(name="Test-Project")
        for user in User.objects.all():
            project.users.add(user)
        project.save()

        for i in range(25):
            image_file = ImageFile.objects.create(project=project,
                                                  filename=f"{i}.png",
                                                  path="",
                                                  date=timezone.now())
            image_file.save()

    def test_calculate_similarity(self):

        project = Project.objects.get(name="Test-Project")
        image_files = ImageFile.objects.all()
        pos = 0

        tests = [
            {"expected": 5,     "data": ["00000", "11111"]},
            {"expected": 10,    "data": ["00000", "22222"]},
            {"expected": 10,    "data": ["00000", "22222", "11111"]},
            {"expected": 8,     "data": ["00000", "00000", "11112"]},
            {"expected": 15,    "data": ["00000", "22222", "11111", "00000"]},
            {"expected": 7.66,  "data": ["01002", "10102", "11112", "11112", "11112", "11112"]},
            {"expected": 6.66,  "data": ["01002", "10112", "11112", "11112", "11112", "11112"]},
            {"expected": 11.5,  "data": ["01201", "20120", "10101", "12100"]},
            {"expected": 1.5,   "data": ["01201", "01201", "01201", "01211"]},
            {"expected": 0,     "data": ["01201", "01201", "01201", "01201"]},
            {"expected": 0,     "data": ["01201"]},
        ]

        for _test in tests:

            image_file = image_files[pos]
            pos += 1
            for idx, data in enumerate(_test.get("data")):
                create_ImageScore(project, idx, image_file, data)

            #print(image_file, image_file.scores.all())
            self.assertEqual(image_file.calc_similarity(), _test.get("expected"))
