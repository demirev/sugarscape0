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

    # initial endowment of sugar and spice - reserves
    sugar = 0
    spice = 0
    
    # consumed sugar and spice - will be used to sustain the agent
    sugar_consumed = 0
    spice_consumed = 0

    # slot for accumulating per-turn utility
    turn_utility = 0

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
        self.spice_price = 1
        self.sugar_price = 1
    
    def act(self, state):
        action = {}
        action['hmove'] = np.random.choice(np.arange(-self.speed, self.speed, 1))
        action['vmove'] = np.random.choice(np.arange(-self.speed, self.speed, 1))
        action['spice_price_change'] = np.random.choice(
            np.arange(-self.price_move, self.price_move, 1)
        )
        action['sugar_price_change'] = np.random.choice(
            np.arange(-self.price_move, self.price_move, 1)
        )
        action['stance'] = np.random.choice(
            ['forage', 'attack', 'defend', 'sell', 'buy', 'copulate']
        )

    def step(self):
        utility = self.turn_utility
        self.turn_utility = 0
        self.age += 1
        if self.is_starved() or self.is_old():
            utility = 0 # dead
        return utility

    def learn(self, state, action, reward, next_state, turn, done):
        pass

    def is_starved(self):
        if self.sugar_consumed <= 0 or self.spice_consumed <= 0:
            self.alive = False
            return True
        return False
    
    def is_old(self):
        if self.age >= self.lifespan:
            self.alive = False
            return True
        return False

    def consume(self, commodity, amount):
        if commodity == 'sugar':
            if self.sugar < amount:
                amount = self.sugar
            self.sugar -= amount
            self.sugar_consumed += amount
        elif commodity == 'spice':
            if self.spice < amount:
                amount = self.spice
            self.spice -= amount
            self.spice_consumed += amount
        else:
            raise ValueError("commodity must be one of 'sugar' or 'spice'")
 
    def metabolize(self):
        self.sugar_consumed -= self.sugar_metabolism
        self.spice_consumed -= self.spice_metabolism

    def update_price(self, commodity, change):
        if commodity == 'sugar':
            self.sugar_price += change
        elif commodity == 'spice':
            self.spice_price += change
        else:
            raise ValueError("commodity must be one of 'sugar' or 'spice'")

    def lose(self, commodity, amount):
        if commodity == 'sugar':
            if self.sugar < amount:
                amount = self.sugar # make sure this doesn't go negative
            self.sugar -= amount
        elif commodity == 'spice':
            if self.spice < amount:
                amount = self.spice
            self.spice -= amount
        else:
            raise ValueError("commodity must be one of 'sugar' or 'spice'")
        return amount # might be used elsewhere

    def harvest(self, commodity, amount):
        if commodity == 'sugar':
            self.sugar += amount
        elif commodity == 'spice':
            self.spice += amount
        else:
            raise ValueError("commodity must be one of 'sugar' or 'spice'")

    def mate_female(self):
        "Any in-agent mating effects - e.g. utility accumulation"
        pass 

    def mate_male(self):
        "Any in-agent mating effects - e.g. utility accumulation"
        pass 

    def give_birth(self, mate):
        baby = DummyAgent(
            location = [0,0], # doesn't matter, will be changed in scape method
            lifespan = np.random.choice(self.lifespan, mate.lifespan), 
            vision = np.random.choice(self.vision, mate.vision), 
            speed = np.random.choice(self.speed, mate.speed), 
            power = np.random.choice(self.power, mate.power), 
            sugar_metabolism = np.random.choice(self.sugar_metabolism, mate.sugar_metabolism), 
            spice_metabolism = np.random.choice(self.spice_metabolism, mate.spice_metabolism), 
            spice_capacity = np.random.choice(self.spice_capacity, mate.spice_capacity), 
            sugar_capacity = np.random.choice(self.sugar_capacity, mate.sugar_capacity), 
            gender = np.random.choice(self.gender, mate.gender), 
            price_move = np.random.choice(self.price_move, mate.price_move), 
            sugar = 0.3 * self.sugar, # mother gives resources to child 
            spice = 0.3 * self.spice
        )
        
        baby.sugar_consumed = baby.sugar 
        baby.spice_consumed = baby.spice

        self.sugar = 0.7 * self.sugar # birth is costly to the mother
        self.spice = 0.7 * self.spice

        return baby








