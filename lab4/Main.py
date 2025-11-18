import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

GRID_SIZE = 55       
DEFAULT_SCALE = 13    
MIN_SCALE = 10
MAX_SCALE = 50

AXIS_COLOR = "#222222"
GRID_COLOR = "#e0e0e0"
GRID_MAJOR_COLOR = "#c0c0c0"
POINT_COLOR = "#d62728"
HIGHLIGHT_COLOR = "#d62728"
LINE_COLOR = "#ff6b35"
RASTER_COLOR = "#000000" 
TEXT_FONT = ("Consolas", 9)
COORD_COLOR = "#2e86ab"  

def naive_line(x0, y0, x1, y1):
    points = []
    log = []
    
    if x0 == x1:
        step = 1 if y1 > y0 else -1
        for y in range(y0, y1 + step, step):
            points.append((x0, y))
            log.append(f"x={x0}, y={y} (вертикальная)")
    else:
        k = (y1 - y0) / (x1 - x0)
        b = y0 - k * x0
        log.append(f"Уравнение: y = {k:.3f}x + {b:.3f}")
        
        if abs(k) <= 1:
            step = 1 if x1 > x0 else -1
            for x in range(x0, x1 + step, step):
                y = k * x + b
                y_round = round(y)
                points.append((x, y_round))
                log.append(f"x={x}, y={y:.3f} -> {y_round}")
        else:
            step = 1 if y1 > y0 else -1
            for y in range(y0, y1 + step, step):
                x = (y - b) / k
                x_round = round(x)
                points.append((x_round, y))
                log.append(f"y={y}, x={x:.3f} -> {x_round}")
    
    return points, log

def dda_line(x0, y0, x1, y1):
    points = []
    log = []
    
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    
    if steps == 0:
        points.append((x0, y0))
        log.append("Точка (нулевая длина)")
        return points, log
    
    x_inc = dx / steps
    y_inc = dy / steps
    
    x = x0
    y = y0
    
    log.append(f"dx={dx}, dy={dy}, steps={steps}")
    log.append(f"x_inc={x_inc:.3f}, y_inc={y_inc:.3f}")
    
    for i in range(steps + 1):
        x_round = round(x)
        y_round = round(y)
        points.append((x_round, y_round))
        log.append(f"шаг {i}: x={x:.3f}, y={y:.3f} -> ({x_round},{y_round})")
        x += x_inc
        y += y_inc
    
    return points, log

def bresenham_line(x0, y0, x1, y1):
    points = []
    log = []
    
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    log.append(f"dx={dx}, dy={dy}, sx={sx}, sy={sy}")
    log.append(f"Начальная ошибка: {err}")
    
    x, y = x0, y0
    step = 0
    
    while True:
        points.append((x, y))
        log.append(f"шаг {step}: ({x},{y}), ошибка={err}")
        
        if x == x1 and y == y1:
            break
            
        e2 = 2 * err
        
        if e2 > -dy:
            err -= dy
            x += sx
            log.append(f"  движение по X -> x={x}, ошибка={err}")
            
        if e2 < dx:
            err += dx
            y += sy
            log.append(f"  движение по Y -> y={y}, ошибка={err}")
            
        step += 1
    
    return points, log

def bresenham_circle(xc, yc, r):
    points = []
    log = []
    
    x = 0
    y = int(abs(r))
    d = 3 - 2 * y
    
    log.append(f"Начальные: x={x}, y={y}, d={d}")
    
    step = 0
    
    while x <= y:
        octants = [
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ]
        
        for point in octants:
            points.append(point)
            
        log.append(f"шаг {step}: x={x}, y={y}, d={d}")
        log.append(f"  точки: {octants}")
        
        if d < 0:
            d = d + 4 * x + 6
            log.append(f"  d < 0: новое d = {d}")
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
            log.append(f"  d >= 0: новое d = {d}, y уменьшен до {y}")
            
        x += 1
        step += 1
    
    seen = set()
    unique_points = []
    for point in points:
        if point not in seen:
            unique_points.append(point)
            seen.add(point)
    
    return unique_points, log

