"""Application entry point."""

import tkinter as tk
from tkinter import ttk

from dcs_c130j_simbridge import SimBridgeApp


def main():
    root = tk.Tk()
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    SimBridgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
