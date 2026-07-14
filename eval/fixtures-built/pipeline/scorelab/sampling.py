"""Sampling helpers."""
import json      # F401: unused import (lint warning 1)
import os        # F401: unused import (lint warning 2)
import random


def sample(rows, k, seed=7):
    rng = random.Random(seed)
    return rng.sample(rows, min(k, len(rows)))
