from django.test import TestCase
from .models import *
from .views.viewsets.viewset_creator import ViewSetCreateModel


def create_ImageScore(project, idx, image_file, data):

    s_eye = data[0] if data[0] != " " else None
    s_nose = data[1] if data[1] != " " else None
    s_cheek = data[2] if data[2] != " " else None
    s_ear = data[3] if data[3] != " " else None
    s_whiskers = data[4] if data[4] != " " else None

    image_score = ImageScore.objects.create(project=project,
                                            user=User.objects.get(username=f"Tester{idx}"),
                                            file=image_file,
                                            s_eye=s_eye,
                                            s_nose=s_nose,
                                            s_cheek=s_cheek,
                                            s_ear=s_ear,
                                            s_whiskers=s_whiskers,
                                            date=timezone.now())
    image_score.save()


class GeneralTestCase(TestCase):
    _name = "Test"

    def setUp(self):

        for i in range(10):
            user = User.objects.create(username=f"Tester{i}", password="geheim")
            user.save()

        project = Project.objects.create(name="Test-Project", wanted_scores_per_user=4, wanted_scores_per_image=2)
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
            {"expected": 2.5,   "data": ["00000", "11111"]},
            {"expected": 8,     "data": ["00000", "22 22"]},
            {"expected": 10,    "data": ["00000", "22222"]},
            {"expected": 5,     "data": ["00000", "22222", "11111"]},
            {"expected": 2.65,  "data": ["00000", "00000", "11112"]},
            {"expected": 4.6,   "data": ["00000", "22222", "11111", "00000"]},
            {"expected": 0.78,  "data": ["01002", "10102", "11112", "11112", "11112", "11112"]},
            {"expected": 0.68,  "data": ["01002", "10112", "11112", "11112", "11112", "11112"]},
            {"expected": 3.17,  "data": ["01201", "20120", "10101", "12100"]},
            {"expected": 0.25,  "data": ["01201", "01201", "01201", "01211"]},
            {"expected": 0,     "data": ["01201", "01201", "01201", "01201"]},
            {"expected": 0,     "data": ["01201"]},
        ]

        for _test in tests:

            image_file = image_files[pos]
            pos += 1
            for idx, data in enumerate(_test.get("data")):
                create_ImageScore(project, idx, image_file, data)

            #print(image_file, image_file.scores.all())
            self.assertEqual(image_file.calc_varianz(), _test.get("expected"))


    def test_scoring(self):

        project = Project.objects.get(name="Test-Project")
        image_files = project.files.all()
        user1 = User.objects.get(username=f"Tester{1}")
        user2 = User.objects.get(username=f"Tester{2}")
        tests = [
            {"user": user1, "image_file": image_files[0], "data": "01201", "start": 4, "end": 3, "existing_scores": 0},
            {"user": user1, "image_file": image_files[1], "data": "10101", "start": 3, "end": 2, "existing_scores": 1},
            {"user": user2, "image_file": image_files[1], "data": "10101", "start": 4, "end": 3, "existing_scores": 2},
            {"user": user2, "image_file": image_files[2], "data": "10101", "start": 3, "end": 2, "existing_scores": 3},
            {"user": user2, "image_file": image_files[3], "data": "10101", "start": 2, "end": 1, "existing_scores": 4},
            {"user": user2, "image_file": image_files[4], "data": "10101", "start": 1, "end": 0, "existing_scores": 5},
        ]

        i = 0
        for test in tests:
            i += 1
            print(f"Starting 'test_scoring' - Run {i} of {len(tests)}")
            data = ViewSetCreateModel.get_images(project.pk, test.get("user")).data
            #print("1", len(project.scores.all()), len(data.get("image")), data.get("files_left"))
            self.assertEqual(data.get("files_left"), test.get("start"))
            self.assertEqual(len(project.scores.all()), test.get("existing_scores"))

            d = test.get("data")
            ViewSetCreateModel.create_imagescore(image_files[0].pk, test.get("user"), d[0], d[1], d[2], d[3], d[4])
            data = ViewSetCreateModel.get_images(project.pk, test.get("user")).data
            #print("2", len(project.scores.all()), len(data.get("image")), data.get("files_left"))
            self.assertEqual(data.get("files_left"), test.get("end"))
            self.assertEqual(len(project.scores.all()), test.get("existing_scores") + 1)
