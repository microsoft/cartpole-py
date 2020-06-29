inkling "2.0"

using Math
using Goal

# Length of the cartpole track in meters
const TrackLength = 0.5

# Maximum angle of pole in radians before it has fallen
const MaxPoleAngle = (12 * Math.Pi) / 180

# Define a type that represents the per-iteration state
# returned by the simulator.
type SimState {
    # Position of cart in meters
    cart_position: number,
    # Velocity of cart in x direction in meters/sec
    cart_velocity: number,
    # Current angle of pole in radians
    pole_angle: number,
    # Angular velocity of pole in radians/sec
    pole_angular_velocity: number,
    # Pole position in meters
    pole_center_position: number,
    # Pole velocity in meters/sec
    pole_center_velocity: number,
    # Target pole position in meters
    target_pole_position: number,
}

# Define a type that represents the per-iteration action
# accepted by the simulator.
type SimAction {
    command: number<-1 .. 1>,
}

# Per-episode configuration that can be sent to the simulator.
# All iterations within an episode will use the same configuration.
type SimConfig {
    # Starting position of cart in meters
    initial_cart_position: number,
    # Starting angle of pole in radians
    initial_pole_angle: number,
    # Target position of pole in meters
    target_pole_position: number,
}

simulator Simulator(action: SimAction, config: SimConfig): SimState {
}

# Define a concept graph
graph (input: SimState): SimAction {
    concept Concept1(input): SimAction {

        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source Simulator
            
            # Add goals here describing what you want to teach the brain
            # See the Inkling documentation for goals syntax
            # https://docs.microsoft.com/bonsai/inkling/keywords/goal
            goal (State: SimState) {
                avoid `Fall Over`:
                    Math.Abs(State.pole_angle) in Goal.RangeAbove(MaxPoleAngle)
                avoid `Out Of Range`:
                    Math.Abs(State.cart_position) in Goal.RangeAbove(TrackLength / 2)
            }

            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 120
            }

            lesson `Randomize Start` {
                # Specify the configuration parameters that should be varied
                # from one episode to the next during this lesson.
                scenario {
                    initial_cart_position: number<-0.2 .. 0.2>,
                    initial_pole_angle: number<-0.01 .. 0.01>,
                    target_pole_position: 0,
                }
            }
        }
    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/cartpoleviz/"
