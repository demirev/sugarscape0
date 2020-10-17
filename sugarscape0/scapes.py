import numpy as np
import warnings

class ScapeSkeleotn:
    """
    Main elements of an environment in sugarscape0. All other environments to inherit from it
    """
    
    # each scape is a 2-d grid of some dimension
    dimensions = [50, 50]

    # each field in the grid can grow sugar and/or spice up to capacity
    sugar_capacity  = np.random.randint(0, 1, size=dimensions)
    spice_capacity  = np.random.randint(0, 1, size=dimensions)
    # growth by default is constant per move
    sugar_growth = 1
    spice_growth = 1
    # intialize scape with sugar and spice at capacity
    sugar = np.copy(sugar_capacity)
    spice = np.copy(spice_capacity)

    # each scape is inhabited by agents
    agents = []
    # the environment holds information about their locations
    agent_map = np.zeros(shape = dimensions)


    def __init__(self):
        raise NotImplementedError

    def reset(self):
        "Reset the state"
        raise NotImplementedError

    def step(self, action, agent):
        """
        Given the actions of a single agent advance the environment
        Must return next_state, reward, done
        """
        raise NotImplementedError

    
    def simulate(self, n_episodes):
        """
        Simulate many turns
        """
        raise NotImplementedError

    def get_state(self):
        """
        Return the state of the environment
        """
        raise NotImplementedError
    
    def reset(self):
        """
        Resets the environment
        """
        raise NotImplementedError

    def record(self):
        """
        Records history
        """
        raise NotImplementedError

    def grow(self):
        raise NotImplementedError
    
    def harvest(self):
        raise NotImplementedError
    

