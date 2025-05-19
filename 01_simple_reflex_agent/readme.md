
# 🧹 Reflex Agent Simulation in a 2x2 Environment

This project simulates a simple **Reflex Agent** that navigates a 2x2 grid environment, deciding whether to clean or move based on its perception of each room's state. It's a fun way to visualize how basic AI agents make decisions in a small world!

---

## 📌 Features

- 🔄 **2x2 Grid Environment** with labeled rooms: `Room1`, `Room2`, `Room3`, `Room4`
- 🧠 **Reflex Agent** logic: 
  - Cleans if the current room is dirty
  - Moves to the next room otherwise
- 🎨 **Visual Simulation** using `matplotlib`:
  - **Red rooms** represent dirty spaces
  - **Green rooms** represent clean spaces
  - A **yellow square** shows the agent's position
- 🔁 Agent loops through the rooms for a number of steps

---

## 🧠 How It Works

1. The environment is defined as a 2x2 grid with clean or dirty status for each room.
2. The agent starts in `Room1`.
3. At each step:
   - It checks the state of the current room.
   - If the room is dirty, it cleans it.
   - Otherwise, it moves to the next room in a clockwise loop.
4. The grid is updated and displayed after each action.

---

## 🚀 Quick Demo

> 💡 Each step shows the current position of the agent and the cleanliness of each room.

_(Optional: Insert a GIF demo here if available)_

---

## 🛠️ Technologies Used

- Python 🐍
- [Matplotlib](https://matplotlib.org/) 📊

---

## 📂 Code Structure

```bash
├── simple_reflex_agent.py
└── README.md
```

---

## 🏁 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/reflex-agent-grid.git
cd reflex-agent-grid
```

### 2. Install Dependencies

Make sure you have Python installed, then install `matplotlib`:

```bash
pip install matplotlib
```

### 3. Run the Simulation

```bash
python simple_reflex_agent.py
```

---

## 🧾 Sample Output

```bash
✔ Simulation complete.
Final Environment State:
{'Room1': 'Clean', 'Room2': 'Clean', 'Room3': 'Clean', 'Room4': 'Clean'}
```

---

## 📌 Customization

- 🧼 Change the initial state of rooms in the `environment` dictionary.
- 🔁 Modify the number of `steps` to control how long the simulation runs.

---

## 📚 Concept Reference

This simulation is inspired by the **Reflex Vacuum Agent** problem from AI studies (Russell & Norvig’s *Artificial Intelligence: A Modern Approach*).

---

## ⭐ Final Words

If you're learning about intelligent agents or want to visualize basic AI logic, this project is a perfect starting point!

Feel free to ⭐ the repo and contribute!
