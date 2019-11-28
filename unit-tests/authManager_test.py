import unittest
from adapters.authManager import AuthManager 

def fun(x):
    return x + 1

class AuthManagerTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)