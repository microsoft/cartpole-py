#!/usr/bin/env python3

"""
MSFT Bonsai SDK3 Template for Simulator Integration using Python
Copyright 2020 Microsoft
Usage:
  For registering simulator with the Bonsai service for training:
    python __main__.py --api-host https://api.bons.ai \
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
from microsoft_bonsai_api.simulator.client import (
    BonsaiClientConfig,
    BonsaiClient
)
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorState,
    SimulatorInterface,
)
from sim.cartpole import CartPoleModel
import math

class TemplateSimulatorSession():
    def __init__(self):
        self.cartpole = CartPoleModel()
    
    def get_state(self):
        """ Called to retreive the current state of the simulator. """
        return {
            "cart_position": self.cartpole._cart_position,
            "cart_velocity": self.cartpole._cart_velocity,
            "pole_angle": self.cartpole._pole_angle,
            "pole_angular_velocity": self.cartpole._pole_angular_velocity,
            "pole_center_position": self.cartpole._pole_center_position,
            "pole_center_velocity": self.cartpole._pole_center_velocity,
            "target_pole_position": self.cartpole._target_pole_position,
        }
    
    def episode_start(self, config: Dict[str, Any]):
        """ Called at the start of each episode """
        self.cartpole.reset(
            config.get("initial_cart_position") or 0,
            config.get("initial_pole_angle") or 0,
            config.get("target_pole_position") or 0,
        )

    def episode_step(self, action: Dict[str, Any]):
        """ Called for each step of the episode """
        self.cartpole.step(action.get("command") or 0)

    def halted(self) -> bool:
        """ Should return True if the simulator cannot continue"""
        # If the pole has fallen past 45 degrees, there's no use 
        # in continuing.
        return abs(self.cartpole._pole_angle) >= math.pi / 4

if __name__ == "__main__":
    # Grab standardized way to interact with sim API
    sim = TemplateSimulatorSession()

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

    try:
        while True:
            # Advance by the new state depending on the event type
            sim_state = SimulatorState(
                            sequence_id=sequence_id, state=sim.get_state(), 
                            halted=sim.halted()
            )
            event = client.session.advance(
                        workspace_name=config_client.workspace, 
                        session_id=registered_session.session_id, body=sim_state
            )
            sequence_id = event.sequence_id
            print("[{}] Last Event: {}".format(time.strftime('%H:%M:%S'), 
                                               event.type))

            # Event loop
            if event.type == 'Idle':
                time.sleep(event.idle.callback_time)
                print('Idling...')
            elif event.type == 'EpisodeStart':
                sim.episode_start(event.episode_start.config)
            elif event.type == 'EpisodeStep':
                sim.episode_step(event.episode_step.action)
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
    except KeyboardInterrupt:
        # Gracefully unregister with keyboard interrupt
        client.session.delete(
            workspace_name=config_client.workspace, 
            session_id=registered_session.session_id
        )
        print("Unregistered simulator.")
    except Exception as err:
        # Gracefully unregister for any other exceptions
        client.session.delete(
            workspace_name=config_client.workspace, 
            session_id=registered_session.session_id
        )
        print("Unregistered simulator because: {}".format(err))