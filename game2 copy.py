# save this file as logistics_game.py and run with Python 3
import networkx as nx
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import messagebox
import random

# ---------------------------
# Graph and Heuristic
# ---------------------------

map_graph = {
    'Delhi': {'Jaipur': 5, 'Lucknow': 6},
    'Jaipur': {'Delhi': 5, 'Ahmedabad': 8, 'Mumbai': 12},
    'Lucknow': {'Delhi': 6, 'Patna': 8, 'Kolkata': 15},
    'Ahmedabad': {'Jaipur': 8, 'Mumbai': 6},
    'Mumbai': {'Ahmedabad': 6, 'Jaipur': 12, 'Hyderabad': 8, 'Bangalore': 15},
    'Hyderabad': {'Mumbai': 8, 'Bangalore': 8, 'Chennai': 9},
    'Bangalore': {'Hyderabad': 8, 'Mumbai': 15, 'Chennai': 6},
    'Chennai': {'Bangalore': 6, 'Hyderabad': 9, 'Kolkata': 18},
    'Kolkata': {'Chennai': 18, 'Lucknow': 15, 'Patna': 6},
    'Patna': {'Kolkata': 6, 'Lucknow': 8}
}

class Vehicle:
    def __init__(self, item, quantity, shelf_life):
        self.item = item
        self.quantity = quantity
        self.shelf_life = shelf_life
        self.position = None
        self.eta = 0

class GameState:
    def __init__(self, vehicle, current_node, remaining_path, disruptions, cost, delivered):
        self.vehicle = vehicle
        self.current_node = current_node
        self.remaining_path = remaining_path
        self.disruptions = disruptions
        self.cost = cost
        self.delivered = delivered

    def is_terminal(self):
        return len(self.remaining_path) == 0 or self.vehicle.shelf_life <= 0 or self.delivered

    def get_possible_moves(self):
        if self.is_terminal():
            return []

        next_node = self.remaining_path[0]
        base_time = map_graph[self.current_node][next_node]
        moves = []

        for delay in [0, 15, 30]:  # Normal, Minor, Major
            new_path = self.remaining_path[1:]
            new_life = self.vehicle.shelf_life - (base_time + delay)
            new_cost = self.cost + base_time + delay
            new_state = GameState(
                vehicle=Vehicle(self.vehicle.item, self.vehicle.quantity, new_life),
                current_node=next_node,
                remaining_path=new_path,
                disruptions=self.disruptions + ([delay] if delay > 0 else []),
                cost=new_cost,
                delivered=(len(new_path) == 0 and new_life > 0)
            )
            moves.append((delay, new_state))

        return moves

def evaluate_state(state: GameState):
    if state.delivered:
        return 100 - state.cost
    if state.vehicle.shelf_life <= 0:
        return -100
    dist_penalty = len(state.remaining_path) * 10
    spoilage_risk = max(0, 50 - state.vehicle.shelf_life)
    disruption_penalty = len(state.disruptions) * 5
    return 50 - dist_penalty - spoilage_risk - disruption_penalty

