import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

class WaterfallGUI:
    def __init__(self, root, x, **callbacks):
        self.root = root
        self.UPDATE = True
        self.update_counter = 1
        self.WATERFALL_LENGTH = 100
        self.Y_AXIS = np.arange(self.WATERFALL_LENGTH)
        self.labs_set = True

        self.matrix_cmap = LinearSegmentedColormap.from_list("",
                                                             ["#0D0208", "#003B00", "#008F11", "#00FF41"])
        self.CMAPS = [
            'CMRmap', 'Spectral', 'hot', 'jet',
            'plasma', 'viridis', 'winter_r', "ent3r_the_matrix"]

        self.CMAP = 'viridis'

        self.sample_macs(x)
        self.create_waterfall_hud(x, **callbacks)

    def sample_macs(self, x):
        self.MACIDS = x.MACID.unique()
        self.waterfall_container = np.zeros((self.WATERFALL_LENGTH, len(self.MACIDS)))
        self.waterfall_container.fill(-100)
        self.waterfall_container = pd.DataFrame(self.waterfall_container)
        self.waterfall_container.columns = self.MACIDS
        self.labels = [i[0:5] for i in self.MACIDS]

    def create_waterfall_hud(self, x, **callbacks):
        # Put the plot in
        self.create_waterfall(x, new=True)



        # Dropdown Selector
        self.selected_option = ctk.StringVar(value=self.CMAP)

        self.dropdown = ctk.CTkOptionMenu(
            master=self.root,
            values=self.CMAPS,
            variable=self.selected_option,
            command=self.select_CMAP)

        self.dropdown.place(relx=0.25, rely=0.01)

        # View Selector
        self.selected_view = ctk.StringVar(value='waterfall')

        self.dropdown = ctk.CTkOptionMenu(
            master=self.root,
            values=['antenna', 'signal', 'waterfall'],
            variable=self.selected_view,
            command=callbacks['toggle_view'])
        self.dropdown.place(relx=0.01, rely=0.01)

    def select_CMAP(self, selection):
        self.CMAP = selection

    def update(self, x):
        if self.update_counter < 3:
            self.sample_macs(x)

        else:
            self.create_waterfall(x, new=False)

        self.update_counter += 1

    def create_waterfall(self, x, new=True):
        if new:
            self.fig, self.ax = plt.subplots()
            self.fig.set_size_inches(11.5, 8.5)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
            self.ax.get_yaxis().set_visible(False)
            self.fig.subplots_adjust(left=0,right=1,bottom=0.1,top=1)
            self.ax.margins(x=0, y=0., tight=True)
            self.fig.set_facecolor("#3B3B3B")
            self.ax.set_xticklabels(self.labels, rotation=90, fontsize=12, color='white')

        now = x.Time.max()

        # Subset the data
        data = x[x.Time >= now - 0.3] # 0.3 because it takes about 0.25 seconds on my device to plot the graph

        if self.MACIDS.shape[0] >= 1:
            data = data[data.MACID.isin(self.MACIDS)]
            self.ax.set_xticklabels(self.labels, rotation=90, fontsize=12, color='white')


        # Collapse the data to MACID and add it in to the plot df
        grouped_df = data[["MACID", "RSSI"]].groupby(["MACID"])
        grouped_df = grouped_df.mean().T

        # Add it in
        self.waterfall_container = pd.concat([self.waterfall_container, grouped_df], ignore_index=True)

        self.waterfall_container.fillna(-100, inplace=True)
        self.waterfall_container = self.waterfall_container.iloc[1:, :]

        if len(self.MACIDS) > 0:

            if self.CMAP != 'ent3r_the_matrix':

                self.ax.pcolormesh(self.MACIDS,
                                   self.Y_AXIS,
                                   self.waterfall_container.to_numpy(dtype='float'),
                                   vmin=-90, vmax=-20, cmap=self.CMAP)

            else:
                self.ax.pcolormesh(self.MACIDS,
                                   self.Y_AXIS,
                                   self.waterfall_container.to_numpy(dtype='float'),
                                   vmin=-90, vmax=-20, cmap=self.matrix_cmap)

        self.canvas.draw()

        if new:
            self.canvas.get_tk_widget().place(relx=0.02, rely=0.02)
        else:
            self.ax.clear()


    def destroy(self):
        plt.close('all')

        for widget in self.root.winfo_children():
            widget.destroy()