# Logistics Optimization Game using Minimax Algorithm in AI

This project is an AI-powered logistics simulation game that models the delivery of perishable goods across major Indian cities. It uses game theory (Minimax algorithm) and GUI elements to simulate disruptions, delivery planning, and optimize routes based on shelf-life constraints.

## Features

* 🗺️ Map of Indian cities connected by weighted routes
* 🚚 Delivery simulation for perishable goods (Milk, Fruits, Medicines)
* ⚠️ Real-time disruption simulation (Minor/Major delays)
* 🧠 AI-based path planning using Minimax Algorithm
* 🧮 Route cost and shelf-life-based evaluation function
* 🖼️ Visual representation of routes and disruptions using NetworkX and Matplotlib
* 🎮 GUI with tkinter to simulate game interactions

## Technologies Used

* **Python 3**
* **Tkinter** for GUI
* **NetworkX** and **Matplotlib** for map visualization

## How it Works

1. **User Input:** Source, Destination, Item to deliver, and Difficulty Level.
2. **AI Route Planning:** Uses a Minimax-based turn-based simulation to find the optimal route under shelf-life and delay constraints.
3. **Disruption Simulation:** User can simulate disruptions (15min or 30min delay) manually.
4. **GUI Visualization:** Real-time update of game state, info logs, and map display with highlighted disruptions.

## Setup Instructions

### Prerequisites

* Python 3.x
* Install required packages:

```bash
pip install networkx matplotlib
```

### Running the App

```bash
python main.py
```

### Controls

* **Start Game**: Begins simulation with given inputs
* **Introduce Disruption**: Adds random delay to current route
* **Next Move**: Progress to next node in route
* **Show Map**: Displays the city network graph with disruptions

## Project Structure

```
.
├── main.py       # Contains all logic: AI, GUI, Graph, Game Loop
├── README.md     # You're here
```

## Cities and Routes

Cities like Delhi, Jaipur, Mumbai, Chennai, etc., are connected in a graph. Each edge has a time cost (representing delivery time). Disruptions increase these costs.

## Shelf Life of Goods

* **Milk**: 50 units
* **Fruits**: 70 units
* **Medicines**: 90 units

## AI Decision-Making

* **Minimax Algorithm** simulates both optimal and worst-case disruptions.
* **Evaluation Function** considers remaining shelf life, disruption penalties, and distance.

## Screenshots
# Home Page UI
![image](https://github.com/user-attachments/assets/c411c343-6665-4e3e-9e68-ebebdb6f0c6d)
# Show Map UI
![image](https://github.com/user-attachments/assets/93005443-4302-4abf-a16f-8add6af9ee8a)
# Show Map UI after Disruption is introduced
![image](https://github.com/user-attachments/assets/26aa0606-6180-4435-8a90-2f653e201b1b)
![image](https://github.com/user-attachments/assets/1874d382-e6f7-417d-81c0-cc3e833f448e)
# Goods Delivered Successfully (AI Wins)
![image](https://github.com/user-attachments/assets/5e0f893c-aea1-47ec-855b-e5f9c3ceb28f)


## Contribution

PRs and suggestions are welcome! Please open an issue first to discuss what you would like to change.

## License

This project is under the [MIT License](LICENSE).

---

Built with ❤️ to simulate smart and adaptive logistics solutions for perishable goods.
