"""The VBox structure is a three-layered one.

Bottommost layer is `cli` -- actual part that calls programs and parses their outputs (where possible);
Middle layer is `pyVb` -- it organises CLI bindings to pythonic object structures and performs final parsing and typecasting;
Topmost layer is `api` -- the one that actually gets exposed to the parent library. Should provide nice and consistent usage experience;
"""
from .api import *