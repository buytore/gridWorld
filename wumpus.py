#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from reinforcement_learning import TDQLearner, SARSALearner, make_exponential_temperature, PerformanceCounter, RLProblem
from environments import RLEnvironment
from Tkinter import *
import threading
import os


class PerpetualTimer(threading._Timer):

    def __init__(self, interval, function, name=None, daemon=False, args=(), kwargs={}):
        super(PerpetualTimer, self).__init__(interval, function, args, kwargs)
        self.setName(name)
        self.setDaemon(daemon)

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.isSet():
                return
            self.function(*self.args, **self.kwargs)

    def stop(self, timeout=None):
        self.cancel()
        self.join(timeout)

    def callback(egg):
        egg.cook()


class WumpusViewer(object):

    def __init__(self, environment):
        widthX = 600 # originally 400
        heightY = 600 # originally 400
        self.environment = environment
        root = Tk()
        w = Canvas(root, width=widthX, height=heightY)
        self.w = w
        w.pack()

        w.create_polygon(0, 0, 0, widthX-10, widthX-10, heightY-10, heightY-10, 0, fill='white', outline="blue")
        for x in range(6):                                 ## Originally range(4)
            w.create_line(100 * x, 0, 100 * x, heightY, width=5.0)
            w.create_line(0, 100 * x, widthX, 100 * x, width=5.0)

        #make holes
        for x, y in environment.holes:
            w.create_oval(*self._coord(x, y), fill='red')

        #make wumpus
        x, y = environment.wumpus
        w.create_oval(*self._coord(x, y), fill='blue')

        #make agent
        #x, y, have_gold = self.environment.state
        x, y, have_gold = self.environment.initial_state
        self.agent = w.create_oval(*self._coord(x, y), fill='green')

        #make gold
        x, y = environment.gold
        self.gold = w.create_oval(*self._coord(x, y), fill='yellow')

        frame = Frame(root)
        frame.pack()

        self.start = Button(frame, text="Start", command=self.start)
        self.start.pack(side=LEFT)
        self.stop = Button(frame, text="Stop", command=self.stop)
        self.stop.pack(side=LEFT)

        root.mainloop()

    def _coord(self, x, y):
        """Sets up main grid world coordinates based on gridEdge (this is a 4 x 4 grid world)"""
        gridEdge = 7           # originally 5
        y = gridEdge - y
        cx = 100 * (x - 1) + 50
        cy = 100 * (y - 1) + 50
        r = 20
        return (cx - r, cy - r, cx + r, cy + r)

    def step(self):
        if self.environment.is_completed(self.environment.state):
            self.timer.cancel()
        else:
            self.environment.step(viewer=self)

    def start(self):
        self.timer = PerpetualTimer(0.5, self.step)
        self.timer.start()
        self.environment.state = self.environment.initial_state

    def stop(self):
        self.timer.cancel()

    def event(self, state1, action, state2, agent):
        # ADD EVENT FROM TrafficMonitorAgent to REROUTE
        print 'action: %s state: %s' % (action, str(state2))
        x, y, have_gold = state2
        if have_gold and self.gold:
            self.w.delete(self.gold)
            self.w.itemconfig(self.agent, outline="yellow", width=6.0)
        self.w.coords(self.agent, self._coord(x, y))


