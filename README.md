# System Stats Monitor

A lightweight and visually appealing application to monitor your system's resource usage in real-time. View CPU, RAM, Disk, and GPU usage through a compact GUI window, which can be positioned anywhere on the screen. The app also features a system tray icon for easy accessibility.

## Features

- **Real-Time Monitoring**:
  - CPU Usage
  - RAM Usage
  - Disk Usage
  - GPU Usage (if available)
- **Customizable Window Position**:
  - Top-Left, Top-Right, Bottom-Left, or Bottom-Right of the screen.
- **System Tray Integration**:
  - Easily toggle the visibility of the stats window.
  - Quickly reposition the stats window from the tray menu.
  - Exit the application via the tray icon.
- **Draggable Interface**:
  - Move the stats window to any custom position by dragging.

## Installation

1. Clone the repository or download the source code:
   ```bash
   git clone https://github.com/yourusername/system-stats-monitor.git
   cd system-stats-monitor
2.pip install psutil pystray pillow
3. python usage.py
