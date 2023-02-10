"""
This is the enhanced version of the previous simulation.
It features 4 kinds of particles--
    1. Citizen -- Green
    2. Diseased -- Brown
    3. Killer -- Red
    4. God -- Golden
There are a few processes that are going on--
    1. Declining immunity as you age--
        a. Applicable to citizens at standard rate
        b. Applicable to diseased at higher rate
        c. Applicable to Killer at a lower rate
        d. Not applicable to a God
    2. The Spreading of a disease--
        a. Initially a certain number of particles are spawned with the disease.
        b. Disease is propagated by reproduction
        c. In any reproduction, if there is a diseased particle present then-
            i. the offspring is a diseased particle.
The behaviours of particles are defined as follows--
    1. Citizens
        a. Citizens are normal particles, they will follow the rules of the game, and not do much.
        b. Most of the particles will be citizens.
        c. Citizens will reproduce to form new citizens.
    2. (precedence) Killers
        a. Killers will kill any particles that they neighbour directly but not diagonally.
        b. Killers will reproduce only with killers
        c. If a killer is present in diagonal relation to a citizen, he will make that citizen a killer.
    3. Diseased
        a. They will try to spread themselves by reproduction.
    4. God
        a. They will cure the disease of any diseased particle and make it a citizen.
        b. They will kill any killer who is present directly in contact to them.
        c. They will transform any killer into a citizen, who is present diagonally in contact to them.
We will build a custom datastructure for storing information for one complete generation.
We will build a simulator to display a list of generation datastructures frame by frame.
Let the fun begin!
"""
import copy
import time
import turtle
import constants
import random
import pickle
import os
import json
import seaborn as sns
import matplotlib.pyplot as plt


class Empty:
    def __init__(self, position, world):
        self.color = constants.COLORS["EMPTY"]
        self.position = position
        self.world = world

    def __str__(self):
        return "EMPTY"

    __repr__ = __str__

    def all_valid_neighbours(self, board):
        i, j = self.position
        an = (
            (i - 1, j - 1), (i, j - 1), (i + 1, j - 1),
            (i - 1, j), (i + 1, j),
            (i - 1, j + 1), (i, j + 1), (i + 1, j + 1)
        )
        return (board[i, j] for i, j in an if 0 < i < self.world.size and 0 < j < self.world.size)

    def enumerate_neighbors(self, board):
        ALL_CLASSES = {
            "CITIZEN": 0,
            "KILLER": 0,
            "GOD": 0,
            "DISEASED": 0,
            "EMPTY": 0,
        }
        for i in self.all_valid_neighbours(board):
            ALL_CLASSES[i.__str__()] += 1
        del ALL_CLASSES["EMPTY"]
        return ALL_CLASSES

    def choose_random_spawn(self):
        # This function is called when none of the special reproduction capabilities are being satisfied.
        return random.choices([
            Citizen(position=self.position, world=self.world),
            Killer(position=self.position, world=self.world),
            God(position=self.position, world=self.world),
        ], weights=constants.REPRO_SPAWN.values(), k=1)[0]

    def enforce_basic_rules(self, board):
        return self

    def apply_immunity(self):
        return self

    def interact(self, board):
        ALL_CLASSES = self.enumerate_neighbors(board)
        # check if there are exactly three neighbours
        if sum(ALL_CLASSES.values()) == 3:
            if ALL_CLASSES["DISEASED"]:
                return Diseased(position=self.position, world=self.world)
            elif ALL_CLASSES["KILLER"]:
                return Killer(position=self.position, world=self.world)
            elif ALL_CLASSES["GOD"] == 2:
                return God(position=self.position, world=self.world)
            else:
                return self.choose_random_spawn()
        return self


