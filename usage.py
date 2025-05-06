import psutil
import time
import threading
import tkinter as tk
from PIL import Image, ImageDraw
import pystray
from pystray import Icon, MenuItem, Menu

# Function to fetch GPU usage info
def get_gpu_usage():
    try:
        # Try to use GPUInfo if available
        from gpuinfo import GPUInfo
        gpus = GPUInfo.get_info()
        if gpus and len(gpus) > 0:
            # Get the usage of the first GPU
            return gpus[0].load * 100
    except:
        try:
            # Fallback to nvidia-smi for NVIDIA GPUs
            import subprocess
            result = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'])
            return float(result.decode('utf-8').strip())
        except:
            pass
    
    # If we can't get GPU info, return 0
    return 0

# Function to gather system resource data
def get_system_stats():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    
    # Get disk usage with better error handling
    disk_usage = 0
    try:
        # Get the system drive usage
        system_drive = psutil.disk_partitions()[0].mountpoint  # Usually C: on Windows or / on Unix
        disk_usage = psutil.disk_usage(system_drive).percent
    except:
        # If that fails, try other methods
        try:
            for part in psutil.disk_partitions():
                if 'fixed' in part.opts.lower() or part.fstype != '':
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_usage = usage.percent
                    break
        except:
            try:
                # Last resort: try C: drive on Windows
                disk_usage = psutil.disk_usage('C:\\').percent
            except:
                disk_usage = 0  # Give up
    
    gpu_usage = get_gpu_usage()

    return cpu_usage, ram_usage, disk_usage, gpu_usage

# GUI to display the system stats
class SystemStatsDisplay(tk.Tk):
    def __init__(self, position="top-left"):
        super().__init__()
        self.position = position
        self.title("System Stats")
        self.geometry("200x120")  # Made slightly taller for GPU info
        self.overrideredirect(True)  # Hide window title bar
        
        # Make window transparent instead of black
        self.attributes("-alpha", 0.85)  # Slightly transparent
        self.configure(bg="SystemButtonFace")  # Use system default background (transparent)
        self.attributes("-topmost", True)  # Keep window on top
        
        # Create a frame with a thin border
        self.frame = tk.Frame(self, bg="SystemButtonFace", bd=1, relief="solid")
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Purple text color as requested
        purple_color = "#aa1dc6"
        
        self.stats_label = tk.Label(self.frame, text="Loading stats...", 
                                   fg=purple_color, font=("Consolas", 10), 
                                   bg="SystemButtonFace", justify="left")
        self.stats_label.pack(padx=5, pady=5)
        
        # Make the window draggable
        self.stats_label.bind("<ButtonPress-1>", self.start_move)
        self.stats_label.bind("<ButtonRelease-1>", self.stop_move)
        self.stats_label.bind("<B1-Motion>", self.on_motion)
        
        self.update_stats()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def update_stats(self):
        # Get the current system stats
        cpu, ram, disk, gpu = get_system_stats()
        
        # Always show all metrics
        stats_text = f"CPU: {cpu:5.1f}%\nRAM: {ram:5.1f}%\nDisk: {disk:5.1f}%"
        if gpu > 0:
            stats_text += f"\nGPU: {gpu:5.1f}%"
        else:
            stats_text += f"\nGPU: N/A"
            
        self.stats_label.config(text=stats_text)

        # Update the window position on first run
        if not hasattr(self, 'positioned'):
            self.update_position()
            self.positioned = True

        # Call this function every second to update the stats
        self.after(1000, self.update_stats)

    def update_position(self):
        # Position window based on user selection
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 200
        window_height = 120
        
        if self.position == "top-left":
            self.geometry(f"+10+10")
        elif self.position == "top-right":
            self.geometry(f"+{screen_width - window_width - 10}+10")
        elif self.position == "bottom-left":
            self.geometry(f"+10+{screen_height - window_height - 10}")
        elif self.position == "bottom-right":
            self.geometry(f"+{screen_width - window_width - 10}+{screen_height - window_height - 10}")
        else:
            # Default to center if position not recognized
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.geometry(f"+{x}+{y}")

# Function to create the system tray icon
def create_tray_icon(app):
    def on_quit():
        app.destroy()
        icon.stop()
    
    def toggle_visibility():
        if app.winfo_viewable():
            app.withdraw()
        else:
            app.deiconify()
    
    def move_to(position):
        app.position = position
        app.update_position()
    
    # Create a better-looking icon
    icon_size = 64
    icon_image = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon_image)
    
    # Draw a simple CPU meter icon - now with purple accent matching text color
    border = 4
    draw.rectangle([border, border, icon_size-border, icon_size-border], outline="#aa1dc6", width=2)
    # Draw some bars to represent stats
    for i in range(4):
        bar_height = 6
        bar_width = icon_size - (border * 4)
        y_pos = 10 + (i * 12)
        # Draw background bar
        draw.rectangle([border*2, y_pos, border*2 + bar_width, y_pos + bar_height], 
                      fill=(230, 230, 230, 255))
        # Draw filled portion (random for icon) - in purple to match text
        fill_width = bar_width * (0.3 + (i * 0.2))
        draw.rectangle([border*2, y_pos, border*2 + fill_width, y_pos + bar_height], 
                      fill=(170, 29, 198, 255))  # #aa1dc6 in RGB

    # Create the menu
    menu = Menu(
        MenuItem("System Stats", toggle_visibility),
        Menu.SEPARATOR,
        MenuItem("Position", Menu(
            MenuItem("Top Left", lambda: move_to("top-left")),
            MenuItem("Top Right", lambda: move_to("top-right")),
            MenuItem("Bottom Left", lambda: move_to("bottom-left")),
            MenuItem("Bottom Right", lambda: move_to("bottom-right"))
        )),
        Menu.SEPARATOR,
        MenuItem("Exit", on_quit)
    )
    
    icon = Icon("system_stats", icon_image, "System Stats Monitor", menu=menu)
    
    # Run the icon in a separate thread
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()
    
    return icon

# Main function to start the application
if __name__ == "__main__":
    # Get position preference
    valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
    position = input(f"Enter position {valid_positions}: ").strip().lower()
    
    if position not in valid_positions:
        print(f"Invalid position. Using default: top-right")
        position = "top-right"
    
    # Create the app
    app = SystemStatsDisplay(position)
    
    # Create the system tray icon
    icon = create_tray_icon(app)
    
    # Start the app
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass