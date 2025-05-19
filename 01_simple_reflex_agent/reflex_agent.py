import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Define the 2x2 environment
environment = {
    "Room1": "Clean",
    "Room2": "Dirty",
    "Room3": "Clean",
    "Room4": "Clean"
}

# Mapping for grid positions
room_positions = {
    "Room1": (0, 1),  # top-left
    "Room2": (1, 1),  # top-right
    "Room3": (0, 0),  # bottom-left
    "Room4": (1, 0)   # bottom-right
}

rooms = list(environment.keys())
agent_index = 0  # Start in Room1

# Reflex agent function
def reflex_agent(state):
    return "Clean" if state == "Dirty" else "Move"

# Function to draw the grid
def draw_grid(env, agent_idx, step):
    fig, ax = plt.subplots()
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Step {step} --> Agent in {rooms[agent_idx]}")

    for room, pos in room_positions.items():
        x, y = pos
        color = "green" if env[room] == "Clean" else "red"
        rect = patches.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(x + 0.5, y + 0.5, room, ha='center', va='center', fontsize=12, color='white')

    # Draw the agent
    agent_x, agent_y = room_positions[rooms[agent_idx]]
    agent_rect = patches.Rectangle((agent_x + 0.25, agent_y + 0.25), 0.5, 0.5, facecolor='yellow')
    ax.add_patch(agent_rect)

    plt.pause(1)  # Pause to show the plot
    plt.close()

# Run simulation
if __name__ == "__main__":
    plt.ion()  # Turn on interactive mode
    steps = 8

    for step in range(steps):
        current_room = rooms[agent_index]
        state = environment[current_room]
        action = reflex_agent(state)

        draw_grid(environment, agent_index, step + 1)

        if action == "Clean":
            environment[current_room] = "Clean"
        else:
            agent_index = (agent_index + 1) % len(rooms)

    plt.ioff()
    print("✔ Simulation complete.")
    print("Final Environment State:")
    print(environment)
    plt.show()
    # Final plot to show the last state of the environment

