import unittest
from loader import distance_mtr


class MyTestCase(unittest.TestCase):

    def test_distanceMtr(self):
        dm = distance_mtr.DiffMatrix("../resources/dataset.csv")
        dm.load()
        self.assertIsNotNone(dm.df)
        split = dm.split_sides([1, 2, 3], [0])
        self.assertTrue('rhs' in split and 'lhs' in split)
        self.assertIsNotNone(split['rhs'])
        self.assertIsNotNone(split['lhs'])
        self.assertGreater(len(split['rhs']),0)
        self.assertGreater(len(split['lhs']), 0)


if __name__ == '__main__':
    unittest.main()
