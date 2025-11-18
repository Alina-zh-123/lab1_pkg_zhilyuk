import tkinter as tk
from tkinter import ttk, colorchooser

class ColorConverterApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Конвертер цветовых моделей")
        self.geometry("1060x400")
        self.configure(bg="#f8fafc")
        self.resizable(True, True)

        self._is_updating = False
        self._last_source_model = None

        style = ttk.Style(self)
        style.configure("TLabel", background="#f1f5f9", font=("Inter", 10))
        style.configure("TFrame", background="#1a344e")
        style.configure("Main.TFrame", background="#0b2641")
        style.configure("Header.TLabel", font=("Inter", 16, "bold"), background="#f8fafc")
        style.configure("Subheader.TLabel", background="#f8fafc", foreground="#64748b")
        style.configure("Model.TLabel", background="#1a344e", foreground="#e2e8f0", font=("Inter", 12, "bold"))
        style.configure("Warning.TLabel", background="#0b2641", foreground="#ff6b6b", font=("Inter", 10, "bold"))

        self._create_widgets()
        self.update_all("hex", "#4287f5")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20, style="Main.TFrame")
        main_frame.pack(expand=True, fill="both")

        top_panel = ttk.Frame(main_frame, style="Main.TFrame")
        top_panel.pack(fill="x", pady=(0, 10))

        self.color_preview = tk.Label(top_panel, bg="#4287f5", width=40, height=6,
                                    relief="groove", borderwidth=2)
        self.color_preview.pack(side="left", padx=(0, 10), fill="x", expand=True)

        ttk.Button(top_panel, text="Выберите цвет",
                command=self._open_color_picker).pack(side="left")

        self.gamut_warning = ttk.Label(main_frame,
                                    text="Внимание: Цвет был скорректирован!",
                                    style="Warning.TLabel", padding=10, wraplength=700)
        self.gamut_warning.pack(fill="x", pady=(0, 10))
        self.gamut_warning.pack_forget()

        self.range_warning = ttk.Label(main_frame,
                                     text="",
                                     style="Warning.TLabel", padding=10, wraplength=700)
        self.range_warning.pack(fill="x", pady=(0, 10))
        self.range_warning.pack_forget()

        models_panel = ttk.Frame(main_frame, style="Main.TFrame")
        models_panel.pack(fill="both", expand=True)

        models_panel.columnconfigure((0, 1, 2), weight=1)

        self.vars = {
            "rgb": {"r": tk.DoubleVar(), "g": tk.DoubleVar(), "b": tk.DoubleVar()},
            "cmyk": {"c": tk.DoubleVar(), "m": tk.DoubleVar(), "y": tk.DoubleVar(), "k": tk.DoubleVar()},
            "xyz": {"x": tk.DoubleVar(), "y": tk.DoubleVar(), "z": tk.DoubleVar()}
        }

        self.ranges = {
            "rgb": {"r": (0, 255), "g": (0, 255), "b": (0, 255)},
            "cmyk": {"c": (0, 100), "m": (0, 100), "y": (0, 100), "k": (0, 100)},
            "xyz": {"x": (0, 95), "y": (0, 100), "z": (0, 110)}
        }

        self._create_model_frame(models_panel, "RGB", "rgb",
            [("R", 0, 255), ("G", 0, 255), ("B", 0, 255)]
        ).grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self._create_model_frame(models_panel, "CMYK", "cmyk",
            [("C", 0, 100), ("M", 0, 100), ("Y", 0, 100), ("K", 0, 100)]
        ).grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        self._create_model_frame(models_panel, "XYZ", "xyz",
            [("X", 0, 95), ("Y", 0, 100), ("Z", 0, 110)]
        ).grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

    def _create_model_frame(self, parent, title, model_name, components):
        frame = ttk.Frame(parent, padding=15, relief="groove", borderwidth=1)
        ttk.Label(frame, text=title, style="Model.TLabel").pack(anchor="w")

        for comp, min_val, max_val in components:
            row = ttk.Frame(frame)
            row.pack(fill="x", expand=True, pady=5)
            ttk.Label(row, text=comp, width=4).pack(side="left")
            var = self.vars[model_name][comp.lower()]
            slider = ttk.Scale(row, from_=min_val, to=max_val, variable=var, orient="horizontal",
                               command=lambda e, m=model_name: self._on_slider_change(m))
            slider.pack(side="left", fill="x", expand=True, padx=10)
            entry = ttk.Entry(row, textvariable=var, width=8)
            entry.pack(side="left")
            entry.bind("<Return>", lambda e, m=model_name, c=comp.lower(): self._validate_and_update(m, c))
        return frame

    def _on_slider_change(self, model_name):
        self.range_warning.pack_forget()
        self.update_all(model_name)

    def _validate_and_update(self, model_name, component):
        try:
            value = self.vars[model_name][component].get()
            min_val, max_val = self.ranges[model_name][component]
            
            if min_val <= value <= max_val:
                self.range_warning.pack_forget()
                self.update_all(model_name)
            else:
                warning_text = f"{model_name.upper()} {component.upper()} должен быть в диапазоне ({min_val}, {max_val})!"
                self.range_warning.config(text=warning_text)
                self.range_warning.pack(pady=5, fill="x")
                
        except (ValueError, tk.TclError):
            warning_text = f"Введите числовое значение для {model_name.upper()} {component.upper()}!"
            self.range_warning.config(text=warning_text)
            self.range_warning.pack(pady=5, fill="x")

    def _open_color_picker(self):
        _, hex_color = colorchooser.askcolor(title="Выберите цвет")
        if hex_color:
            self.range_warning.pack_forget()  
            self.update_all("hex", hex_color)

    @staticmethod
    def _rgb_to_cmyk(r, g, b):
        if r == 0 and g == 0 and b == 0: 
            return 0, 0, 0, 100
        r_, g_, b_ = r / 255, g / 255, b / 255
        k = 1 - max(r_, g_, b_)
        if k == 1: 
            return 0, 0, 0, 100
        c = (1 - r_ - k) / (1 - k)
        m = (1 - g_ - k) / (1 - k)
        y = (1 - b_ - k) / (1 - k)
        return c * 100, m * 100, y * 100, k * 100

    @staticmethod
    def _cmyk_to_rgb(c, m, y, k):
        c, m, y, k = c / 100, m / 100, y / 100, k / 100
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        return r, g, b

    @staticmethod
    def _rgb_to_xyz(r, g, b):
        r, g, b = r / 255, g / 255, b / 255

        def linearize(val):
            return ((val + 0.055) / 1.055) ** 2.4 if val > 0.04045 else val / 12.92

        r_lin, g_lin, b_lin = map(linearize, [r, g, b])
        x = r_lin * 0.4124564 + g_lin * 0.3575761 + b_lin * 0.1804375
        y = r_lin * 0.2126729 + g_lin * 0.7151522 + b_lin * 0.0721750
        z = r_lin * 0.0193339 + g_lin * 0.1191920 + b_lin * 0.9503041
        return x * 100, y * 100, z * 100

    def _xyz_to_rgb(self, x, y, z):
        x, y, z = x / 100, y / 100, z / 100
        r_lin = x * 3.2404542 - y * 1.5371385 - z * 0.4985314
        g_lin = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
        b_lin = x * 0.0556434 - y * 0.2040259 + z * 1.0572252

        def correct_gamma(val):
            return (1.055 * val ** (1 / 2.4) - 0.055) if val > 0.0031308 else 12.92 * val

        r, g, b = map(correct_gamma, [r_lin, g_lin, b_lin])
        is_out_of_gamut = False

        def clamp(val):
            nonlocal is_out_of_gamut
            if val < 0: 
                is_out_of_gamut = True
                return 0
            if val > 1: 
                is_out_of_gamut = True
                return 1
            return val
        
        r, g, b = map(clamp, [r, g, b])
        if is_out_of_gamut:
            self.gamut_warning.pack(pady=5, fill="x")
        else:
            self.gamut_warning.pack_forget()
        return r * 255, g * 255, b * 255

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def update_all(self, source_model, source_value=None):
        if self._is_updating: 
            return
        
        self._is_updating = True
        self._last_source_model = source_model
        
        rgb, cmyk, xyz = (0, 0, 0), (0, 0, 0, 100), (0, 0, 0)

        try:
            if source_model == 'hex':
                rgb = self._hex_to_rgb(source_value)
                cmyk = self._rgb_to_cmyk(*rgb)
                xyz = self._rgb_to_xyz(*rgb)
            elif source_model == 'rgb':
                rgb = (self.vars['rgb']['r'].get(), self.vars['rgb']['g'].get(), self.vars['rgb']['b'].get())
                cmyk = self._rgb_to_cmyk(*rgb)
                xyz = self._rgb_to_xyz(*rgb)
            elif source_model == 'cmyk':
                cmyk_vals = (
                    self.vars['cmyk']['c'].get(), 
                    self.vars['cmyk']['m'].get(), 
                    self.vars['cmyk']['y'].get(),
                    self.vars['cmyk']['k'].get()
                )
                rgb = self._cmyk_to_rgb(*cmyk_vals)
                cmyk = cmyk_vals
                xyz = self._rgb_to_xyz(*rgb)
            elif source_model == 'xyz':
                xyz = (self.vars['xyz']['x'].get(), self.vars['xyz']['y'].get(), self.vars['xyz']['z'].get())
                rgb = self._xyz_to_rgb(*xyz)
                cmyk = self._rgb_to_cmyk(*rgb)

            if source_model != 'cmyk':
                self.vars['rgb']['r'].set(round(rgb[0]))
                self.vars['rgb']['g'].set(round(rgb[1]))
                self.vars['rgb']['b'].set(round(rgb[2]))
                self.vars['cmyk']['c'].set(round(cmyk[0], 1))
                self.vars['cmyk']['m'].set(round(cmyk[1], 1))
                self.vars['cmyk']['y'].set(round(cmyk[2], 1))
                self.vars['cmyk']['k'].set(round(cmyk[3], 1))
                self.vars['xyz']['x'].set(round(xyz[0], 2))
                self.vars['xyz']['y'].set(round(xyz[1], 2))
                self.vars['xyz']['z'].set(round(xyz[2], 2))
            else:
                self.vars['rgb']['r'].set(round(rgb[0]))
                self.vars['rgb']['g'].set(round(rgb[1]))
                self.vars['rgb']['b'].set(round(rgb[2]))
                self.vars['xyz']['x'].set(round(xyz[0], 2))
                self.vars['xyz']['y'].set(round(xyz[1], 2))
                self.vars['xyz']['z'].set(round(xyz[2], 2))

            hex_color = f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
            self.color_preview.config(bg=hex_color)

            if source_model != 'xyz':
                self.gamut_warning.pack_forget()
                
        except Exception as e:
            print(f"Error in update_all: {e}")
        finally:
            self._is_updating = False

if __name__ == "__main__":
    app = ColorConverterApp()
    app.mainloop()