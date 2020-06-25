"""
Classic cart-pole system implemented by Rich Sutton et al.
Derived from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict

import math
import random

# Constants
GRAVITY = 9.8  # a classic...
CART_MASS = 0.31  # kg
POLE_MASS = 0.055  # kg
TOTAL_MASS = CART_MASS + POLE_MASS
POLE_HALF_LENGTH = 0.4 / 2  # half the pole's length in m
POLE_MASS_LENGTH = POLE_MASS * POLE_HALF_LENGTH
FORCE_MAG = 1.0
STEP_DURATION = 0.02  # seconds between state updates (20ms)
TRACK_WIDTH = 1.0  # m
FORCE_NOISE = 0.02  # % of FORCE_MAG

# Model parameters
class CartPoleModel():
    def __init__(self):
        self.reset()

    def reset(self,
             initial_cart_position: float = 0,
             initial_pole_angle: float = 0,
             target_pole_position: float = 0,
        ):
        # cart position (m)
        self._cart_position = initial_cart_position

        # cart velocity (m/s)
        self._cart_velocity = 0

        # cart angle (rad)
        self._pole_angle = initial_pole_angle

        # pole angular velocity (rad/s)
        self._pole_angular_velocity = 0

        # pole position (m)
        self._pole_center_position = 0

        # pole velocity (m/s)
        self._pole_center_velocity = 0

        # target pole position (m)
        self._target_pole_position = target_pole_position

    def step(self, command: float):
        # We are expecting the input command to be -1 or 1,
        # but we'll support a continuous action space.
        # Add a small amount of random noise to the force so
        # the policy can't succeed by simply applying zero
        # force each time.
        force = FORCE_MAG * (command + random.uniform(-0.02, 0.02))

        cosTheta = math.cos(self._pole_angle)
        sinTheta = math.sin(self._pole_angle)

        temp = (
            force + POLE_MASS_LENGTH * self._pole_angular_velocity ** 2 * sinTheta
        ) / TOTAL_MASS
        angularAccel = (GRAVITY * sinTheta - cosTheta * temp) / (
            POLE_HALF_LENGTH * (4.0 / 3.0 - (POLE_MASS * cosTheta ** 2) / TOTAL_MASS)
        )
        linearAccel = temp - (POLE_MASS_LENGTH * angularAccel * cosTheta) / TOTAL_MASS

        self._cart_position = self._cart_position + STEP_DURATION * self._cart_velocity
        self._cart_velocity = self._cart_velocity + STEP_DURATION * linearAccel

        self._pole_angle = (
            self._pole_angle + STEP_DURATION * self._pole_angular_velocity
        )
        self._pole_angular_velocity = (
            self._pole_angular_velocity + STEP_DURATION * angularAccel
        )

        # Use the pole center, not the cart center, for tracking
        # pole center velocity.
        self._pole_center_position = (
            self._cart_position + math.sin(self._pole_angle) * POLE_HALF_LENGTH
        )
        self._pole_center_velocity = (
            self._cart_velocity
            + math.sin(self._pole_angular_velocity) * POLE_HALF_LENGTH
        )