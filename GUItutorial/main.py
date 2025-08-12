import customtkinter as ctk
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# 

class CSVplotter:

    def __init__(self, root):
        self.root= root
        root.title("CSV Plotter")

        self.plot_types = ["Line", "Bar", "Scatter"]
        self.plot_types_var = ctk.StringVar(value=self.plot_types[0])
        plot_menu = ctk.CTkOptionMenu(self.root, variable=self.plot_types_var, values=self.plot_types, command=self.update_plot)
        plot_menu.pack(pady=10, padx=10)

        load_button = ctk.CTkButton(self.root, text="Load CSV", command=self.load_csv, hover = True)
        load_button.pack(pady=10, padx=10)

        self.checkbox_var= ctk.StringVar(value = "off")
        checkbox = ctk.CTkCheckBox(self.root, text="Live Plot", variable=self.checkbox_var, command=self.update_plot, onvalue="on", offvalue="off")
        checkbox.pack(pady =10, padx = 10)

        self.fig, self.ax= plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(padx=10, pady=10)

        self.df = None # DataFrame to hold the CSV data and there's no data loaded initially

    # load CSV file using pandas
    def load_csv(self):
        file_path = filedialog.askopenfilename()
        # print(f"{file_path}")
        if '.asc' in file_path:
            # print('if statement .asc file works')
            self.ascFile = True
            with open(file_path, 'r') as f:
                # print('opening.asc file works')
                for i, line in enumerate(f):
                    print('for loop works')
                    print(line)
                    if "Frequency" in line:
                        self.start_line = i + 1  # +1 to start from the line after "Frequency"
                        print(f"Start line: {self.start_line}")
                        break
            self.df = pd.read_csv(file_path, skiprows=self.start_line, sep='\t')
            self.update_plot()
        else:
            ascFile = False
            self.df = pd.read_csv(file_path)
            self.update_plot()

    # update the plot based on selected plot type
    def update_plot(self, event=None):
        if self.df is not None:
            live_plot = self.checkbox_var.get()# check if live plot is enabled
            print(f"Live Plot: {live_plot}")
            if live_plot == "on":
                plot_type = self.plot_types_var.get() # get value of string variable for plot type
                if self.ascFile == False:
                    x = self.df.columns[0]  # Use the first column as x-axis
                    y = self.df.columns[1]  # Use the second column as y-axis
                else:
                    x = self.df.columns[0]  # Use the first column as x-axis
                    y = self.df.columns[1:]  # Use the second column as y-axis

##### INSERT CODE TO PLOT AMP OR PHASE DATA FOR EACH WAVELENGTH ##############
                self.ax.clear()
                if plot_type == "Line":
                    self.ax.plot(self.df[x], self.df[y], label=f'{y} vs {x}')
                elif plot_type == "Bar":
                    self.ax.bar(self.df[x], self.df[y], label=f'{y} vs {x}')
                elif plot_type == "Scatter":
                    self.ax.scatter(self.df[x], self.df[y], label=f'{y} vs {x}')

                self.ax.set_xlabel(x)
                self.ax.set_ylabel(y)
                self.ax.legend()
                self.canvas.draw() #draws the updated plot on the canvas
            else:
                self.ax.clear()
                self.ax.text(0.5, 0.5, "Live Plot is Off", fontsize=20, ha='center')
                self.canvas.draw()

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x600")
    root.resizable(False, False)  # Make the window resizable or not (True/False)
    app = CSVplotter(root)
    root.mainloop()

### creates a modern GUI login system using ctk
# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("green")

# root = ctk.CTk()
# root.geometry("500x350")

# def login():
#     print("Login button clicked")

# frame = ctk.CTkFrame(master=root)
# frame.pack(pady=20, padx=60, fill="both", expand=True) # this is the frame that will contain the widgets

# label = ctk.CTkLabel(master=frame, text="Login System", font=("Arial", 24))
# label.pack(pady=12, padx=10)

# entry1 = ctk.CTkEntry(master=frame, placeholder_text="Username")
# entry1.pack(pady=12, padx=10)

# # Create a password entry field
# entry2 = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
# entry2.pack(pady=12, padx=10)

# # Create a login button
# button = ctk.CTkButton(master=frame, text="Login", command=login)
# button.pack(pady=12, padx=10)

# # Create a remember me checkbox
# checkbox = ctk.CTkCheckBox(master=frame, text="Remember me")
# checkbox.pack(pady=12, padx=10)

# # Start the main loop
# root.mainloop()
