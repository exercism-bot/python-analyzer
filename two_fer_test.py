import ast
import unittest
import analyzer

class TwoFerTest(unittest.TestCase):
    def test_camel_case(self):
        camel_case = "someVar = 0"
        feedback = analyzer.analyze(camel_case)
        self.assertTrue(analyzer.var_convention in feedback[0])

    def test_camel_case_2(self):
        not_camel = "some_var = 0"
        feedback = analyzer.analyze(not_camel)
        self.assertFalse(analyzer.var_convention in feedback[0])

    def test_malformed_input(self):
        malformed_input = ")^*()&*$@Jfjlkajsdf;"
        feedback = analyzer.analyze(malformed_input)
        self.assertTrue(analyzer.malformed_code in feedback[0])

    def test_missing_method(self):
        wrong_method_name = '''def one_fer(name="you"): return "One for %s, one for me." % name'''
        feedback = analyzer.analyze(wrong_method_name)
        self.assertTrue(analyzer.no_method in feedback[0])

    def test_has_method(self):
        correct_method_name = '''def two_fer(name="you"): return "One for %s, one for me." % name'''
        feedback = analyzer.analyze(correct_method_name)
        self.assertFalse(analyzer.no_method in feedback[0])

if __name__ == '__main__':
    unittest.main()