class Citizen:
    def __init__(self, position, world, immunity=constants.IMMUNITY["CITIZEN"]):
        self.immunity = immunity
        self.position = position
        self.world = world
        self.color = constants.COLORS["CITIZEN"]
        self.generation = 1

    def __str__(self):
        return "CITIZEN"

    __repr__ = __str__

    def apply_immunity(self):
        dying_probability = self.generation / self.immunity
        will_live = random.choices([0, 1], weights=(dying_probability, 1 - dying_probability), k=1)[0]
        if will_live:
            self.generation += 1
            return self
        else:
            return Empty(position=self.position, world=self.world)

    @staticmethod
    def evaluate_weight(obj):
        if isinstance(obj, Empty):
            return 0
        return 1

    def num_neighbours(self, board):
        i, j = self.position
        an = (
            (i - 1, j - 1), (i, j - 1), (i + 1, j - 1),
            (i - 1, j), (i + 1, j),
            (i - 1, j + 1), (i, j + 1), (i + 1, j + 1)
        )
        valid = (self.evaluate_weight(board[i, j]) for i, j in an if 0 < i < self.world.size and 0 < j < self.world.size)
        return sum(valid)

    def find_neighbours(self):
        i, j = self.position
        return {
            "DIRECT": (
                (i, j - 1), (i - 1, j), (i + 1, j), (i, j + 1),
            ),
            "DIAGONAL": (
                (i - 1, j - 1), (i + 1, j - 1),
                (i - 1, j + 1), (i + 1, j + 1),
            )
        }

    def enforce_basic_rules(self, board):
        # Enforce the basic rules that you can die of under or over population
        ns = self.num_neighbours(board)
        if ns not in (2, 3):
            if ns < 2:
                return random.choices((Empty(position=self.position, world=self.world), self),
                                      weights=(constants.MORTALITY_UP[self.__str__()],
                                               1 - constants.MORTALITY_UP[self.__str__()]))[0]
            else:
                return random.choices((Empty(position=self.position, world=self.world), self),
                                      weights=(constants.MORTALITY_OP[self.__str__()],
                                               1 - constants.MORTALITY_OP[self.__str__()]))[0]
        return self

    def interact(self, board):
        all_neighbours = self.find_neighbours()
        direct_neighbours = [board[i, j] for i, j in all_neighbours["DIRECT"] if
                             0 < i < self.world.size and 0 < j < self.world.size]
        diagonal_neighbours = [board[i, j] for i, j in all_neighbours["DIRECT"] if
                               0 < i < self.world.size and 0 < j < self.world.size]
        # check if killer is directly in contact
        for check in direct_neighbours:
            if isinstance(check, Killer):
                return random.choices([
                    Empty(position=self.position, world=self.world),
                    self
                ], weights=(
                    constants.KILLER_KILL_RATE["CITIZEN"],
                    1 - constants.KILLER_KILL_RATE["CITIZEN"],
                ))[0]
        # check if killer is diagonally in contact
        for check in diagonal_neighbours:
            if isinstance(check, Killer):
                return random.choices([
                    Killer(position=self.position, world=self.world),
                    self
                ], weights=(
                    constants.KILLER_TRANSFORM_RATE["CITIZEN"],
                    1 - constants.KILLER_TRANSFORM_RATE["CITIZEN"],
                ))[0]
        return self


class Killer(Citizen):
    def __init__(self, position, world, immunity=constants.IMMUNITY["KILLER"]):
        super().__init__(immunity, world)
        self.immunity = immunity
        self.position = position
        self.world = world
        self.color = constants.COLORS["KILLER"]
        self.generation = 1

    def __str__(self):
        return "KILLER"

    __repr__ = __str__

    def interact(self, board):
        all_neighbours = self.find_neighbours()
        direct_neighbours = [board[i, j] for i, j in all_neighbours["DIRECT"] if
                             0 < i < self.world.size and 0 < j < self.world.size]
        diagonal_neighbours = [board[i, j] for i, j in all_neighbours["DIRECT"] if
                               0 < i < self.world.size and 0 < j < self.world.size]
        # Check if in direct contact with a god
        for check in direct_neighbours:
            if isinstance(check, God):
                return random.choices([
                    Empty(position=self.position, world=self.world),
                    self
                ], weights=(
                    constants.GOD_KILL_RATE["KILLER"],
                    1 - constants.GOD_KILL_RATE["KILLER"],
                ))[0]
        # Check if in diagonal contact with a god
        for check in diagonal_neighbours:
            if isinstance(check, God):
                return random.choices([
                    Citizen(position=self.position, world=self.world),
                    self
                ], weights=(
                    constants.GOD_TRANSFORM_RATE["KILLER"],
                    1 - constants.GOD_TRANSFORM_RATE["KILLER"],
                ))[0]
        return self


class Diseased(Citizen):
    def __init__(self, position, world, immunity=constants.IMMUNITY["DISEASED"]):
        super().__init__(immunity, world)
        self.immunity = immunity
        self.position = position
        self.world = world
        self.color = constants.COLORS["DISEASED"]
        self.generation = 1

    def __str__(self):
        return "DISEASED"

    __repr__ = __str__

    def interact(self, board):
        all_neighbours = self.find_neighbours()
        direct_neighbours = [board[i, j] for i, j in all_neighbours["DIRECT"] if
                             0 < i < self.world.size and 0 < j < self.world.size]
        # Check if in direct contact with a god
        for check in direct_neighbours:
            if isinstance(check, God):
                return random.choices([
                    Citizen(position=self.position, world=self.world),
                    self
                ], weights=(
                    constants.GOD_TRANSFORM_RATE["DISEASED"],
                    1 - constants.GOD_TRANSFORM_RATE["DISEASED"],
                ))[0]
        # check if killer is directly in contact
        for check in direct_neighbours:
            if isinstance(check, Killer):
                return random.choices([
                    Empty(position=self.position, world=self.world),
                    self
                ], weights=(
                    constants.KILLER_KILL_RATE["DISEASED"],
                    1 - constants.KILLER_KILL_RATE["DISEASED"],
                ))[0]
        return self


