import unittest, random
from .organism import ANCESTOR, mutate
from .sim import Sim

class TestDish(unittest.TestCase):
    def test_inoculation(self):
        self.assertEqual(Sim(width=16, height=12, seed=1, seeds=4).census().population, 4)
    def test_mutation_can_change_genome(self):
        rng = random.Random(0)
        g = list(ANCESTOR)
        self.assertTrue(any(mutate(g, rng, rate=0.2) != g for _ in range(200)))
    def test_run_does_not_crash(self):
        last = Sim(width=20, height=14, seed=5, seeds=6, max_pop=80).run(200)
        self.assertGreaterEqual(last.tick, 1)

if __name__ == "__main__":
    unittest.main()
