import numpy as np

class AgentSkeleton:
    """
    Main elements of an agent in sugarscape0. All other agents to inherit from it
    """
    
    # each agent occupies a location somewhere on the grid
    location = [0, 0]
    # an indicator if the agent is dead or alive
    alive = True
    # age counter
    age = 0
    # lifespan for dying of old age
    lifespan = 100

    # each agent has a vision parameter determining how much of the environment it can see
    vision = 4
    # each agent has a vspped parameter determining its per-turn movement range
    speed = 1
    # metabolism vars determine burn rate of sugar and spice
    sugar_metabolism = 1
    spice_metabolism = 1
    # how much the agent can carry
    sugar_capacity = 1
    spice_capacity = 1

    # initial endowment of sugar and spice
    sugar = 0
    spice = 0

    def __init__(self):
        raise NotImplementedError

    def act(self, state):
        raise NotImplementedError

    def is_starved(self):
        raise NotImplementedError
    
    def is_old(self):
        raise NotImplementedError


class DummyAgent(AgentSkeleton):
    """
    A basic agent able to operate in an environment. Takes reandom actions
    """

    def __init__(
        self, location, lifespan, vision, speed, power,
        sugar_metabolism, spice_metabolism,
        sugar_capacity, spice_capacity, gender,
        price_move, sugar, spice
    ):
        self.location = location,
        self.lifespan = lifespan,
        self.vision = vision,
        self.speed = speed,
        self.power = power
        self.sugar_metabolism = sugar_metabolism,
        self.spice_metabolism = spice_metabolism,
        self.sugar_capacity = sugar_capacity,
        self.spice_capacity = spice_capacity,
        self.gender = gender
        self.price_move = price_move
        self.sugar = sugar
        self.spice = spice
        self.alive = True
        self.stance = 'defence'
        self.sugar_consumption_unit = 1
        self.spice_consumption_unit = 1
    
    def act(self, state):
        action = {}
        action['hmove'] = np.random.choice(np.arange(-self.speed, self.speed, 1))
        action['vmove'] = np.random.choice(np.arange(-self.speed, self.speed, 1))
        action['price_adjust'] = np.random.choice(
            np.arange(-self.price_move, self.price_move, 1)
        )
        action['stance'] = np.random.choice(
            ['forage', 'attack', 'defend', 'sell', 'buy', 'copulate']
        )

    def step(self):
        raise NotImplementedError

    def learn(self, state, action, reward, next_state, turn, done):
        pass

    def is_starved(self):
        if self.sugar <= 0 or self.spice <= 0:
            self.alive = False
            return True
        return False
    
    def is_old(self):
        if self.age >= self.lifespan:
            self.alive = False
            return True
        return False

    def consume(self, commodity, amount):
        raise NotImplementedError

    def update_price(self, commodity, change):
        raise NotImplementedError

    def lose(self, commodity, amount):
        raise NotImplementedError

    def harvest(self, commodity, amount):
        raise NotImplementedError

    def mate_female(self):
        raise NotImplementedError

    def mate_male(self):
        raise NotImplementedError

    def give_birth(self, mate):
        raise NotImplementedError








