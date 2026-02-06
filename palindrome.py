# Import necessary modules
import tkinter as tk  # For GUI
from tkinter import messagebox  # For showing error dialogs
from collections import deque, defaultdict  # For ARC and set-associative structures
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for embedding plots in Tkinter
import matplotlib.pyplot as plt  # For plotting results
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embed matplotlib in Tkinter
import threading  # To run simulation in a background thread
import time  # For delay in UI updates

# LIFO cache replacement policy class
class LIFO:
    def __init__(self, capacity):
        self.stack = []  # List to simulate a stack
        self.capacity = capacity

    def access(self, addr):
        if addr in self.stack:
            return True  # It's a hit
        if len(self.stack) >= self.capacity:
            self.stack.pop()  # Remove last accessed block
        self.stack.append(addr)  # Add new address to top
        return False  # It's a miss

    def view(self):
        return list(self.stack)  # Return current stack

# ARC (Adaptive Replacement Cache) class
class ARC:
    def __init__(self, capacity):
        self.t1 = deque()  # Recently used
        self.t2 = deque()  # Frequently used
        self.capacity = capacity

    def access(self, addr):
        if addr in self.t1:
            self.t1.remove(addr)
            self.t2.append(addr)  # Promote to frequently used
            return True
        elif addr in self.t2:
            self.t2.remove(addr)
            self.t2.append(addr)  # Reaccessed in t2
            return True
        if len(self.t1) + len(self.t2) >= self.capacity:
            if self.t1:
                self.t1.popleft()  # Remove oldest from t1
            elif self.t2:
                self.t2.popleft()  # Or from t2 if t1 is empty
        self.t1.append(addr)  # Add to t1
        return False

    def view(self):
        return list(self.t1) + list(self.t2)  # Combined view

# CLOCK cache replacement policy class
class CLOCK:
    def __init__(self, capacity):
        self.entries = []  # Cache entries
        self.refs = []  # Reference bits
        self.pointer = 0  # Clock hand
        self.capacity = capacity

    def access(self, addr):
        if addr in self.entries:
            i = self.entries.index(addr)
            self.refs[i] = 1  # Set reference bit
            return True
        if len(self.entries) < self.capacity:
            self.entries.append(addr)
            self.refs.append(1)
        else:
            while self.refs[self.pointer] == 1:
                self.refs[self.pointer] = 0
                self.pointer = (self.pointer + 1) % self.capacity  # Move clock hand
            self.entries[self.pointer] = addr
            self.refs[self.pointer] = 1
            self.pointer = (self.pointer + 1) % self.capacity
        return False

    def view(self):
        return list(self.entries)

# Simulator class to handle address access logic
class CacheSimulator:
    def __init__(self, size, policy_name, mapping, associativity, update_ui):
        self.size = size
        self.mapping = mapping
        self.associativity = associativity
        self.hits = 0
        self.misses = 0
        self.update_ui = update_ui
        self.policy_name = policy_name

        if mapping == 'direct-mapped':
            self.cache = [None] * size  # Simple fixed-size list
        else:
            self.num_sets = size // associativity  # Number of sets in cache
            self.cache = defaultdict(self._create_policy)  # Set-associative

    def _create_policy(self):
        # Return appropriate replacement policy instance
        if self.policy_name == 'LIFO':
            return LIFO(self.associativity)
        elif self.policy_name == 'ARC':
            return ARC(self.associativity)
        elif self.policy_name == 'CLOCK':
            return CLOCK(self.associativity)

    def access(self, address):
        if self.mapping == 'direct-mapped':
            index = address % self.size
            hit = self.cache[index] == address
            if hit:
                self.hits += 1
            else:
                self.cache[index] = address
                self.misses += 1
            self.update_ui(address, hit, self.cache)
        else:
            set_index = address % self.num_sets
            block = self.cache[set_index]
            hit = block.access(address)
            if hit:
                self.hits += 1
            else:
                self.misses += 1
            self.update_ui(address, hit, block.view())

