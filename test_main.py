from main import RollerBot
import unittest
import pytest

class MockRandom:
    index = 0;
    def randrange(self, min, max):
        delta = max-min
        result = min + self.index
        self.index = (self.index + 1) % delta
        return result

class RollerBotTester(unittest.TestCase):

    def setUp(self):
        self.roller = RollerBot( MockRandom().randrange )

    def test_roll(self):
        rollResult = (count, results, success, added, stunt) = self.roller.roll('roll 10')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__']
        expectedResult = (10, expectedRoll, 5, 0, 0)
        self.assertEqual(expectedResult, rollResult);

    def test_roll_reroll(self):
        rollResult = (count, results, success, added, stunt) = self.roller.roll('roll 10 rr<=6')
        expectedRoll = [
            '~~1~~', '~~2~~', '~~3~~', '~~4~~', '~~5~~', '~~6~~', '__7__', '__8__', '__9__', '__**10**__',
            '~~1~~', '~~2~~', '~~3~~', '~~4~~', '~~5~~', '~~6~~', '__7__', '__8__', '__9__', '__**10**__',
            '~~1~~', '~~2~~', '~~3~~', '~~4~~', '~~5~~', '~~6~~', '__7__', '__8__'
            ]
        expectedResult = (10, expectedRoll, 12, 0, 0)
        self.assertEqual(expectedResult, rollResult);

    def test_roll_reroll_once(self):
        rollResult = (count, results, success, added, stunt) = self.roller.roll('roll 10 ro<=2')
        expectedRoll = ['~~1~~', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__', '~~1~~', '2']
        expectedResult = (10, expectedRoll, 5, 0, 0)
        self.assertEqual(expectedResult, rollResult);

    def test_roll_stunt1(self):
        rollResult = (count, results, success, added, stunt) = self.roller.roll('roll 8 stunt1')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__']
        expectedResult = (10, expectedRoll, 5, 0, 1)
        self.assertEqual(expectedResult, rollResult);

    def test_roll_stunt_1(self):
        rollResult = (count, results, success, added, stunt) = self.roller.roll('roll 8 stunt 1')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__']
        expectedResult = (10, expectedRoll, 5, 0, 1)
        self.assertEqual(expectedResult, rollResult);

    def test_parseAsText(self):
        # print(self.roller.parseAsText('@test_user', self.roller.roll('!roll 23 rr<=2 ro<7 do>6')))
        self.assertTrue(True);

if __name__ == '__main__':
    unittest.main()