def wu_line(x0, y0, x1, y1):
    points = []
    log = []
    
    x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
    
    dx = x1 - x0
    dy = y1 - y0
    steep = abs(dy) > abs(dx)
    
    log.append(f"dx={dx:.3f}, dy={dy:.3f}, steep={steep}")
    
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        dx, dy = dy, dx
        log.append(f"Обмен координат: ({x0:.3f}, {y0:.3f}) -> ({x1:.3f}, {y1:.3f})")
    
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
        dx, dy = -dx, -dy
        log.append(f"Обмен концов: ({x0:.3f}, {y0:.3f}) -> ({x1:.3f}, {y1:.3f})")
    
    gradient = dy / dx if dx != 0 else 0
    log.append(f"Градиент: {gradient:.3f}")
    
    def plot(x, y, intensity, is_steep):
        if is_steep:
            points.append((y, x, intensity))
        else:
            points.append((x, y, intensity))
    
    x_start = round(x0)
    y_start = round(y0)
    plot(x_start, y_start, 255, steep)
    log.append(f"Начальная точка: ({x_start}, {y_start}), интенсивность: 255")
    
    x_end = round(x1)
    y_end = round(y1)
    plot(x_end, y_end, 255, steep)
    log.append(f"Конечная точка: ({x_end}, {y_end}), интенсивность: 255")
    
    intery = y0 + gradient * (round(x0) + 1 - x0)
    log.append(f"Начальное intery: {intery:.3f}")
    
    x = round(x0) + 1
    step_count = 0
    
    while x <= round(x1) - 1:
        y_f = intery
        y = math.floor(y_f)
        frac = y_f - y
        
        intensity_upper = round((1 - frac) * 255)
        intensity_lower = round(frac * 255)
        
        plot(x, y, intensity_upper, steep)
        plot(x, y + 1, intensity_lower, steep)
        
        log.append(f"шаг {step_count}: x={x}, y_floor={y}, frac={frac:.3f}")
        log.append(f"  верхняя точка: ({x}, {y}), интенсивность: {intensity_upper}")
        log.append(f"  нижняя точка: ({x}, {y+1}), интенсивность: {intensity_lower}")
        
        intery += gradient
        x += 1
        step_count += 1
    
    log.append(f"Всего точек: {len(points)}")
    return points, log

def to_canvas_coords(x, y, scale, center_x, center_y):
    canvas_x = center_x + x * scale
    canvas_y = center_y - y * scale
    return canvas_x, canvas_y

def clamp_int(value, min_val, max_val):
    try:
        result = int(round(float(value)))
        return max(min_val, min(max_val, result))
    except (ValueError, TypeError):
        return min_val

