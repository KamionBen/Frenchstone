import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Entities as ent


class TestCard(unittest.TestCase):
    def test_is_card_id(self):
        self.assertTrue(ent.is_card_id('023-2'))
        self.assertFalse(ent.is_card_id('coucou maman !'))
        self.assertFalse(ent.is_card_id('Maléfice'))
        self.assertFalse(ent.is_card_id(3))

    def test_int_to_id(self):
        self.assertEqual(ent.int_to_id(128, 2), '0128-2')
        with self.assertRaises(TypeError):
            ent.int_to_id('bleu', 1)

    def test_get_card(self):
        cardspath = "cards.json"  # J'ai un problème là ...
        self.assertEqual(type(ent.get_card(1), data=cardspath), ent.Card)
        self.assertEqual(ent.get_card("Maléfice", data=cardspath).name, "Maléfice")
        self.assertEqual(ent.get_card("46-2", data=cardspath).id, "46-2")
        with self.assertRaises(KeyError):
            ent.get_card(-1, data=cardspath)


if __name__ == '__main__':
    unittest.main()

