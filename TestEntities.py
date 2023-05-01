import Entities as ent
import unittest

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
        self.assertEqual(type(ent.get_card(1)), ent.Card)
        self.assertEqual(ent.get_card("Maléfice").name, "Maléfice")
        self.assertEqual(ent.get_card("46-2").id, "46-2")
        with self.assertRaises(KeyError):
            ent.get_card(-1)

    def test_import_cardgroup(self):
        self.assertEqual(type(ent.import_deck("basic_chasseur.csv")), ent.CardGroup)




if __name__ == '__main__':
    unittest.main()