class God(Citizen):
    def __init__(self, position, world, immunity=constants.IMMUNITY["GOD"]):
        super().__init__(immunity, world)
        self.immunity = immunity
        self.position = position
        self.world = world
        self.color = constants.COLORS["GOD"]
        self.generation = 1

    def __str__(self):
        return "GOD"

    __repr__ = __str__

    def interact(self, board):
        all_neighbours = self.find_neighbours()
        direct_neighbours = [board[i, j] for i, j in all_neighbours["DIRECT"] if
                             0 < i < self.world.size and 0 < j < self.world.size]
        # Check if in direct contact with killer
        for check in direct_neighbours:
            if isinstance(check, Killer):
                self.immunity *= constants.KILLER_GOD_IMM_PENALTY
        for check in direct_neighbours:
            if isinstance(check, Diseased):
                self.immunity *= constants.DISEASED_GOD_IMM_PENALTY
        return self


class Board:
    def __init__(self, size, num_spawn, save_path, num_ticks=constants.NUM_TICKS, spawn_probs=constants.SPAWN_PROB):
        print("STARTING COMPUTATION ENGINE...")
        self.size = size
        self.num_spawn = num_spawn
        self.spawn_probs = spawn_probs
        self.curr_gen = 1
        self.num_ticks = num_ticks
        self.path = save_path

    def first_gen(self):
        board = {(i, j): Empty(position=(i, j), world=self) for i in range(self.size) for j in range(self.size)}
        all_spawns = random.choices([(i, j) for i in range(self.size) for j in range(self.size)], k=self.num_spawn)
        for choice in all_spawns:
            board[choice] = random.choices([
                Citizen(position=choice, world=self),
                Diseased(position=choice, world=self),
                Killer(position=choice, world=self),
                God(position=choice, world=self),
            ], weights=constants.SPAWN_PROB.values(), k=1)[0]
        return board

    def compute_board_states(self):
        if not os.path.isfile(f"{self.path}.gol"):
            print("Computing Board States...")
            generations = []
            board = self.first_gen()
            while self.curr_gen <= self.num_ticks:
                board_copy = copy.deepcopy(board)
                for position, particle in board_copy.items():
                    board_copy[position] = board_copy[position].apply_immunity().enforce_basic_rules(board_copy).interact(board_copy)
                self.curr_gen += 1
                board = board_copy
                generations.append(board)
            self.save_board(generations)
            print("Board States Computed!")
        else:
            print("File already exists...\n Board state computation aborted.")

    def save_board(self, generations):
        with open(f"{self.path}.gol", "wb") as f:
            data = {
                "Meta": {
                    "Animation": self.path,
                    "Grid Size": self.size,
                    "Spawned Elements": self.num_spawn,
                    "No. of generations computed": self.num_ticks,
                    "Spawning Probabilities": constants.SPAWN_PROB,
                    "Immunity": constants.IMMUNITY,
                    "Reproduction Spawn Probability": constants.REPRO_SPAWN,
                    "Over Population Mortality": constants.MORTALITY_OP,
                    "Under Population Mortality": constants.MORTALITY_UP,
                    "Killer Kill Rate": constants.KILLER_KILL_RATE,
                    "God Kill Rate": constants.GOD_KILL_RATE,
                    "God Transform Rate": constants.GOD_TRANSFORM_RATE,
                    "Killer Transform Rate": constants.KILLER_TRANSFORM_RATE,
                    "Penalty on god when touching killer": constants.KILLER_GOD_IMM_PENALTY,
                    "Penalty on god when touching Diseased": constants.DISEASED_GOD_IMM_PENALTY,

                },
                "Animation": generations
            }
            pickle.dump(data, f)