class RasterApp:
    def __init__(self, root):
        self.root = root
        root.title("Растровые алгоритмы")
        
        self.scale = DEFAULT_SCALE
        self.grid_size = GRID_SIZE
        self.canvas_size = 2 * self.grid_size * self.scale
        
        self.canvas = tk.Canvas(
            root, 
            width=700, 
            height=700,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.grid(row=0, column=0, rowspan=20, padx=10, pady=10)
        
        self.center_x = self.canvas_size // 2
        self.center_y = self.canvas_size // 2
        
        self.create_control_panel()
        
        self.last_points = []
        self.last_log = []
        self.draw_grid()
        
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def create_control_panel(self):
        frm = ttk.Frame(self.root)
        frm.grid(row=0, column=1, sticky="nw", padx=10, pady=10)
        
        ttk.Label(frm, font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.alg_var = tk.StringVar(value="naive")
        
        algorithms = [
            ("Пошаговый алгоритм", "naive"),
            ("Алгоритм ЦДА", "dda"), 
            ("Алгоритм Брезенхема (линия)", "bres_line"),
            ("Алгоритм Брезенхема (окружность)", "bres_circle"),
            ("Алгоритм Ву (линия)", "wu_line")
        ]
        
        for i, (label, value) in enumerate(algorithms):
            ttk.Radiobutton(
                frm, text=label, variable=self.alg_var, value=value,
                command=self.on_algorithm_change
            ).grid(row=1+i, column=0, sticky="w", pady=2)
        
        ttk.Label(frm, text="Координаты:", font=("Arial", 11, "bold")).grid(row=6, column=0, sticky="w", pady=(15, 5))
        
        coord_frame = ttk.Frame(frm)
        coord_frame.grid(row=7, column=0, sticky="w", pady=5)
        
        ttk.Label(coord_frame, text="Начальная точка:").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(coord_frame, text="x0:").grid(row=1, column=0, padx=(0, 2))
        self.x0_entry = ttk.Entry(coord_frame, width=6)
        self.x0_entry.grid(row=1, column=1, padx=(0, 10))
        
        ttk.Label(coord_frame, text="y0:").grid(row=1, column=2, padx=(0, 2))
        self.y0_entry = ttk.Entry(coord_frame, width=6)
        self.y0_entry.grid(row=1, column=3, padx=(0, 10))
        
        ttk.Label(coord_frame, text="Конечная точка / Радиус:").grid(row=2, column=0, columnspan=4, sticky="w", pady=(5, 0))
        ttk.Label(coord_frame, text="x1/r:").grid(row=3, column=0, padx=(0, 2))
        self.x1_entry = ttk.Entry(coord_frame, width=6)
        self.x1_entry.grid(row=3, column=1, padx=(0, 10))
        
        ttk.Label(coord_frame, text="y1:").grid(row=3, column=2, padx=(0, 2))
        self.y1_entry = ttk.Entry(coord_frame, width=6)
        self.y1_entry.grid(row=3, column=3, padx=(0, 10))
        
        self.x0_entry.insert(0, "2")
        self.y0_entry.insert(0, "3")
        self.x1_entry.insert(0, "8")
        self.y1_entry.insert(0, "6")
        
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=8, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Построить", command=self.on_draw).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.on_clear).grid(row=0, column=1, padx=5)
        
        ttk.Label(frm, text="Масштаб:", font=("Arial", 11, "bold")).grid(row=9, column=0, sticky="w", pady=(15, 5))
        
        scale_frame = ttk.Frame(frm)
        scale_frame.grid(row=10, column=0, sticky="w", pady=5)
        
        self.scale_var = tk.IntVar(value=self.scale)
        self.scale_slider = ttk.Scale(
            scale_frame, 
            from_=MIN_SCALE, 
            to=MAX_SCALE, 
            orient="horizontal",
            command=self.on_scale_change, 
            variable=self.scale_var,
            length=180
        )
        self.scale_slider.grid(row=0, column=0)
        
        self.scale_label = ttk.Label(scale_frame, text=f"{self.scale} px/ед")
        self.scale_label.grid(row=1, column=0, sticky="w")
        
        self.time_label = ttk.Label(frm, text="Время: ---", font=("Arial", 10))
        self.time_label.grid(row=11, column=0, sticky="w", pady=(15, 5))
        
        ttk.Label(frm, text="Вычисления:", font=("Arial", 11, "bold")).grid(row=12, column=0, sticky="w", pady=(15, 5))
        
        log_frame = ttk.Frame(frm)
        log_frame.grid(row=13, column=0, sticky="nsew", pady=5)
        
        self.log_text = tk.Text(log_frame, width=45, height=15, font=TEXT_FONT, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        frm.rowconfigure(13, weight=1)

    def on_canvas_resize(self, event):
        self.center_x = event.width // 2
        self.center_y = event.height // 2
        self.draw_grid()
        if self.last_points:
            self.redraw_points()

    def on_scale_change(self, event=None):
        new_scale = int(round(self.scale_var.get()))
        if new_scale != self.scale:
            self.scale = new_scale
            self.scale_label.config(text=f"{self.scale} px/ед")
            self.draw_grid()
            if self.last_points:
                self.redraw_points()

    def on_algorithm_change(self):
        self.clear_drawing()

    def draw_grid(self):
        self.canvas.delete("all")
        
        s = self.scale
        cx, cy = self.center_x, self.center_y
        gs = self.grid_size
        
        for i in range(-gs, gs + 1):
            x = cx + i * s
            self.canvas.create_line(x, 0, x, self.canvas_size, fill=GRID_COLOR, tags="grid")
            
            y = cy + i * s
            self.canvas.create_line(0, y, self.canvas_size, y, fill=GRID_COLOR, tags="grid")
        
        for i in range(-gs, gs + 1, 5):
            if i == 0:
                continue
            x = cx + i * s
            self.canvas.create_line(x, 0, x, self.canvas_size, fill=GRID_MAJOR_COLOR, tags="grid")
            
            y = cy + i * s
            self.canvas.create_line(0, y, self.canvas_size, y, fill=GRID_MAJOR_COLOR, tags="grid")
        
        self.canvas.create_line(0, cy, self.canvas_size, cy, fill=AXIS_COLOR, width=2, tags="axis")
        self.canvas.create_line(cx, 0, cx, self.canvas_size, fill=AXIS_COLOR, width=2, tags="axis")
        
        self.canvas.create_text(2 * cx - 10, cy - 10, text="X", font=("Arial", 12, "bold"), tags="axis")
        self.canvas.create_text(cx - 10, 10, text="Y", font=("Arial", 12, "bold"), tags="axis")
        
        for i in range(-gs, gs + 1, 2):
            if i != 0:
                x = cx + i * s
                self.canvas.create_text(x, cy + 10, text=str(i), font=("Arial", 8), tags="axis")
                
                y = cy + i * s
                self.canvas.create_text(cx + 10, y, text=str(-i), font=("Arial", 8), tags="axis")
        
        self.canvas.create_text(cx + 12, cy + 12, text="0", font=("Arial", 9, "bold"), tags="axis")
        
        self.canvas.create_text(10, 10, text=f"Масштаб: 1 ед = {s} px", 
                               anchor="nw", font=("Arial", 9), tags="info")

    def draw_raster_square(self, x, y, intensity=255):
        canvas_x, canvas_y = to_canvas_coords(x, y, self.scale, self.center_x, self.center_y)
        
        pixel_size = self.scale - 1
        half_pixel = pixel_size // 2
        
        if intensity < 255:
            gray_value = 255 - intensity
            color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            self.canvas.create_rectangle(
                canvas_x - half_pixel, canvas_y - half_pixel,
                canvas_x + half_pixel, canvas_y + half_pixel,
                fill=color, outline=color, tags="raster"
            )
        else:
            self.canvas.create_rectangle(
                canvas_x - half_pixel, canvas_y - half_pixel,
                canvas_x + half_pixel, canvas_y + half_pixel,
                fill=RASTER_COLOR, outline=RASTER_COLOR, tags="raster"
            )

    def draw_point(self, x, y, color=POINT_COLOR, highlight=False):
        canvas_x, canvas_y = to_canvas_coords(x, y, self.scale, self.center_x, self.center_y)
        
        point_size = max(3, self.scale // 3)
        
        self.canvas.create_rectangle(
            canvas_x - point_size, canvas_y - point_size,
            canvas_x + point_size, canvas_y + point_size,
            fill=color, outline=color, tags="point"
        )
        
        if highlight:
            self.canvas.create_text(
                canvas_x + point_size + 8,
                canvas_y + point_size + 8,
                text=f"({x}, {y})",
                fill=COORD_COLOR,
                font=("Arial", 9, "bold"),
                tags="coord_label"
            )

    def draw_line_segment(self, x1, y1, x2, y2):
        x1_canvas, y1_canvas = to_canvas_coords(x1, y1, self.scale, self.center_x, self.center_y)
        x2_canvas, y2_canvas = to_canvas_coords(x2, y2, self.scale, self.center_x, self.center_y)
        
        self.canvas.create_line(
            x1_canvas, y1_canvas, x2_canvas, y2_canvas,
            fill=LINE_COLOR, width=1, dash=(2, 2), tags="ideal_line"
        )

    def redraw_points(self):
        if not self.last_points:
            return
            
        highlight_points = set()
        algorithm = self.alg_var.get()
        
        if algorithm != "bres_circle":
            try:
                x0 = clamp_int(self.x0_entry.get(), -self.grid_size, self.grid_size)
                y0 = clamp_int(self.y0_entry.get(), -self.grid_size, self.grid_size)
                x1 = clamp_int(self.x1_entry.get(), -self.grid_size, self.grid_size)
                y1 = clamp_int(self.y1_entry.get(), -self.grid_size, self.grid_size)
                highlight_points.add((x0, y0))
                highlight_points.add((x1, y1))
            except:
                pass
        else:
            try:
                x0 = clamp_int(self.x0_entry.get(), -self.grid_size, self.grid_size)
                y0 = clamp_int(self.y0_entry.get(), -self.grid_size, self.grid_size)
                highlight_points.add((x0, y0))
            except:
                pass
        
        if algorithm == "wu_line":
            for point in self.last_points:
                x, y, intensity = point
                self.draw_raster_square(x, y, intensity)
        else:
            for point in self.last_points:
                if len(point) == 2:
                    x, y = point
                    self.draw_raster_square(x, y)
                elif len(point) == 3:
                    x, y, intensity = point
                    self.draw_raster_square(x, y, intensity)
        
        if algorithm != "bres_circle" and len(highlight_points) == 2:
            points_list = list(highlight_points)
            self.draw_line_segment(points_list[0][0], points_list[0][1], 
                                 points_list[1][0], points_list[1][1])
        
        for point in highlight_points:
            self.draw_point(point[0], point[1], highlight=True)

    def write_log(self, lines):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        
        if isinstance(lines, str):
            self.log_text.insert("end", lines)
        else:
            for line in lines:
                self.log_text.insert("end", line + "\n")
        
        self.log_text.config(state="disabled")
        self.log_text.see("1.0") 

    def clear_drawing(self):
        self.canvas.delete("point")
        self.canvas.delete("ideal_line")
        self.canvas.delete("raster")
        self.canvas.delete("coord_label")
        self.last_points = []
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.time_label.config(text="Время: ---")

    def on_clear(self):
        self.clear_drawing()
        self.draw_grid()

    def on_draw(self):
        try:
            x0 = clamp_int(self.x0_entry.get(), -self.grid_size, self.grid_size)
            y0 = clamp_int(self.y0_entry.get(), -self.grid_size, self.grid_size)
            x1 = clamp_int(self.x1_entry.get(), -self.grid_size, self.grid_size)
            y1 = clamp_int(self.y1_entry.get(), -self.grid_size, self.grid_size)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные целочисленные координаты")
            return
        
        algorithm = self.alg_var.get()
        
        self.clear_drawing()
        
        start_time = time.perf_counter()
        
        if algorithm == "naive":
            points, log = naive_line(x0, y0, x1, y1)
        elif algorithm == "dda":
            points, log = dda_line(x0, y0, x1, y1)
        elif algorithm == "bres_line":
            points, log = bresenham_line(x0, y0, x1, y1)
        elif algorithm == "bres_circle":
            points, log = bresenham_circle(x0, y0, x1)
        elif algorithm == "wu_line":
            points, log = wu_line(x0, y0, x1, y1)
        else:
            points, log = [], ["Неизвестный алгоритм"]
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        
        self.last_points = points
        
        if algorithm != "bres_circle":
            header = [
                f"Алгоритм: {algorithm}",
                f"Начальная точка: ({x0}, {y0})",
                f"Конечная точка: ({x1}, {y1})",
                f"Количество точек: {len(points)}",
                f"Время выполнения: {execution_time:.3f} мс",
                "-" * 45
            ]
        else:
            header = [
                f"Алгоритм: {algorithm}",
                f"Центр окружности: ({x0}, {y0})",
                f"Радиус: {x1}",
                f"Количество точек: {len(points)}", 
                f"Время выполнения: {execution_time:.3f} мс",
                "-" * 45
            ]
        
        full_log = header + log
        self.write_log(full_log)
        self.time_label.config(text=f"Время: {execution_time:.3f} мс")
        
        self.redraw_points()

def main():
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
