#/usr/bin/env -S pipenv run python
from main import RollerBot
import unittest


class MockRandom:

    index = 0

    def randrange(self, min, max):
        delta = max - min
        result = min + self.index
        self.index = (self.index + 1) % delta
        return result


class RollerBotTester(unittest.TestCase):

    def setUp(self):
        self.roller = RollerBot(MockRandom().randrange)

    def test_roll(self):
        (count, results, success, added, stunt) = self.roller.roll('roll 10')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__']
        self.assertEqual(expectedRoll, results)
        self.assertEqual(10, count)
        self.assertEqual(5, success)
        self.assertEqual(0, added)
        self.assertEqual(0, stunt)

    def test_roll_damage(self):
        (count, results, success, added, stunt) = self.roller.roll('roll 10 damage')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__10__']
        self.assertEqual(expectedRoll, results)
        self.assertEqual(10, count)
        self.assertEqual(4, success)
        self.assertEqual(0, added)
        self.assertEqual(0, stunt)

    def test_roll_reroll(self):
        (count, results, success, added, stunt) = self.roller.roll('roll 10 rr<=6')
        expectedRoll = [
            '~~1~~', '~~2~~', '~~3~~', '~~4~~', '~~5~~', '~~6~~', '__7__', '__8__', '__9__', '__**10**__',
            '~~1~~', '~~2~~', '~~3~~', '~~4~~', '~~5~~', '~~6~~', '__7__', '__8__', '__9__', '__**10**__',
            '~~1~~', '~~2~~', '~~3~~', '~~4~~', '~~5~~', '~~6~~', '__7__', '__8__'
        ]
        self.assertEqual(expectedRoll, results)
        self.assertEqual(10, count)
        self.assertEqual(12, success)
        self.assertEqual(0, added)
        self.assertEqual(0, stunt)

    def test_roll_reroll_once(self):
        (count, results, success, added, stunt) = self.roller.roll('roll 10 ro<=2')
        expectedRoll = ['~~1~~', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__', '~~1~~', '2']
        self.assertEqual(expectedRoll, results)
        self.assertEqual(10, count)
        self.assertEqual(5, success)
        self.assertEqual(0, added)
        self.assertEqual(0, stunt)

    def test_roll_stunt1(self):
        (count, results, success, added, stunt) = self.roller.roll('roll 8 stunt1')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__']
        self.assertEqual(expectedRoll, results)
        self.assertEqual(10, count)
        self.assertEqual(5, success)
        self.assertEqual(0, added)
        self.assertEqual(1, stunt)

    def test_roll_stunt_1(self):
        (count, results, success, added, stunt) = self.roller.roll('roll 8 stunt 1')
        expectedRoll = ['1', '2', '3', '4', '5', '6', '__7__', '__8__', '__9__', '__**10**__']
        self.assertEqual(expectedRoll, results)
        self.assertEqual(10, count)
        self.assertEqual(5, success)
        self.assertEqual(0, added)
        self.assertEqual(1, stunt)

    def test_parseAsText(self):
        # sample result from '!roll 23 rr<=2 ro<7 do>6'
        roll = (23, [
            '~~1~~', '~~2~~', '3', '~~4~~', '5', '~~6~~', '__**7**__', '__**8**__', '__**9**__', '__**10**__',
            '~~1~~', '~~2~~', '3', '~~4~~', '5', '~~6~~', '__**7**__', '__**8**__', '__**9**__', '__**10**__',
            '~~1~~', '~~2~~', '3', '~~4~~', '5', '~~6~~', '__**7**__', '__**8**__', '__**9**__', '__**10**__',
            '~~1~~', '~~2~~', '3', '~~4~~', '5', '~~6~~', '__**7**__', '__**8**__', '__**9**__'
        ], 30, 3, 2)

        result = self.roller.parseAsText('@test_user', roll)
        self.assertEqual({
            'content': "@test_user rolled 23 dice for 30 successes. 26s rolled +3s bonus +1s from stunt\n"
                + "roll:\n"
                + "[ "
                    + "~~1~~, ~~2~~, 3, ~~4~~, 5, ~~6~~, __**7**__, __**8**__, __**9**__, __**10**__, "
                    + "~~1~~, ~~2~~, 3, ~~4~~, 5, ~~6~~, __**7**__, __**8**__, __**9**__, __**10**__, "
                    + "~~1~~, ~~2~~, 3, ~~4~~, 5, ~~6~~, __**7**__, __**8**__, __**9**__, __**10**__, "
                    + "~~1~~, ~~2~~, 3, ~~4~~, 5, ~~6~~, __**7**__, __**8**__, __**9**__"
                + " ]"
        }, result)


if __name__ == '__main__':
    unittest.main()
