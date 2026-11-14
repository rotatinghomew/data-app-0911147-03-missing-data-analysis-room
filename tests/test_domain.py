import copy
import unittest
from app import domain
from app.service import load_study


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data = load_study()
        self.request = {'operation': 'complete_cases', 'fields': ['hours', 'score']}

    def test_missing_reason_required(self):
        data = copy.deepcopy(self.data)
        data['records'][0]['hours'] = None
        data['missing_reasons'] = [row for row in data['missing_reasons']
                                   if not (row['student'] == data['records'][0]['student'] and row['field'] == 'hours')]
        with self.assertRaises(ValueError):
            domain.baseline(data)

    def test_complete_case_subset(self):
        result = domain.act(self.data, self.request)
        expected = [row for row in self.data['records'] if row['hours'] is not None and row['score'] is not None]
        self.assertEqual(result['retained'], len(expected))
        self.assertEqual(result['excluded'] + result['retained'], len(self.data['records']))

    def test_inconsistent_derived_score(self):
        data = copy.deepcopy(self.data)
        data['records'][0].update(part_a=10, part_b=10, score=30)
        with self.assertRaises(ValueError):
            domain.baseline(data)


if __name__ == '__main__':
    unittest.main()
