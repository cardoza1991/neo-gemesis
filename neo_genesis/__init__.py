"""neo-genesis: digital bacteria in a bounded world."""
from .sim import Sim
from .organism import ANCESTOR, Organism
from .isa import Op
__all__ = ["Sim", "Organism", "ANCESTOR", "Op"]
__version__ = "0.1.0"
