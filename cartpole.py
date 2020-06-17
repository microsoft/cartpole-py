"""
Classic cart-pole system implemented by Rich Sutton et al.
Derived from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict

import math
import os
import random
import sys
import json
from typing import Dict, Any


from sim_common import SimulatorSession
from microsoft_bonsai_api.client import BonsaiClientConfig
from microsoft_bonsai_api.simulator.models import SimulatorInterface


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
class CartPoleModel(SimulatorSession):
    def reset(
        self,
        initial_cart_position: float = 0,
        initial_pole_angle: float = 0,
        target_pole_position: float = 0,
    ):

        # cart position (m)
        self._cart_position = 0

        # cart velocity (m/s)
        self._cart_velocity = 0

        # cart angle (rad)
        self._pole_angle = 0

        # pole angular velocity (rad/s)
        self._pole_angular_velocity = 0

        # pole position (m)
        self._pole_center_position = 0

        # pole velocity (m/s)
        self._pole_center_velocity = 0

        # target pole position (m)
        self._target_pole_position = 0

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

    def halted(self):
        # If the pole has fallen past 45 degrees, there's no use in continuing.
        return abs(self._pole_angle) >= math.pi / 4

    def state(self):
        return {
            "cart_position": self._cart_position,
            "cart_velocity": self._cart_velocity,
            "pole_angle": self._pole_angle,
            "pole_angular_velocity": self._pole_angular_velocity,
            "pole_center_position": self._pole_center_position,
            "pole_center_velocity": self._pole_center_velocity,
            "target_pole_position": self._target_pole_position,
        }

    # Callbacks
    def get_state(self):
        return self.state()

    def get_interface(self) -> SimulatorInterface:
        interface_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "cartpole_interface.json"
        )
        with open(interface_file_path, "r") as file:
            json_interface = file.read()
        interface = json.loads(json_interface)
        return SimulatorInterface(
            name=interface["name"],
            timeout=interface["timeout"],
            simulator_context=self.get_simulator_context(),
            description=interface["description"],
        )

    def episode_start(self, config: Dict[str, Any]):
        self.reset(
            config.get("initial_cart_position") or 0,
            config.get("initial_pole_angle") or 0,
            config.get("target_pole_position") or 0,
        )

    def episode_step(self, action: Dict[str, Any]):
        self.step(action.get("command") or 0)


if __name__ == "__main__":
    config = BonsaiClientConfig(argv=sys.argv)
    cartpole = CartPoleModel(config)
    cartpole.reset()
    while cartpole.run():
        continue
