import matplotlib
import customtkinter as ctk



class App:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.root = root

        self.root.title = "My awesome app"
        self.root.size = "400x400"

        self.frame_1 = ctk.CTkFrame(master=self.root)
        self.frame_1.pack(pady=20, padx=60, fill="both", expand=True)

        self.label_1 = ctk.CTkLabel(master=self.frame_1, justify=ctk.LEFT, text="panel 1 !!")
        self.label_1.pack(pady=10, padx=10)

        self.progressbar_1 = ctk.CTkProgressBar(master=self.frame_1)
        self.progressbar_1.pack(pady=10, padx=10)

        self.button_1 = ctk.CTkButton(master=self.frame_1, command=self.button_callback, text="click me")
        self.button_1.pack(pady=10, padx=10)

        self.slider_1 = ctk.CTkSlider(master=self.frame_1, command=self.slider_callback, from_=0, to=1)
        self.slider_1.pack(pady=10, padx=10)
        self.slider_1.set(0.5)

        self.entry_1 = ctk.CTkEntry(master=self.frame_1, placeholder_text="whats up?")
        self.entry_1.pack(pady=10, padx=10)

        self.optionmenu_1 = ctk.CTkOptionMenu(self.frame_1,
                                                   values=["Option 1", "Option 2"],
                                                   command=self.options_callback)
        self.optionmenu_1.pack(pady=10, padx=10)
        self.optionmenu_1.set("Options")

        self.checkbox_1 = ctk.CTkCheckBox(master=self.frame_1, command=self.checkbox_callback, text="check me")
        self.checkbox_1.pack(pady=10, padx=10)

        self.radiobutton_var = ctk.IntVar(value=0)
        self.radiobutton_1 = ctk.CTkRadioButton(master=self.frame_1, text="option 1",
                                                variable=self.radiobutton_var, value=1, command=self.radio_callback)
        self.radiobutton_1.pack(pady=10, padx=10)
        self.radiobutton_2 = ctk.CTkRadioButton(master=self.frame_1, text="option 2",
                                                variable=self.radiobutton_var, value=2, command=self.radio_callback)
        self.radiobutton_2.pack(pady=10, padx=10)

        self.switch_1 = ctk.CTkSwitch(master=self.frame_1, command=self.switch_callback, text="yes?")
        self.switch_1.pack(pady=10, padx=10)

        self.text_1 = ctk.CTkTextbox(master=self.frame_1, width=200, height=70)
        self.text_1.pack(pady=10, padx=10)
        self.text_1.insert("0.0", "Hello world\n\n\n\n")

        self.segmented_button_1 = ctk.CTkSegmentedButton(master=self.frame_1, values=["Value 1", "Value 2"],
                                                         command=self.segmented_button_callback)
        self.segmented_button_1.pack(pady=10, padx=10)



    def button_callback(self):
        print("Button clicked")
        print("Slider: ", self.slider_1.get())
        print("Entry: ", self.entry_1.get())

    def slider_callback(self, value):
        self.progressbar_1.set(value)

    def options_callback(self, value):
        print("Option menu: ", self.optionmenu_1.get())

    def radio_callback(self):
        print("Radio: ", self.radiobutton_var.get())

    def switch_callback(self):
        print("Switch: ", self.switch_1.get())

    def checkbox_callback(self):
        print("Checkbox: ", self.checkbox_1.get())

    def segmented_button_callback(self, value):
        print("Segmented button: ", self.segmented_button_1.get())
        print(value)

if __name__ == "__main__":
    root = ctk.CTk()
    App(root)
    root.mainloop()



