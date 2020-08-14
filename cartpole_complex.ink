# This sample demonstrates how to teach a policy for controlling
# a cartpole (inverted pendulum) device.

inkling "2.0"

using Math
using Goal

# Length of the cartpole track in meters
const TrackLength = 0.8

# Maximum angle of pole in radians before it is considered "fallen"
const MaxPoleAngle = (12 * 2 * Math.Pi) / 360

# How close to the target (in meters) must the cart be to be
# considered successful?
const CloseEnough = 0.004

# Define a type that represents the per-iteration state
# returned by the simulator.
type SimState {
    # Position of cart in meters
    cart_position: number,

    # Velocity of cart in x direction in meters/sec
    cart_velocity: number,

    # Current angle of pole in radians
    pole_angle: number<-Math.Pi .. Math.Pi>,

    # Angular velocity of the pole in radians/sec
    pole_angular_velocity: number,

    # X position of center of pole in meters
    pole_center_position: number,

    # X velocity of center of pole in meters/sec
    pole_center_velocity: number,

    # Target pole position in meters; does not
    # change throughout a single episode
    target_pole_position: number,
}

# Define a type that represents the per-iteration state
# that will be fed to the resulting policy at prediction
# time. This is a subset of the state available state
# provided by the simulator.
type ObservableState {
    # Position of cart in meters
    cart_position: number,

    # Velocity of cart in x direction in meters/sec
    cart_velocity: number,

    # Current angle of pole in radians
    pole_angle: number<-Math.Pi .. Math.Pi>,

    # Angular velocity of the pole in radians/sec
    pole_angular_velocity: number,

    # Target pole position in meters; does not
    # change throughout a single episode
    target_pole_position: number,
}

# Define a type that represents the per-iteration action
# accepted by the simulator.
type SimAction {
    # Amount of force in x direction to apply to the cart.
    command: number<-1 .. 1>
}

# Define a type that represents the per-episode configuration
# settings supported by the simulator.
type SimConfig {
    # Starting cart position in meters
    initial_cart_position: number<-TrackLength / 2 .. TrackLength / 2>,

    # Starting pole angle in radians
    initial_pole_angle: number<-Math.Pi .. Math.Pi>,

    # Target pole position in meters
    target_pole_position: number<-TrackLength / 2 .. TrackLength / 2>,
}

# Define a concept graph with a single concept
graph (input: ObservableState): SimAction {
    concept MoveToTargetAndBalance(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action and configuration info as input
            # and outputs a state.
            source simulator (Action: SimAction, Config: SimConfig): SimState {
            }

            # The objective of training is expressed as a goal with three
            # subgoals: don't let the pole fall over, don't move
            # the cart off the track, and move to the target position.
            goal (State: SimState) {
                avoid FallOver:
                    Math.Abs(State.pole_angle) in Goal.RangeAbove(MaxPoleAngle)
                avoid OutOfRange:
                    Math.Abs(State.cart_position) in Goal.RangeAbove(TrackLength / 2)
                drive MoveToTarget:
                    State.cart_position in Goal.Sphere(State.target_pole_position, CloseEnough)
            }

            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 120
            }

            # First lesson: start with the pole in the same position
            lesson VaryTarget {
                scenario {
                    # Vary the target position
                    target_pole_position: number<-TrackLength / 4 .. TrackLength / 4>,

                    # Keep the starting position and angle constant
                    initial_cart_position: 0,
                    initial_pole_angle: 0
                }
            }

            # Second lesson: vary the start position and angle
            lesson VaryTargetAndStart {
                scenario {
                    # Vary the target position
                    target_pole_position: number<-TrackLength / 4 .. TrackLength / 4>,

                    # Vary the starting position and angle
                    initial_cart_position: number<-TrackLength / 4 .. TrackLength / 4>,
                    initial_pole_angle: number<-MaxPoleAngle / 2 .. MaxPoleAngle / 2>
                }
            }
        }
    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/cartpoleviz/"