def minimax(state: GameState, depth, is_maximizing):
    if depth == 0 or state.is_terminal():
        return evaluate_state(state), state

    if is_maximizing:
        max_eval = float('-inf')
        best_state = None
        for _, child in state.get_possible_moves():
            eval, _ = minimax(child, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_state = child
        return max_eval, best_state
    else:
        min_eval = float('inf')
        best_state = None
        for _, child in state.get_possible_moves():
            eval, _ = minimax(child, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_state = child
        return min_eval, best_state

# ---------------------------
# GUI
# ---------------------------

class LogisticsGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Perishable Goods Logistics Optimizer")

        self.input_frame = tk.Frame(root)
        self.input_frame.pack()

        tk.Label(self.input_frame, text="Source:").grid(row=0, column=0)
        tk.Label(self.input_frame, text="Destination:").grid(row=1, column=0)
        tk.Label(self.input_frame, text="Item:").grid(row=2, column=0)
        tk.Label(self.input_frame, text="Quantity:").grid(row=3, column=0)

        self.source_entry = tk.Entry(self.input_frame)
        self.destination_entry = tk.Entry(self.input_frame)
        self.item_entry = tk.Entry(self.input_frame)
        self.quantity_entry = tk.Entry(self.input_frame)

        self.source_entry.grid(row=0, column=1)
        self.destination_entry.grid(row=1, column=1)
        self.item_entry.grid(row=2, column=1)
        self.quantity_entry.grid(row=3, column=1)

        self.start_btn = tk.Button(self.input_frame, text="Start Game", command=self.start_game)
        self.start_btn.grid(row=4, columnspan=2)

        self.info_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.info_label.pack(pady=10)

        self.disrupt_btn = tk.Button(root, text="Introduce Disruption", command=self.introduce_disruption, state='disabled')
        self.disrupt_btn.pack()

        self.next_btn = tk.Button(root, text="Next Move", command=self.next_move, state='disabled')
        self.next_btn.pack()

        self.map_btn = tk.Button(root, text="Show Map", command=self.show_map)
        self.map_btn.pack()


        self.reset()
    def show_map(self):
        G = nx.DiGraph()

        # Add edges with weights
        for node in map_graph:
            for neighbor, weight in map_graph[node].items():
                G.add_edge(node, neighbor, weight=weight)

        pos = nx.spring_layout(G, seed=42)  # Consistent layout
        edge_labels = nx.get_edge_attributes(G, 'weight')

        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1000, font_weight='bold', arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        # Highlight source/destination
        if self.vehicle:
            src = self.path[0]
            dst = self.path[-1]
            nx.draw_networkx_nodes(G, pos, nodelist=[src], node_color='green')
            nx.draw_networkx_nodes(G, pos, nodelist=[dst], node_color='red')

        plt.title("Map Representation of Route Network")
        plt.show()


    def reset(self):
        self.vehicle = None
        self.state = None
        self.path = []
        self.route = []

    def find_path(self, src, dst):
        from collections import deque
        queue = deque([(src, [src])])
        visited = set()
        while queue:
            node, path = queue.popleft()
            if node == dst:
                return path
            for neighbor in map_graph.get(node, {}):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def start_game(self):
        src = self.source_entry.get().strip().title()
        dst = self.destination_entry.get().strip().title()
        item = self.item_entry.get().strip()
        quantity = int(self.quantity_entry.get().strip())

        if src not in map_graph or dst not in map_graph:
            messagebox.showerror("Invalid Input", "Invalid Source or Destination")
            return

        path = self.find_path(src, dst)
        if not path or path[0] != src or path[-1] != dst:
            messagebox.showerror("No Route", "No valid path found.")
            return

        self.vehicle = Vehicle(item, quantity, shelf_life=100)
        self.vehicle.position = src
        self.path = path
        self.route = path[1:]
        self.state = GameState(self.vehicle, src, self.route, [], 0, False)
        self.update_info()

        self.disrupt_btn.config(state='normal')
        self.next_btn.config(state='normal')

    def introduce_disruption(self):
        if self.state.is_terminal():
            return

        if self.state.remaining_path:
            next_node = self.state.remaining_path[0]
            map_graph[self.state.current_node][next_node] += 15  # Fixed disruption
            self.state.disruptions.append(f"Delay at {next_node}")
            self.update_info()

    def next_move(self):
        if self.state.is_terminal():
            result = "Delivered Successfully!" if self.state.delivered else "Goods Spoiled!"
            messagebox.showinfo("Game Over", result)
            return

        _, new_state = minimax(self.state, 2, True)
        self.state = new_state
        self.update_info()

    def update_info(self):
        truck_loc = self.state.current_node
        route_str = " -> ".join([truck_loc] + self.state.remaining_path)
        status = f"Truck at: {truck_loc}\nRoute: {route_str}\nETA: {self.state.cost}\nShelf Life: {self.state.vehicle.shelf_life}\nDisruptions: {self.state.disruptions}"
        self.info_label.config(text=status)

# ---------------------------
# Launch App
# ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = LogisticsGameGUI(root)
    root.mainloop()
