from utils.direction import *
import random
from trainers.abctrainer import ABCTrainer
import numpy as np

class QLearningTrainer(ABCTrainer):

    def __init__(self, tau_init, tau_decay, alpha_init, alpha_decay,
                    gamma, decay_rate, size_x, size_y):

        super().__init__(gamma, decay_rate, size_x, size_y, False)

        # Training data
        self.q_dict = {}
        self.tau_init = tau_init
        self.tau = tau_init
        self.tau_decay = tau_decay
        self.alpha = alpha_init
        self.alpha_decay = alpha_decay

    # Implement abstract method
    def update_hyperparameters(self):
        super().update_hyperparameters()
        if self.iter % self.decay_rate == 0:
            if self.tau > 0.2:
                self.tau *= self.tau_decay
            self.alpha *= self.alpha_decay

    # Implement abstract method
    def get_state(self):
        super().get_state()
        danger = list(self.get_danger().values())
        food = list(self.get_food().values())
        return self._hash_bin(danger + food)

    # Implement abstract method
    def choose_action(self, state):
        super().choose_action(state)
        return np.random.choice(list(Direction), p=self._softmax(state))

    # Implement abstract method
    def update_q_dict(self, state, state2, action, action2):
        super().update_q_dict(state, state2, action, action2)
        if state not in self.q_dict:
            self.q_dict[state] = dict.fromkeys(list(Direction), 0)
        if state2 not in self.q_dict:
            self.q_dict[state2] = dict.fromkeys(list(Direction), 0)
        prev = self.q_dict[state][action]

        #Q-learning update
        self.q_dict[state][action] = prev + self.alpha * (
            self.reward +
            self.gamma * self.q_dict[state2][max(self.q_dict[state2],
                key=self.q_dict[state2].get)] - prev
        )

    # Implement abstract method
    def print_recap(self):
        super().print_recap()
        print(('n_iter: %4d | best_score: %2d | avg_score: %5.2f ' +
                '| tau: %6.3f | alpha: %6.4f | q_dict_size: %3d') % (
                self.iter, self.best_score, self.sum_score/self.decay_rate,
                self.tau, self.alpha, len(self.q_dict)
        ))

    # walls & snake_body & snake_pos
    def get_danger(self):
        danger = dict.fromkeys(list(Direction), 0)

        if self.snake_pos[0] < 1:
            danger[Direction.LEFT] = 1
        if self.snake_pos[0] > self.size_x - 2:
            danger[Direction.RIGHT] = 1
        if self.snake_pos[1] < 1:
            danger[Direction.DOWN] = 1
        if self.snake_pos[1] > self.size_y - 2:
            danger[Direction.UP] = 1

        for block in self.snake_body[1:]:
            if self.get_distance(block) <= 1:
                direction = self.get_direction(block).cast()
                danger[direction] = 1

        return danger

    # food_pos & snake_pos
    def get_food(self):
        food = dict.fromkeys(list(ExtendedDirection), 0)
        food[self.get_direction(self.food_pos)] = 1
        return food

    # returns the corresponding value of the binary array
    def _hash_bin(self, array):
        hash = 0
        n = len(array)
        power = 1
        for i in range(n):
            hash += array[n-1-i] * power
            power *= 2
        return hash

    def _softmax(self, state):
        try:
            weights = np.array([np.exp(self.q_dict[state][action]/self.tau)
                                    for action in list(Direction)])
            wsum = sum(weights)
            return weights/wsum
        except KeyError:
            return np.array([1/4,1/4,1/4,1/4])
