import matplotlib
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import tkinter.font as fnt
import plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt


PLOT_SIZE = plot.PLOT_SIZE
SIZE = (1350, 850)
FONT = "Helvetika"
FONT_SIZE_LABEL = 20
FONT_SIZE_WIDGET = 18
TEXT_SIZE = (20, 2)
WIDGET_SIZE = (140, 40)

class App:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        root.title = "My awesome app"
        root.protocol("WM_DELETE_WINDOW", self.quit_attempt)
        screen_width = root.winfo_screenwidth()  # Width of the screen
        screen_height = root.winfo_screenheight()  # Height of the screen
        x = (screen_width / 2) - (SIZE[0] / 2)
        y = (screen_height / 2) - (SIZE[1] / 2)
        root.geometry('%dx%d+%d+%d' % (SIZE[0], SIZE[1], x, y))
        self.root = root


        self.output_dir = None
        self.cur_plot = self.create_empty_plot()
        self.plots = [self.cur_plot]
        self.gene = None
        self.empty_plot = self.create_empty_plot(gene_not_found=True)
        self.plot_index = 0



        self.frame_controls = ctk.CTkFrame(master=self.root, width=240, height=800)
        self.frame_plot = ctk.CTkFrame(master=self.root)
        self.frame_updates = ctk.CTkFrame(master=self.root)

        self.label_organism = ctk.CTkLabel(self.frame_controls, text="Organism: ",
                                           width=TEXT_SIZE[0], height=TEXT_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_LABEL))
        self.optionmenu_organism = ctk.CTkOptionMenu(master=self.frame_controls, command=self.callback_organism, values=["mouse", "human"],
                                                     width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.label_organ = ctk.CTkLabel(self.frame_controls, text="Tissue: ",
                                        width=TEXT_SIZE[0], height=TEXT_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_LABEL))
        self.optionmenu_organ = ctk.CTkOptionMenu(self.frame_controls, values=["all tissues", "pancreas", "intestine", "liver"], command=self.callback_organ,
                                                  width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.entry = ctk.CTkEntry(master=self.frame_controls, placeholder_text="Gene",
                                  width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.button_generate = ctk.CTkButton(master=self.frame_controls, command=self.callback_generate, text="Generate",
                                             width=WIDGET_SIZE[0], height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.label_updates_board = ctk.CTkLabel(self.frame_updates, text=f"{'  -  '*11}\ntest",
                                                width=TEXT_SIZE[0]*2, height=TEXT_SIZE[1]*2, font=ctk.CTkFont(family=FONT,
                                                size=FONT_SIZE_WIDGET), anchor="nw", compound="left", justify="left")


        self.button_next = ctk.CTkButton(master=self.frame_plot, command=self.callback_next, text="Next",
                                         width=220, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.button_previous = ctk.CTkButton(master=self.frame_plot, command=self.callback_previous, text="Previous",
                                             width=220, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.button_save = ctk.CTkButton(master=self.frame_plot, command=self.callback_save, text="Save",
                                         width=520, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))
        self.switch_save = ctk.CTkSwitch(master=self.frame_plot, command=self.callback_switch_save, text="Remember output folder",
                                         width=280, height=WIDGET_SIZE[1], font=ctk.CTkFont(family=FONT, size=FONT_SIZE_WIDGET))

        self.frame_controls.grid(column=0, row=1, rowspan=4, columnspan=2, padx=20, pady=20)
        self.frame_updates.grid(column=0, row=6, rowspan=2, columnspan=2, padx=20, pady=20)
        self.frame_plot.grid(column=3, row=1, rowspan=7, columnspan=4, padx=20, pady=20)
        self.label_organism.grid(column=0, row=1, padx=20, pady=20)
        self.optionmenu_organism.grid(column=1, row=1, padx=20, pady=20)
        self.label_organ.grid(column=0, row=2, padx=20, pady=20)
        self.optionmenu_organ.grid(column=1, row=2, padx=20, pady=20)
        self.entry.grid(column=1, row=3, padx=20, pady=20)
        self.button_generate.grid(column=1, row=4, padx=20, pady=20)
        self.label_updates_board.grid(column=0, row=5, rowspan=2, columnspan=2, padx=20, pady=20)
        self.button_previous.grid(column=1, row=1, padx=20, pady=20)
        self.button_next.grid(column=2, row=1, padx=20, pady=20)
        self.button_save.grid(column=1, row=7, columnspan=2, padx=5, pady=20)
        self.switch_save.grid(column=3, row=7, padx=20, pady=20)


        self.datasets = plot.import_datasets()
        self.draw_plot()

        # path = "img.png" #todo
        # self.image1 = ImageTk.PhotoImage(Image.open(path))
        # self.image = ctk.CTkImage(dark_image=Image.open(path), size=PLOT_SIZE)
        # self.plot_label = ctk.CTkLabel(self.frame_plot, image=self.image, text='')
        # self.plot_label.grid(column=1, row=2, columnspan=3, rowspan=5, padx=20, pady=20)

    @staticmethod
    def create_empty_plot(gene_not_found=False):
        fig, ax = plt.subplots(figsize=PLOT_SIZE)
        text = "Gene not found" if gene_not_found else "Welcome to Roy's plotter"
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=26, color='red')
        ax.axis('off')
        ax.patch.set_alpha(0)
        return fig
    def create_plots(self,):
        self.plots = plot.make_plots(self.optionmenu_organism.get(), self.optionmenu_organ.get(), self.gene, self.datasets)
        print(self.optionmenu_organism.get(), self.optionmenu_organ.get(), self.gene)
        print("generated: ", self.plots)
        if not self.plots:
            self.plots = [self.empty_plot]
        self.plot_index = 0
        self.cur_plot = self.plots[self.plot_index]
        self.draw_plot()
    def draw_plot(self):
        self.canvas = FigureCanvasTkAgg(self.cur_plot, master=self.frame_plot)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=1, row=2, columnspan=3, rowspan=5, padx=20, pady=20)
    def callback_organism(self, val):
        print("organism: ", val)
    def callback_type(self,val):
        print("type: ", val)
    def callback_organ(self,val):
        print("organ: ", val)
    def callback_generate(self):
        self.gene = self.entry.get().upper().strip()
        if not self.gene:
            return
        print("generate button, gene: ", self.gene)
        self.create_plots()
    def callback_next(self):
        print("next button")
        if self.plot_index >= len(self.plots) - 1:
            return
        self.plot_index += 1
        self.cur_plot = self.plots[self.plot_index]
        self.draw_plot()
    def callback_previous(self):
        print("previous button")
        if self.plot_index <= 0:
            return
        self.plot_index -= 1
        self.cur_plot = self.plots[self.plot_index]
        self.draw_plot()

    def callback_save(self):
        """saves the current plot"""
        if self.cur_plot is None:
            return
        directory = fd.askdirectory() if self.output_dir is None else self.output_dir
        if not directory:
            return
        if self.switch_save.get() == 1:
            self.output_dir = directory
        name = self.save_cur_plot(directory)
        self.update_label(f'[SAVED] {name}')

    def save_cur_plot(self, directory):
        name = f'{self.optionmenu_organism.get()}_{self.optionmenu_organ.get()}_{self.gene}_{self.plot_index+1}'
        filename = f'{directory}/{name}.png'
        self.cur_plot.savefig(filename)
        return name

    def callback_switch_save(self):
        if self.switch_save.get() == 0:
            self.output_dir = None
        print("save output:", self.switch_save.get())

    def quit_attempt(self):
        if True:
            self.root.destroy()
        # if messagebox.askokcancel("Quit", "Quit?"):
        #     self.root.destroy() # todo remove


    def update_label(self, update):
        print(update)




if __name__ == "__main__":
    root = ctk.CTk()
    App(root)
    root.mainloop()


