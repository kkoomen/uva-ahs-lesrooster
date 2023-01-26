from unittest import TestCase, mock

from code.utils.data import load_courses, load_rooms, load_students

class TestUtilsData(TestCase):
    @mock.patch('code.utils.helpers.data_path')
    @mock.patch('csv.reader')
    def test_load_students(self, mock_csv_reader, data_path):
        mock_csv_reader.return_value = iter([
            ['Achternaam', 'Voornaam', 'Stud.Nr.', 'Vak1', 'Vak2', 'Vak3', 'Vak4', 'Vak5'],
            ['Abbing', 'Yanick', '52311353', 'Analysemethoden en -technieken', 'Data Mining', 'Lineaire Algebra', 'Software engineering'],
        ])
        data_path.return_value = 'students.csv'

        with mock.patch('code.utils.data.open'):
            students = load_students()

        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].first_name, 'Yanick')
        self.assertEqual(students[0].last_name, 'Abbing')
        self.assertEqual(students[0].student_id, '52311353')
        self.assertEqual(students[0].enrolled_courses, [
            'Analysemethoden en -technieken',
            'Data Mining',
            'Lineaire Algebra',
            'Software engineering'
        ])

    @mock.patch('code.utils.helpers.data_path')
    @mock.patch('csv.DictReader')
    def test_load_courses(self, mock_csv_reader, data_path):
        mock_csv_reader.return_value = iter([
            {
                'Vak': 'Advanced Heuristics',
                '#Hoorcolleges': '1',
                '#Werkcolleges': '0',
                'Max. stud. Werkcollege': '',
                '#Practica': '1',
                'Max. stud. Practicum': '10',
                '#Inschrijvingen': '22',
            },
        ])
        data_path.return_value = 'courses.csv'

        with mock.patch('code.utils.data.open'):
            courses = load_courses()

        self.assertEqual(len(courses), 1)
        self.assertEqual(isinstance(courses[0].id, int), True)
        self.assertEqual(courses[0].name, 'Advanced Heuristics')
        self.assertEqual(courses[0].lectures_amount, 1)
        self.assertEqual(courses[0].seminars_amount, 0)
        self.assertEqual(courses[0].seminar_capacity, 0)
        self.assertEqual(courses[0].practicals_amount, 1)
        self.assertEqual(courses[0].practical_capacity, 10)
        self.assertEqual(courses[0].enrolment, 22)
        self.assertEqual(courses[0].enrolled_students, [])
        self.assertEqual(courses[0].conflicting_courses, [])

    @mock.patch('code.utils.helpers.data_path')
    @mock.patch('csv.DictReader')
    def test_load_rooms(self, mock_csv_reader, data_path):
        mock_csv_reader.return_value = iter([
            {
                'Zaalnummer': 'A1.04',
                'Max. capaciteit': '41',
            },
            {
                'Zaalnummer': 'C0.110',
                'Max. capaciteit': '117',
            },
        ])
        data_path.return_value = 'rooms.csv'

        with mock.patch('code.utils.data.open'):
            rooms = load_rooms()

        self.assertEqual(len(rooms), 2)

        self.assertEqual(rooms[0].location_id, 'A1.04')
        self.assertEqual(rooms[0].capacity, 41)
        self.assertEqual(rooms[0].is_largest, False)

        self.assertEqual(rooms[1].location_id, 'C0.110')
        self.assertEqual(rooms[1].capacity, 117)
        self.assertEqual(rooms[1].is_largest, True)
