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

if __name__ == '__main__':
    """Usage:
    For registering simulator with the Bonsai service for training:
        python cartpole.py --api-host https://api.bons.ai \
            --workspace <workspace_id> \
            --accesskey="<access_key> \
    Then connect your registered simulator to a Brain via UI.
    Alternatively, one can set the SIM_ACCESS_KEY and SIM_WORSKPACE as
    environment variables.
    """
    import os
    import sys
    import json
    import time
    from typing import Dict, Any, Optional
    from microsoft_bonsai_api.client import BonsaiClientConfig, BonsaiClient
    from microsoft_bonsai_api.simulator.models import (
        SimulatorState,
        SimulatorInterface,
    )

    from cartpole import CartPoleModel

    # Create entry point to simulator API
    sim = CartPoleModel()

    # Configure client to interact with Bonsai service
    config_client = BonsaiClientConfig()
    client = BonsaiClient(config_client)

    # Load json file as simulator integration config type file
    with open('cartpole_interface.json') as file:
        interface = json.load(file)

    # Create simulator session and init sequence id
    registration_info = SimulatorInterface(
                            name=interface['name'], 
                            timeout=interface['timeout'], 
                            simulator_context=config_client.simulator_context, 
    )
    registered_session = client.session.create(
                            workspace_name=config_client.workspace, 
                            body=registration_info
    )
    print("Registered simulator.")
    sequence_id = 1

    while True:
        # Advance by the new state depending on the event type
        sim_state = SimulatorState(
            session_id=registered_session.session_id,
            sequence_id=sequence_id, 
            state={
                "cart_position": sim._cart_position,
                "cart_velocity": sim._cart_velocity,
                "pole_angle": sim._pole_angle,
                "pole_angular_velocity": sim._pole_angular_velocity,
                "pole_center_position": sim._pole_center_position,
                "pole_center_velocity": sim._pole_center_velocity,
                "target_pole_position": sim._target_pole_position,
                }, 
            halted=abs(sim._pole_angle) >= math.pi / 4
        )
        event = client.session.advance(
                    workspace_name=config_client.workspace, 
                    session_id=registered_session.session_id, 
                    body=sim_state
        )
        sequence_id = event.sequence_id
        print("[{}] Last Event: {}".format(time.strftime('%H:%M:%S'), 
                                            event.type))

        # Event loop
        if event.type == 'Idle':
            time.sleep(event.idle.callback_time)
            print('Idling...')
        elif event.type == 'EpisodeStart':
            sim.reset(
                event.episode_start.config['initial_cart_position'],
                event.episode_start.config['initial_pole_angle'],
                event.episode_start.config['target_pole_position']
            )
        elif event.type == 'EpisodeStep':
            sim.step(event.episode_step.action['command'])
        elif event.type == 'EpisodeFinish':
            print('Episode Finishing...')
        elif event.type == 'Unregister':
            client.session.delete(
                workspace_name=config_client.workspace, 
                session_id=registered_session.session_id
            )
            print("Unregistered simulator.")
        else:
            pass