import unittest
from os.path import dirname
from os.path import join
from os import listdir

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        testdir = join(dirname(__file__), "data/articles")

        data = ""
        for fn in [join(testdir, fn) for fn in listdir(testdir)]:
            print(fn)
            fh = open(fn)
            data += fh.read()
        print(data)

    def test_test(self):
        """
        Just to make sure that we can run the test cases
        """
        self.assertEqual(1,1)


    def test_parse(self):

        pass

if __name__ == '__main__':
    unittest.main()