class Animator:
    def __init__(self, width, height, title, world, sleep=0, start=0, cut=None):
        print("STARTING ANIMATION ENGINE...")
        self.width = width
        self.height = height
        self.title = title
        self.world = world
        self.sleep = sleep
        self.cut = cut
        self.start = start

    def load_world(self):
        with open(f"{self.world.path}.gol", "rb") as f:
            return pickle.load(f)

    def animate(self):
        print("Loading Animation Data...")
        data = self.load_world()
        print("Data Loaded from file!")
        if isinstance(data, dict):
            print(json.dumps(data["Meta"], indent=2))
            data = data["Animation"]
        wn = turtle.Screen()
        wn.title(self.title)
        wn.bgcolor("black")
        wn.setup(700, 700)
        wn.tracer(0)
        stamper = turtle.Turtle()
        stamper.shape("square")
        stamper.shapesize(self.width / (self.world.size * 20) - 4 / self.world.size, self.width / (self.world.size * 20) - 4 / self.world.size, 0)
        stamper.penup()
        writer = turtle.Turtle()
        writer.hideturtle()
        writer.goto(0, 0)
        writer.pencolor("crimson")
        writer.write("THE GAME OF LIFE", align="center", font=("chiller", 50, "normal"))
        time.sleep(4)
        writer.goto(0, -30)
        writer.write("A Kiss of Death💋", align="center", font=("chiller", 30, "normal"))
        time.sleep(3)
        writer.clear()
        x, y = -self.width / 2, self.height / 2
        data = data[self.start:]
        if self.cut:
            data = data[:self.cut]
        for tick in data:
            for location, entity in tick.items():
                if not isinstance(entity, Empty):
                    i, j = location
                    stamper.goto(x + (i + 1) * self.width / self.world.size - self.height / (self.world.size * 2),
                                 y - (j + 1) * self.width / self.world.size - self.height / (self.world.size * 2))
                    stamper.color(entity.color)
                    stamper.stamp()
            wn.update()
            time.sleep(self.sleep)
            stamper.clear()
        time.sleep(2)
        writer.goto(0, -120)
        writer.write("💀", align="center", font=("chiller", 180, "normal"))
        time.sleep(5)
        writer.clear()
        wn.bye()


class StatisticGenerator:
    def __init__(self, animation_path, start=0, cut=None, save_path=None):
        print("STARTING STATISTICS ENGINE...")
        self.animation_path = animation_path
        self.cut = cut
        self.start = start
        self.save_path = save_path

    def load_world(self):
        with open(f"{self.animation_path}.gol", "rb") as f:
            return pickle.load(f)

    def compute_statistics(self):
        print("Loading Data...")
        data = self.load_world()
        print("Data Load Completed")
        # Right now I am just counting the number of people in each species.
        if isinstance(data, dict):
            data = data["Animation"]
        data = data[self.start:]
        if self.cut:
            data = data[:self.cut + 1]
        NUM_GEN = len(data)
        FRAME_STATS = {
            "CITIZEN": {
                "GENERATIONS": [i for i in range(NUM_GEN)],
                "POPULATION": []
            },
            "KILLER": {
                "GENERATIONS": [i for i in range(NUM_GEN)],
                "POPULATION": []
            },
            "GOD": {
                "GENERATIONS": [i for i in range(NUM_GEN)],
                "POPULATION": []
            },
            "DISEASED": {
                "GENERATIONS": [i for i in range(NUM_GEN)],
                "POPULATION": []
            },
            "EMPTY": {
                "GENERATIONS": [i for i in range(NUM_GEN)],
                "POPULATION": []
            },
        }
        for tick in data:
            ALL_CLASSES = {
                "CITIZEN": 0,
                "KILLER": 0,
                "GOD": 0,
                "DISEASED": 0,
                "EMPTY": 0,
            }
            for i in tick.values():
                ALL_CLASSES[i.__str__()] += 1
            for j in ALL_CLASSES.keys():
                FRAME_STATS[j]["POPULATION"].append(ALL_CLASSES[j])
        return FRAME_STATS

    def plot_statistics(self):
        sns.set_theme(style="darkgrid")
        sns.set(rc={
            'axes.facecolor': 'black',
            'figure.facecolor': 'black',
            'text.color': 'white',
            'font.family': 'chiller',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'axes.labelcolor': 'white',
        })
        data = self.compute_statistics()
        print("statistics computed")
        sns.lineplot(data=data["KILLER"], x="GENERATIONS", y="POPULATION", color=constants.COLORS["KILLER"])
        sns.lineplot(data=data["GOD"], x="GENERATIONS", y="POPULATION", color=constants.COLORS["GOD"])
        sns.lineplot(data=data["CITIZEN"], x="GENERATIONS", y="POPULATION", color="green")
        sns.lineplot(data=data["DISEASED"], x="GENERATIONS", y="POPULATION", color=constants.COLORS["DISEASED"])
        plt.legend(labels=['KILLER', 'GOD', 'CITIZEN', 'DISEASED'])
        plt.title(self.animation_path)
        if self.save_path:
            plt.savefig(self.save_path)
        plt.show()
