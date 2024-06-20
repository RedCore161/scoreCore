from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.test import TestCase
from django.utils import timezone

from .models import Project
from .views.viewsets.viewset_creator import ViewSetCreateModel


class GeneralTestCase(TestCase):
    _name = "Test"
    
    wanted_scores_per_user = 10
    wanted_scores_per_image = 6
    
    user_count = 10
    image_files_count = 15
    
    def setUp(self):

        for i in range(self.user_count):
            user = User.objects.create(username=f"Tester{i}", password="geheim")
            user.save()

        project = Project.objects.create(name="Test-Project",
                                         wanted_scores_per_user=self.wanted_scores_per_user,
                                         wanted_scores_per_image=self.wanted_scores_per_image)
        for user in User.objects.all():
            project.users.add(user)
        project.save()

        for i in range(self.image_files_count):
            image_file = ImageFile.objects.create(project=project,
                                                  filename=f"{i}.png",
                                                  path="",
                                                  date=timezone.now())
            image_file.save()

    def test_calculate_similarity(self):

        project = Project.objects.get(name="Test-Project")
        image_files = project.get_all_files_save()
        pos = 0

        tests = [
            {"expected": 2.5,   "data": ["00000", "11111"]},
            {"expected": 4,     "data": ["00000", "22X22"]},
            {"expected": 5,     "data": ["00000", "22222"]},
            {"expected": 4.1,   "data": ["00000", "22222", "11111"]},
            {"expected": 2.82,  "data": ["00000", "00000", "11112"]},
            {"expected": 4.15,  "data": ["00000", "22222", "11111", "00000"]},
            {"expected": 1.58,  "data": ["01002", "10102", "11112", "11112", "11112", "11112"]},
            {"expected": 1.48,  "data": ["01002", "10112", "11112", "11112", "11112", "11112"]},
            {"expected": 3.34,  "data": ["01201", "20120", "10101", "12100"]},
            {"expected": 0.43,  "data": ["01201", "01201", "01201", "01211"]},
            {"expected": 0,     "data": ["01201", "01201", "01201", "01201"]},
            {"expected": 0,     "data": ["01201"]},
        ]

        _fixxed_files = list(image_files)

        for _test in tests:

            image_file = _fixxed_files[pos]
            pos += 1

            for idx, data in enumerate(_test.get("data")):
                user = User.objects.get(username=f"Tester{idx}")
                ViewSetCreateModel().create_or_update_imagescore(image_file.pk, user, data)

            self.assertEqual(image_file.calc_std_dev(), _test.get("expected"))

    def test_scoring(self):

        project = Project.objects.get(name="Test-Project")

        users = {
            "1": User.objects.get(username=f"Tester{1}"),
            "2": User.objects.get(username=f"Tester{2}"),
            "3": User.objects.get(username=f"Tester{3}"),
            "4": User.objects.get(username=f"Tester{4}"),
            "5": User.objects.get(username=f"Tester{5}"),
        }

        fi_le = self.wanted_scores_per_user

        tests = [
            {"user": users.get("1"), "data": "01201", "files_left": fi_le-0, "ratio": 0},
            {"user": users.get("1"), "data": "10101", "files_left": fi_le-1, "ratio": 0},

            {"user": users.get("2"), "data": "10101", "files_left": fi_le-0, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-1, "ratio": 0},
            {"user": users.get("2"), "data": "1X101", "files_left": fi_le-2, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-3, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-4, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-5, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-6, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-7, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-8, "ratio": 0},
            {"user": users.get("2"), "data": "10101", "files_left": fi_le-9, "ratio": 0},

            {"user": users.get("3"), "data": "10102", "files_left": fi_le-0, "ratio": 0},
            {"user": users.get("3"), "data": "10101", "files_left": fi_le-1, "ratio": 0},

            {"user": users.get("4"), "data": "22222", "files_left": fi_le-0, "ratio": 1},
            {"user": users.get("4"), "data": "2X2X2", "files_left": fi_le-1, "ratio": 1},
            {"user": users.get("4"), "data": "22222", "files_left": fi_le-2, "ratio": 1},
            {"user": users.get("4"), "data": "2X2X2", "files_left": fi_le-3, "ratio": 1},

            {"user": users.get("3"), "data": "10101", "files_left": fi_le-2, "ratio": 1},
            {"user": users.get("3"), "data": "101X1", "files_left": fi_le-3, "ratio": 1},
            {"user": users.get("3"), "data": "10102", "files_left": fi_le-4, "ratio": 1},
            {"user": users.get("3"), "data": "10101", "files_left": fi_le-5, "ratio": 1},
            {"user": users.get("3"), "data": "10X01", "files_left": fi_le-6, "ratio": 1},
            {"user": users.get("3"), "data": "10101", "files_left": fi_le-7, "ratio": 1},
            {"user": users.get("3"), "data": "10101", "files_left": fi_le-8, "ratio": 1},
            {"user": users.get("3"), "data": "10201", "files_left": fi_le-9, "ratio": 1},

            {"user": users.get("5"), "data": "01011", "files_left": fi_le-0, "ratio": 1},
            {"user": users.get("5"), "data": "01011", "files_left": fi_le-1, "ratio": 1},
            {"user": users.get("5"), "data": "01011", "files_left": fi_le-2, "ratio": 1},
            {"user": users.get("5"), "data": "01011", "files_left": fi_le-3, "ratio": 2},

        ]


        for idx, test in enumerate(tests):
            print(f"Starting 'test_scoring' - Run {idx+1} of {len(tests)}")
            data = ViewSetCreateModel.get_next_image(project.pk, test.get("user")).data
            self.assertEqual(data.get("files_left"), test.get("files_left"))
            self.assertEqual(len(project.get_all_scores_save()), idx)

            d = test.get("data")
            image_file_id = data.get("image").get("id")
            ViewSetCreateModel.create_or_update_imagescore(image_file_id, test.get("user"), d)
            data = ViewSetCreateModel.get_next_image(project.pk, test.get("user")).data
            self.assertEqual(data.get("files_left"), test.get("files_left") - 1)
            self.assertEqual(len(project.get_all_scores_save()), idx + 1)
            self.assertEqual(data.get("scores_ratio"), test.get("ratio"))
