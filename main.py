import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog as fd
import plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from functools import partial


PLOT_SIZE = plot.PLOT_SIZE
SIZE = (1350, 850)
FONT = "Helvetika"
FONT_SIZE_LABEL = 20
FONT_SIZE_WIDGET = 18
TEXT_SIZE = (20, 2)
WIDGET_SIZE = (140, 40)
LABEL_MAX_LEN = 12


class App:
    def __init__(self, root):
        ctk.set_default_color_theme("green")
        ctk.set_appearance_mode("dark")

        root.title("Roy's plotter")
        root.iconbitmap("icon.ico")
        screen_width = root.winfo_screenwidth()  # Width of the screen
        screen_height = root.winfo_screenheight()  # Height of the screen
        x = (screen_width / 2) - (SIZE[0] / 2)
        y = (screen_height / 2) - (SIZE[1] / 2)
        root.geometry('%dx%d+%d+%d' % (SIZE[0], SIZE[1], x, y))

        root.protocol("WM_DELETE_WINDOW", self.quit_attempt)
        root.bind_all('<Escape>', lambda event: self.quit_attempt())
        root.bind_all('<Left>', lambda event: self.callback_previous())
        root.bind_all('<Right>', lambda event: self.callback_next())
        root.bind_all('<Up>', lambda event: self.callback_previous())
        root.bind_all('<Down>', lambda event: self.callback_next())
        root.bind_all("<Return>", lambda event: self.callback_generate())
        for i in range(1, 10):
            root.bind_all(f"{i}", partial(self.callback_numkeys, i))

        self.root = root

        self.output_dir = None
        self.canvas = None
        self.names = None
        self.cur_plot = self.create_empty_plot()
        self.plots = [self.cur_plot]
        self.gene = None
        self.empty_plot = self.create_empty_plot(gene_not_found=True)
        self.plot_index = 0
        self.messages = ['  -  ' * 11]

        self.frame_controls = ctk.CTkFrame(master=self.root)
        self.frame_plot = ctk.CTkFrame(master=self.root)
        self.frame_extra = ctk.CTkFrame(master=self.root)

        self.label_organism = ctk.CTkLabel(self.frame_controls, text="Organism: ",
                                           width=TEXT_SIZE[0], height=TEXT_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_LABEL))
        self.optionmenu_organism = ctk.CTkOptionMenu(master=self.frame_controls, values=plot.ORGANISMS,
                                                     width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.label_organ = ctk.CTkLabel(self.frame_controls, text="Tissue: ",
                                        width=TEXT_SIZE[0], height=TEXT_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_LABEL))
        self.optionmenu_organ = ctk.CTkOptionMenu(self.frame_controls, values=plot.TISSUES,
                                                  width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.label_gene = ctk.CTkLabel(self.frame_controls, text="Gene: ",
                                       width=TEXT_SIZE[0], height=TEXT_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_LABEL))
        self.entry = ctk.CTkEntry(master=self.frame_controls, placeholder_text="Gene",
                                  width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.button_generate = ctk.CTkButton(master=self.frame_controls, command=self.callback_generate, text="Generate",
                                             width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))

        self.button_next = ctk.CTkButton(master=self.frame_plot, command=self.callback_next, text="Next",
                                         width=220, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.button_previous = ctk.CTkButton(master=self.frame_plot, command=self.callback_previous, text="Previous",
                                             width=220, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.optionmenu_plot = ctk.CTkOptionMenu(self.frame_plot, values=["plot"], state="disabled", command=self.callback_options_plots,
                                                 width=240, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET), dynamic_resizing=False)
        self.switch_theme = ctk.CTkSwitch(master=self.frame_extra, command=self.callback_switch_theme, variable=ctk.StringVar(value="dark"), onvalue="dark", offvalue="",
                                          text="Dark theme", width=280, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.button_save = ctk.CTkButton(master=self.frame_plot, command=self.callback_save, text="Save", state="disabled",
                                         width=520, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.switch_save = ctk.CTkSwitch(master=self.frame_plot, command=self.callback_switch_save, text="Remember output folder",
                                         width=280, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))

        self.frame_controls.grid(column=0, row=1, rowspan=7, columnspan=2, padx=20, pady=20)
        self.frame_plot.grid(column=3, row=1, rowspan=7, columnspan=4, padx=20, pady=20)
        self.frame_extra.grid(column=0, row=7, columnspan=2, padx=20, pady=20)
        self.label_organism.grid(column=0, row=1, padx=20, pady=20)
        self.optionmenu_organism.grid(column=1, row=1, padx=20, pady=20)
        self.label_organ.grid(column=0, row=2, padx=20, pady=20)
        self.optionmenu_organ.grid(column=1, row=2, padx=20, pady=20)
        self.label_gene.grid(column=0, row=3, padx=20, pady=20)
        self.entry.grid(column=1, row=3, padx=20, pady=20)
        self.button_generate.grid(column=1, row=4, padx=20, pady=20)
        self.button_previous.grid(column=1, row=1, padx=20, pady=20)
        self.button_next.grid(column=2, row=1, padx=20, pady=20)
        self.optionmenu_plot.grid(column=3, row=1, padx=20, pady=20)
        self.switch_theme.grid(column=0, row=7, rowspan=2, padx=20, pady=20)
        self.button_save.grid(column=1, row=7, columnspan=2, padx=5, pady=20)
        self.switch_save.grid(column=3, row=7, padx=20, pady=20)

        self.datasets = plot.import_datasets()
        self.draw_plot()

    def callback_switch_theme(self):
        opt = 'dark' if self.switch_theme.get() else 'light'
        ctk.set_appearance_mode(opt)

    @staticmethod
    def create_empty_plot(gene_not_found=False):
        fig, ax = plt.subplots(figsize=PLOT_SIZE)
        text = "Gene not found" if gene_not_found else "Welcome to Roy's plotter"
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=26, color='red')
        ax.axis('off')
        ax.patch.set_alpha(0)
        return fig

    def create_plots(self,):
        self.plots, self.names = plot.make_plots(self.optionmenu_organism.get(), self.optionmenu_organ.get(), self.gene, self.datasets)
        print('options: ', self.optionmenu_organism.get(), self.optionmenu_organ.get(), self.gene)
        print("generated ", len(self.plots), ' plots')
        if not self.plots:
            self.button_save.configure(state="disabled")
            self.names = ["plot"]
            self.optionmenu_plot.configure(state="disabled", values=self.names)
            self.plots = [self.empty_plot]
            self.gene = None
        else:
            self.button_save.configure(state="normal")
            self.optionmenu_plot.configure(state="normal", values=self.names)
        self.plot_index = 0
        self.cur_plot = self.plots[self.plot_index]
        self.optionmenu_plot.set(self.names[self.plot_index])
        self.draw_plot()

    def draw_plot(self):
        self.canvas = FigureCanvasTkAgg(self.cur_plot, master=self.frame_plot)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=1, row=2, columnspan=3, rowspan=5, padx=20, pady=20)
        if self.plot_index == 0:
            self.button_previous.configure(state="disabled")
        else:
            self.button_previous.configure(state="normal")
        if self.plot_index == len(self.plots) - 1:
            self.button_next.configure(state="disabled")
        else:
            self.button_next.configure(state="normal")

    def callback_generate(self):
        self.gene = self.entry.get().upper().strip()
        if not self.gene:
            return
        self.create_plots()

    def callback_options_plots(self, value):
        self.plot_index = self.names.index(value)
        self.cur_plot = self.plots[self.plot_index]
        self.draw_plot()

    def callback_numkeys(self, key, e):
        if (key < 1) or (key > len(self.plots)):
            return
        self.plot_index = key - 1
        self.cur_plot = self.plots[self.plot_index]
        self.optionmenu_plot.set(self.names[self.plot_index])
        self.draw_plot()

    def callback_next(self):
        if self.plot_index >= len(self.plots) - 1:
            return
        self.plot_index += 1
        self.cur_plot = self.plots[self.plot_index]
        self.optionmenu_plot.set(self.names[self.plot_index])
        self.draw_plot()

    def callback_previous(self):
        if self.plot_index <= 0:
            return
        self.plot_index -= 1
        self.cur_plot = self.plots[self.plot_index]
        self.optionmenu_plot.set(self.names[self.plot_index])
        self.draw_plot()

    def callback_save(self):
        if self.cur_plot is None or self.gene is None:
            return
        directory = fd.askdirectory() if self.output_dir is None else self.output_dir
        if not directory:
            return
        if self.switch_save.get() == 1:
            self.output_dir = directory
        self.save_cur_plot(directory)

    def save_cur_plot(self, directory):
        """saves the current plot"""
        name = f'{self.optionmenu_organism.get()}_{self.optionmenu_organ.get()}_{self.gene}_{self.plot_index+1}'
        filename = f'{directory}/{name}.png'
        self.cur_plot.savefig(filename)
        print(f"saved: {filename}")

    def callback_switch_save(self):
        if self.switch_save.get() == 0:
            self.output_dir = None

    def quit_attempt(self):
        if messagebox.askokcancel("Quit", "Quit?"):
            self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    App(root)
    root.mainloop()
