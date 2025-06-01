import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, simpledialog

# Graph 
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
#coord according to India Map
city_coords = {
    'Delhi': (28.6667, 77.2167),
    'Jaipur': (26.9221, 75.7789),
    'Lucknow': (26.8500, 80.9499),
    'Ahmedabad': (23.0339, 72.5850),
    'Mumbai': (19.0761, 72.8775),
    'Hyderabad': (17.3850, 78.4867),
    'Bangalore': (12.9716, 77.5946),
    'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639),
    'Patna': (25.5941, 85.1376)
}


# global dictionary for items & shelf life
ITEM_SHELF_LIFE = {
    "Milk": 50,
    "Fruits": 70,
    "Medicines": 90
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

# GUI
class LogisticsGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Perishable Goods Logistics Optimizer")
        self.root.configure(bg="#f0f4f8")  # Light bluish background

        # Center the window on the screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

        title = tk.Label(root, text="🚚 Perishable Goods Logistics Optimizer", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#2c3e50")
        title.pack(pady=20)

        self.input_frame = tk.Frame(root, bg="#f0f4f8", padx=20, pady=10)
        self.input_frame.pack()

        label_style = {"font": ("Helvetica", 12), "bg": "#f0f4f8"}

        tk.Label(self.input_frame, text="Source:", **label_style).grid(row=0, column=0, sticky="e", pady=5)
        tk.Label(self.input_frame, text="Destination:", **label_style).grid(row=1, column=0, sticky="e", pady=5)
        tk.Label(self.input_frame, text="Choose Goods:", **label_style).grid(row=2, column=0, sticky="e", pady=5)
        tk.Label(self.input_frame, text="Difficulty:", **label_style).grid(row=3, column=0, sticky="e", pady=5)

        self.difficulty = tk.StringVar()
        self.difficulty.set("Medium")  # default level
        difficulty_options = ["Easy", "Medium", "Hard"]
        tk.OptionMenu(self.input_frame, self.difficulty, *difficulty_options).grid(row=3, column=1)

        self.selected_item = tk.StringVar()
        self.selected_item.set("Milk")  # default
        item_options = list(ITEM_SHELF_LIFE.keys())
        self.item_dropdown = tk.OptionMenu(self.input_frame, self.selected_item, *item_options)
        self.item_dropdown.grid(row=2, column=1)

        self.source_entry = tk.Entry(self.input_frame)
        self.destination_entry = tk.Entry(self.input_frame)
        # self.item_entry = tk.Entry(self.input_frame)

        self.source_entry.grid(row=0, column=1)
        self.destination_entry.grid(row=1, column=1)
        # self.item_entry.grid(row=2, column=1)
        
        #all the buttons to be displayed on the GUI
        btn_style = {"bg": "#3498db", "fg": "white", "font": ("Helvetica", 10, "bold"), "padx": 10, "pady": 5}

        self.start_btn = tk.Button(self.input_frame, text="Start Game", command=self.start_game, **btn_style)
        self.start_btn.grid(row=4, columnspan=2, pady=10)

        self.disrupt_btn = tk.Button(root, text="Introduce Disruption", command=self.introduce_disruption, state='disabled', **btn_style)
        self.disrupt_btn.pack(pady=5)

        self.next_btn = tk.Button(root, text="Next Move", command=self.next_move, state='disabled', **btn_style)
        self.next_btn.pack(pady=5)

        self.map_btn = tk.Button(root, text="Show Map", command=self.show_map, **btn_style)
        self.map_btn.pack(pady=5)

        self.info_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg="#f0f4f8", justify="left")
        self.info_label.pack(pady=10)

        self.reset()

    @staticmethod
    def normalize_coords(coords):
        lats = [lat for lat, lon in coords.values()]
        lons = [lon for lat, lon in coords.values()]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        norm_coords = {}
        for city, (lat, lon) in coords.items():
            x = (lon - min_lon) / (max_lon - min_lon)
            y = (lat - min_lat) / (max_lat - min_lat)
            norm_coords[city] = (x, y)
        return norm_coords


    def show_map(self):
        G = nx.DiGraph()
        disrupted = getattr(self, 'disrupted_edges', set())

        for node in map_graph:
            for neighbor, weight in map_graph[node].items():
                G.add_edge(node, neighbor, weight=weight)

        pos = self.normalize_coords(city_coords)
        edge_labels = nx.get_edge_attributes(G, 'weight')

        plt.figure(figsize=(10, 7))
        nx.draw(G, pos, with_labels=True, node_color='lightblue',
                node_size=1000, font_weight='bold', arrows=True)

        # Highlight disrupted edges
        disrupted_edges = [edge for edge in G.edges if edge in disrupted]
        normal_edges = [edge for edge in G.edges if edge not in disrupted]

        nx.draw_networkx_edges(G, pos, edgelist=normal_edges, edge_color='black')
        nx.draw_networkx_edges(G, pos, edgelist=disrupted_edges, edge_color='red', width=2)

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        if self.vehicle:
            src = self.path[0]
            dst = self.path[-1]
            nx.draw_networkx_nodes(G, pos, nodelist=[src], node_color='green')
            nx.draw_networkx_nodes(G, pos, nodelist=[dst], node_color='red')

        plt.title("Map Representation with Disruptions Highlighted")
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

    #method to satrt the game
    def start_game(self):
        src = self.source_entry.get().strip().title()
        dst = self.destination_entry.get().strip().title()
        item = self.selected_item.get()
        shelf_life = ITEM_SHELF_LIFE[item]

        if src not in map_graph or dst not in map_graph:
            messagebox.showerror("Invalid Input", "Invalid Source or Destination")
            return

        path = self.find_path(src, dst)
        if not path or path[0] != src or path[-1] != dst:
            messagebox.showerror("No Route", "No valid path found.")
            return

        self.vehicle = Vehicle(item, quantity=None, shelf_life=shelf_life)
        self.vehicle.position = src
        self.path = path
        self.route = path[1:]
        self.state = GameState(self.vehicle, src, self.route, [], 0, False)
        self.update_info()

        self.disrupt_btn.config(state='normal')
        self.next_btn.config(state='normal')

    #Helper method for the introduced disruptions function
    def apply_disruption(self, popup, node1, node2, disruption_type):
        popup.destroy()

        level = self.difficulty.get().lower()

        if disruption_type.lower() == 'weather':
            delay = {'easy': 10, 'medium': 15, 'hard': 20}[level]
        else:
            delay = {'easy': 20, 'medium': 30, 'hard': 40}[level]

        map_graph[node1][node2] += delay
        if node2 in map_graph and node1 in map_graph[node2]:
            map_graph[node2][node1] += delay

        label = f"{disruption_type.title()} delay of {delay} at edge {node1}-{node2}"
        self.state.disruptions.append(label)

        # Save for map highlight
        if not hasattr(self, 'disrupted_edges'):
            self.disrupted_edges = set()
        self.disrupted_edges.add((node1, node2))
        self.disrupted_edges.add((node2, node1))  # Assume bi-directional for highlight

        self.recalculate_best_route()
        self.update_info()


    def introduce_disruption(self):
        if self.state.is_terminal():
            return

        edge_input = tk.simpledialog.askstring(
            "Add Disruption",
            "Enter edge (format: City1-City2), e.g. Delhi-Jaipur:"
        )
        if not edge_input or '-' not in edge_input:
            messagebox.showerror("Invalid Format", "Use format City1-City2.")
            return

        node1, node2 = [c.strip().title() for c in edge_input.split('-')]
        if node1 not in map_graph or node2 not in map_graph[node1]:
            messagebox.showerror("Invalid Edge", f"{node1}-{node2} not found.")
            return

        # Dropdown popup for disruption type
        type_popup = tk.Toplevel(self.root)
        type_popup.title("Select Disruption Type")
        tk.Label(type_popup, text="Choose Disruption Type:").pack(pady=5)

        disruption_choice = tk.StringVar(value="Weather")

        tk.OptionMenu(type_popup, disruption_choice, "Weather", "Traffic").pack(pady=5)
        tk.Button(type_popup, text="Apply", command=lambda: self.apply_disruption(
            type_popup, node1, node2, disruption_choice.get()
        )).pack(pady=5)


    def next_move(self):
        if self.state.is_terminal():
            result = "Delivered Successfully!" if self.state.delivered else "Goods Spoiled!"
            messagebox.showinfo("Game Over", result)
            return

        _, new_state = minimax(self.state, 2, True)
        self.state = new_state
        self.update_info()

    def recalculate_best_route(self):
        # Get all paths from current node to destination
        all_paths = list(nx.all_simple_paths(nx.DiGraph(map_graph), self.state.current_node, self.path[-1]))
        best_score = float('-inf')
        best_path = None

        for p in all_paths:
            if len(p) < 2: continue
            vehicle_copy = Vehicle(self.vehicle.item, self.vehicle.quantity, self.state.vehicle.shelf_life)
            candidate_state = GameState(vehicle_copy, p[0], p[1:], self.state.disruptions[:], self.state.cost, False)
            score, _ = minimax(candidate_state, 2, True)
            if score > best_score:
                best_score = score
                best_path = p

        #if suggested path and the new path are not equal
        if best_path and best_path != [self.state.current_node] + self.state.remaining_path:
            self.route = best_path[1:]
            self.path = best_path
            self.state = GameState(self.vehicle, best_path[0], best_path[1:], self.state.disruptions[:], self.state.cost, False)


    def update_info(self):
        truck_loc = self.state.current_node
        route_str = " -> ".join([truck_loc] + self.state.remaining_path)
        # Calculate ETA (sum of weights of remaining path from current_node)
        eta = 0
        current = truck_loc
        for next_node in self.state.remaining_path:
            eta += map_graph[current][next_node]
            current = next_node

        status = (
            f"Truck Currently at: {truck_loc}\n"
            f"Route Status: {route_str}\n"
            f"ETA: {eta}\n"
            f"Elapsed Time: {self.state.cost}\n"
            f"Shelf Life Left: {self.state.vehicle.shelf_life}\n"
            f"Disruptions: {self.state.disruptions}"
        )  

        self.info_label.config(text=status)

# Main function
if __name__ == "__main__":
    root = tk.Tk()
    app = LogisticsGameGUI(root)
    root.mainloop()
