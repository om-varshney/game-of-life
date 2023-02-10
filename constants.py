COLORS = {
    "CITIZEN": "dark green",
    "DISEASED": "magenta",
    "KILLER": "crimson",
    "GOD": "gold",
    "EMPTY": "black"
}

SPAWN_PROB = {
    "CITIZEN": 50,
    "DISEASED": 10,
    "KILLER": 11,
    "GOD": 29,
}

IMMUNITY = {
    "CITIZEN": 4000,
    "DISEASED": 5,
    "KILLER": 50,
    "GOD": 2500,
}

REPRO_SPAWN = {
    "CITIZEN": 90,
    "KILLER": 3,
    "GOD": 7,
}

MORTALITY_OP = {
    "CITIZEN": 0.6,
    "DISEASED": 0.9,
    "KILLER": 0.7,
    "GOD": 0.07,
}

MORTALITY_UP = {
    "CITIZEN": 0.6,
    "DISEASED": 0.9,
    "KILLER": 0.4,
    "GOD": 0.2,
}

KILLER_KILL_RATE = {
    "CITIZEN": 0.8,
    "DISEASED": 0.9
}

GOD_KILL_RATE = {
    "KILLER": 0.9,
}

GOD_TRANSFORM_RATE = {
    "KILLER": 0.7,
    "DISEASED": 0.9,
}

KILLER_TRANSFORM_RATE = {
    "CITIZEN": 0.9,
}

KILLER_GOD_IMM_PENALTY = 0.85
DISEASED_GOD_IMM_PENALTY = 0.95

NUM_TICKS = 1000