class WumpusEnvironment(RLEnvironment):

    def __init__(self, agent):
        """
        if type(agent[0]) is SARSALearner:
            super(RLEnvironment, self).__init__(agent, (1, 1, False))  ## Set location of Agent
            print "Its a Sarsa Learner"
            self.action_dict = {'up': (0, 1), 'down': (0, -1), 'left': (-1, 0), 'right': (1, 0)}
            self.wumpus = (3, 2)
            self.holes = [(3, 1), (3, 3), (3, 4), (2, 5)]
            self.gold = (4, 1)     # (6, 5)
            self.threats = [self.wumpus] + self.holes

            # setup positive reward after finding the gold and reset to beginning of game and Maze
            self.rewards = {(4, 1, True): 10}

            # setup negative rewards for holes in maze (includes Wumpus location)
            for c, r in self.threats:
                self.rewards[(c, r, True)] = -10
                self.rewards[(c, r, False)] = -10
        else:
        """
        startLocation = (1, 1, False)
        super(RLEnvironment, self).__init__(agent, startLocation)  ## Set location of Agent
        #super(RLEnvironment, self).__init__(agent, (1, 1, False))  ## Set location of Agent

        self.action_dict = {'up': (0, 1), 'down': (0, -1), 'left': (-1, 0), 'right': (1, 0)}
        self.wumpus = (3, 2)
        #self.holes = [(3, 3)]
        self.holes = [(3, 1), (3, 3), (3, 4), (2, 5)]
        self.gold = (6, 5)
        self.threats = [self.wumpus] + self.holes
        #grid = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (4, 1),
        #        (4, 2), (4, 3), (4, 4), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)]

        # setup positive reward after finding the gold and reset to beginning of game and Maze
        self.rewards = {(6, 5, True): 10}

        # setup negative rewards for holes in maze (includes Wumpus location)
        for c, r in self.threats:
            #self.rewards[(c, r, True)] = -10
            self.rewards[(c, r, False)] = -10

        #for c1, r1 in list(set(self.threats) ^ set(grid) ^ set([self.gold])):
        #    self.rewards[(c1, r1, False)] = -1


    def do_action(self, state, action, agent):
        c1, r1, have_gold = state                   ## Breaks state tuple into components x, y, boolean
        c2, r2 = self.action_dict[action]
        rn = r1 + r2
        cn = c1 + c2
        if not have_gold and (cn, rn) == self.gold:
            have_gold = True
        _next = (cn, rn, have_gold)
        if (1 <= rn <= 6) and (1 <= cn <= 6):
            return _next
        return state

    def is_completed(self, state):
        return state in self.rewards.keys()

    def reward(self, state, agent):
        return self.rewards.get(state, -0.08)


class WumpusProblem(RLProblem):

    def actions(self, state):
        actions = ['up', 'down', 'left', 'right']  #MWB - RIGHT WAS SPELLED WRONG rigth - Fixed
        return actions


if __name__ == '__main__':

    #if os.path.isfile('tdq_learn.csv'):
    #        os.remove('tdq_learn.csv')
    #if os.path.isfile('sarsa_learn.csv'):
    #        os.remove('sarsa_learn.csv')
    if os.path.isfile('epsilon_utilities.txt'):
            os.remove('epsilon_utilities.txt')

    if os.path.isfile('boltzmann_utilities.txt'):
            os.remove('boltzmann_utilities.txt')


    agent1 = TDQLearner(WumpusProblem(), temperature_function=make_exponential_temperature(1000, 0.01), discount_factor=0.8)
    # ORIGINAL SETTINGS agent = TDQLearner(WumpusProblem(), temperature_function=make_exponential_temperature(1000, 0.01), discount_factor=0.8)

    #agent2 = SARSALearner(WumpusProblem(), temperature_function=make_exponential_temperature(1000, 0.01), discount_factor=0.8)

    game = WumpusEnvironment([agent1])

    # p = PerformanceCounter([agent1], ['Q-Epsilon'])

    print 'Training...'

    for i in range(5000):
        #game.run(viewer=WumpusViewer(game))   ## Will show visual of training
        game.run()
    # p.show_statistics()                       ## Produces graphical statistics about training

    # TEST Concept of second routing
    #agent2 = SARSALearner(WumpusProblem(), temperature_function=make_exponential_temperature(1000, 0.01), discount_factor=0.8)
    #game2 = WumpusEnvironment([agent2])
    #for i in range(5000):
    #    game2.run()


    print "Finished Training"
    game.run(viewer=WumpusViewer(game))
    print "running the game after training"
    #game.run()

    print "All Done - Finally"