# GUI Class using Tkinter
class CacheGUI:
    def __init__(self, root):
        self.root = root
        root.title("Interactive Cache Simulator")

        # Main container
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top input controls
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Trace input
        tk.Label(controls_frame, text="Memory Trace (comma-separated):").pack()
        self.trace_entry = tk.Entry(controls_frame, width=50)
        self.trace_entry.pack()

        # Policy dropdown
        tk.Label(controls_frame, text="Replacement Policy:").pack()
        self.policy_var = tk.StringVar(value='LIFO')
        tk.OptionMenu(controls_frame, self.policy_var, 'LIFO', 'ARC', 'CLOCK').pack()

        # Mapping dropdown
        tk.Label(controls_frame, text="Mapping Type:").pack()
        self.mapping_var = tk.StringVar(value='set-associative')
        tk.OptionMenu(controls_frame, self.mapping_var, 'set-associative', 'direct-mapped').pack()

        # Cache size input
        tk.Label(controls_frame, text="Cache Size:").pack()
        self.size_entry = tk.Entry(controls_frame)
        self.size_entry.insert(0, '4')
        self.size_entry.pack()

        # Associativity input
        tk.Label(controls_frame, text="Associativity (if applicable):").pack()
        self.assoc_entry = tk.Entry(controls_frame)
        self.assoc_entry.insert(0, '2')
        self.assoc_entry.pack()

        # Start simulation button
        tk.Button(controls_frame, text="Start Simulation", command=self.start_simulation).pack(pady=10)

        # Results display (text + graph)
        results_frame = tk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Text area
        text_frame = tk.Frame(results_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(text_frame, text="Simulation Log:").pack(anchor=tk.W)

        text_scroll_frame = tk.Frame(text_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True)
        self.text = tk.Text(text_scroll_frame, height=20, width=40, font=("Courier", 10))
        scrollbar = tk.Scrollbar(text_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

        # Graph area
        self.graph_frame = tk.Frame(results_frame)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(self.graph_frame, text="Results Visualization:").pack(anchor=tk.W)
        self.canvas = None
        placeholder = tk.Label(self.graph_frame, text="Graph will appear after simulation",
                               font=("Arial", 12), fg="gray")
        placeholder.pack(expand=True)

    def plot_results(self, hits, misses):
        def create_graph():
            try:
                if self.canvas:
                    self.canvas.get_tk_widget().destroy()
                    self.canvas = None

                # Clear widgets except title label
                for widget in self.graph_frame.winfo_children():
                    if not isinstance(widget, tk.Label) or "Results Visualization" not in widget.cget("text"):
                        if widget != self.graph_frame.winfo_children()[0]:
                            widget.destroy()

                # Create bar chart
                labels = ['Hits', 'Misses']
                values = [hits, misses]
                colors = ['green', 'red']
                fig, ax = plt.subplots(figsize=(6, 4))
                bars = ax.bar(labels, values, color=colors)
                ax.set_title("Cache Simulation Results")
                ax.set_ylabel("Count")

                # Add bar labels
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{value}', ha='center', va='bottom')

                # Set y-axis limits
                ax.set_ylim(0, max(values) * 1.2)

                self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                plt.close(fig)
            except Exception as e:
                # Fallback if graph fails
                print(f"Error creating graph: {e}")
                result_text = f"Results:\nHits: {hits}\nMisses: {misses}\nHit Rate: {hits/(hits+misses)*100:.1f}%"
                fallback_label = tk.Label(self.graph_frame, text=result_text,
                                          font=("Arial", 12), bg="lightgray",
                                          relief=tk.RAISED, padx=10, pady=10)
                fallback_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.root.after(0, create_graph)

    def update_display(self, address, hit, cache_state):
        def gui_update():
            self.text.insert(tk.END, f"Access {address}: {'HIT' if hit else 'MISS'}\n")
            self.text.insert(tk.END, f"Cache State: {cache_state}\n")
            self.text.insert(tk.END, "-" * 30 + "\n")
            self.text.see(tk.END)

        self.root.after(0, gui_update)
        time.sleep(0.5)  # Delay for visual pacing

    def run_simulation(self, trace, sim):
        for addr in trace:
            sim.access(addr)

        def final_update():
            self.text.insert(tk.END, "\n--- Simulation Complete ---\n")
            self.text.insert(tk.END, f"Total accesses: {len(trace)}\n")
            self.text.insert(tk.END, f"Hits: {sim.hits}\n")
            self.text.insert(tk.END, f"Misses: {sim.misses}\n")
            hit_ratio = 100 * sim.hits / len(trace) if len(trace) > 0 else 0
            self.text.insert(tk.END, f"Hit Ratio: {hit_ratio:.2f}%\n")
            self.text.insert(tk.END, f"Miss Ratio: {100 - hit_ratio:.2f}%\n")
            self.text.see(tk.END)

        def update_graph():
            self.plot_results(sim.hits, sim.misses)

        self.root.after(0, final_update)
        self.root.after(100, update_graph)

    def start_simulation(self):
        try:
            trace = list(map(int, self.trace_entry.get().split(',')))  # Parse addresses
            policy = self.policy_var.get()
            mapping = self.mapping_var.get()
            size = int(self.size_entry.get())
            assoc = int(self.assoc_entry.get())

            # Clear output areas
            self.text.delete(1.0, tk.END)
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            for widget in self.graph_frame.winfo_children():
                if not isinstance(widget, tk.Label) or "Results Visualization" not in widget.cget("text"):
                    widget.destroy()

            # Show "running" label
            placeholder = tk.Label(self.graph_frame, text="Running simulation...",
                                   font=("Arial", 12), fg="blue")
            placeholder.pack(expand=True)

            # Start simulation thread
            sim = CacheSimulator(size=size, policy_name=policy, mapping=mapping,
                                 associativity=assoc, update_ui=self.update_display)
            threading.Thread(target=self.run_simulation, args=(trace, sim), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

# Start Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")  # Set window size
    app = CacheGUI(root)
    root.mainloop()