class BaseScape(ScapeSkeleotn):

    stances = [
        'offence', 'defence', 'harvest_sugar', 'harvest_spice', 
        'sell_sugar', 'sell_spice', 'buy_sugar', 'buy_spice' 
        'mate_male', 'mate_female', 'consume_sugar', 'consume_spice'
    ]

    def __init__(self, agents = [], dimensions = [50, 50]):
        # set dimensions
        if len(dimensions) == 1:
            dimensions = [dimensions, dimensions]
        elif len(dimensions) > 2:
            warnings.warn("dimensions longer than needed. Only first two elements will be used")
        elif len(dimensions) == 0:
            raise ValueError("dimensions cannot be 0-length")

        self.dimensions = dimensions

        # put agents on the sugerscape
        agent_map = np.array([1]*len(agents) + [0]*(dimensions[0]*dimensions[1] - len(agents)))
        agent_map = np.random.shuffle(agent_map.reshape(dimensions))

        agent_locs = []
        for x, y in zip(range(dimensions), range(dimensions)):
            if agent_map[x,y] == 1:
                agent_locs.append([x,y])
        
        for agent, loc in zip(agents, agent_locs):
            agent.location = loc

        self.agent_map = agent_map
        self.agents = agents

        # determine agent stance map
        self.stance_maps = {}
        for stance in self.stances:
            stance_map = np.zeros(self.dimensions)
            for agent in self.agents:
                if agent.stance == stance:
                    stance_map[agent.location] = 1
            self.stance_maps[stance] = stance_map  
        
        # determine price map
        self.price_maps = {}
        price_map_sugar = np.zeros(self.dimensions)
        price_map_spice = np.zeros(self.dimensions)
        for agent in self.agents:
            price_map_sugar[agent.location] = agent.sugar_price
            price_map_spice[agent.location] = agent.spice_price
        self.price_maps['sugar'] = price_map_sugar
        self.price_maps['spice'] = price_map_spice


    def step(self, action, agent):
        """
        Given the actions of a single agent advance the environment
        Must return next_state, reward, done
        """

        old_location = agent.location

        # resolve movement ----
        target_space = [old_location[0] + action.movement[0], old_location[1] + action.movement[1]]
        if self.agent_map[target_space] == 0: # if space is free...
            # vacate current location
            self.agent_map[old_location] = 0
            # put agent on the new location
            agent.location = target_space
            self.agent_map[target_space] = 1
        
        # change offer prices ----
        if action.price_spice is not None:
            agent.update_price('spice', action.price_spice)

        if action.price_sugar is not None:
            agent.update_price('sugar', action.price_spice)

        # change stance ----
        target_stance = action.stance
        # note that agent is no longer in old stance
        self.stance_maps[agent.stance][old_location] = 0 
        # and put it into new stance
        self.stance_maps[target_stance][agent.location] = 1
        agent.stance = target_stance

        # resolve stance ----
        self.resolve_interaction(target_stance, agent)

        # any per-turn agent-side effects (if any reward is received this should return it)
        reward = agent.step()

        # return state, reward, done flag tupple
        return [self.get_state(), reward, False]

    def simulate(self, n_turns):
        """
        Simulate many turns
        """
        for turn in range(n_turns):
            for agent in self.agents:
                if agent.alive:
                    state = self.get_state()
                    action = agent.act(state)
                    next_state, reward, done = self.step(action, agent)
                    agent.learn(state, action, reward, next_state, turn, done)

    def resolve_interaction(self, stance, agent):
        if stance == 'offence':
            self.resolve_offence(agent)
        elif stance == "defence":
            self.resolve_defence(agent)
        elif stance == "harvest_sugar":
            self.resolve_harvest_sugar(agent)
        elif stance == "harvest_spice":
            self.resolve_harvest_spice(agent)
        elif stance == "sell_sugar":
            self.resolve_sell_sugar(agent)
        elif stance == "sell_spice":
            self.resolve_sell_spice(agent)
        elif stance == "buy_sugar":
            self.resolve_buy_sugar(agent)
        elif stance == "buy_spice":
            self.resolve_buy_spice(agent)
        elif stance == "mate_male":
            self.resolve_mate_male(agent)
        elif stance == "mate_female":
            self.resolve_mate_female(agent)
        else:
            raise ValueError("unrecognized stance")

    def resolve_offence(self, agent):
        """
        in offence mode the agent attacks their neighbours and steals sugar 
        and spice equal to agent's power stat
        """ 
        neighbours = self.find_neigbours(agent)
        for neighbour in neighbours:
            if neighbour.stance != 'defence': # defence mode negates attacks
                agent.harvest('spice', neighbour.lose('spice', agent.power))
                agent.harvest('sugar', neighbour.lose('sugar', agent.power))

    def resolve_defence(self, agent):
        "nothing happens in defensive mode"
        pass

    def resolve_harvest_sugar(self, agent):
        "harvest sugar"
        harvest = self.sugar[agent.location]
        self.sugar[agent.location] = 0
        agent.harvest('sugar', harvest)

    def resolve_harvest_spice(self, agent):
        "harvest spice"
        harvest = self.spice[agent.location]
        self.spice[agent.location] = 0
        agent.harvest('spice', harvest)

    def resolve_sell_sugar(self, agent):
        "nothing immedeately happens when selling"
        pass
    
    def resolve_sell_spice(self, agent):
        "nothing immedeately happens when selling"
        pass

    def resolve_buy_sugar(self, agent):
        "buy sugar from any neighbour who is selling"
        neighbours = self.find_neigbours(agent)
        for neighbour in neighbours:
            if neighbour.stance == 'sell_sugar':
                price = neighbour.sugar_price
                if agent.spice >= price and neighbour.sugar >= neighbour.sugar_sell_unit:
                    agent.lose('spice', price) # pay in spice
                    agent.harvest('sugar', neighbour.sugar_sell_unit) # gain 1 unit in sugar
                    neighbour.lose('sugar', neighbour.sugar_sell_unit)
                    neighbour.harvest('spice', price)


    def resolve_buy_spice(self, agent):
        "buy sugar from any neighbour who is selling"
        neighbours = self.find_neigbours(agent)
        for neighbour in neighbours:
            if neighbour.stance == 'sell_spice':
                price = neighbour.spice_price
                if agent.sugar >= price and neighbour.spice >= neighbour.spice_sell_unit:
                    agent.lose('sugar', price) # pay in sugar
                    agent.harvest('spice', neighbour.spice_sell_unit) # gain 1 unit in spice
                    neighbour.lose('spice', neighbour.spice_sell_unit)
                    neighbour.harvest('sugar', price)

    def resolve_mate_female(self, agent):
        "mate with 1 random neighbour in mate_male mode"
        neighbours = self.find_neigbours(agent)
        potential_mates = [neighbour for neighbour in neighbours if neighbour.stance == 'mate_male']
        if len(potential_mates):
            mate = np.random.choice(potential_mates)
            mate.mate_male() # any in-agent effects such as utility gain or resource cost
            agent.mate_female()
            free_fields = self.find_free_fields(agent)
            if len(free_fields):
                field = np.random.choice(free_fields)
                child = self.copulate(agent, mate)
                child.location = field
                self.agents.append(child) 

    def resolve_mate_male(self, agent):
        "nothing happens in mate_male mode"
        pass

    def resolve_consume_sugar(self, agent):
        "agent eats sugar"
        agent.consume('sugar', agent.sugar_consumption_unit) # consume 1 unit of sugar

    def resolve_consume_spice(self, agent):
        "agent eats spice"
        agent.consume('spice', agent.spice_consumption_unit) # consume 1 unit of spice

    def find_neigbours(self, agent):
        "return all other agents next to agent"
        neighbours = []
        for other in self.agents: # there's got to be a better way here
            diff0 = other.location[0] - agent.location[0] 
            diff1 = other.location[1] - agent.location[1]
            if diff0 <= 1 and diff1 <= 1:
                if not diff0 == 0 and diff1 == 0: # don't return the agent themselve
                    neighbours.append(other)
        return neighbours

    def find_free_fields(self, agent):
        free_fields = []
        for vrt in [-1, 0, 1]:
            for hrz in [-1, 0, 1]:
                is_occupied = self.agent_map[agent.location[0] + hrz, agent.location[1] + vrt]
                if not is_occupied:
                    free_fields.append(agent.location[0] + hrz, agent.location[1] + vrt)
        return free_fields

    def copulate(self, female, male):
        child = female.give_birth(male)
        return child

    def get_state(self):
        state = np.stack([self.agent_map, self.sugar, self.spice] + self.stance_maps + self.price_maps)
        return state
