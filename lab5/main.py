import tkinter as tk
from tkinter import filedialog
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

class Polygon:
    def __init__(self, points):
        self.points = points

class ClippingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы отсечения")
        self.root.geometry("1100x700")
        
        self.lines = []
        self.polygon = None
        self.clip_window = None
        self.clipped_lines = []
        self.clipped_polygon = None
        
        self.original_color = "blue"
        self.clip_color = "red"
        self.clipped_color = "green"
        self.polygon_color = "yellow"
        
        self.scale = 50
        self.offset_x = 400  
        self.offset_y = 350
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.Frame(main_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Button(left_frame, text="Загрузить файл", command=self.load_file,
                 width=20).pack(pady=5)
        tk.Button(left_frame, text="Отсечь отрезки", command=self.clip_lines,
                 width=20).pack(pady=5)
        tk.Button(left_frame, text="Отсечь многоугольник", command=self.clip_polygon,
                 width=20).pack(pady=5)
        tk.Button(left_frame, text="Очистить", command=self.clear_canvas,
                 width=20).pack(pady=5)
        
        info_text = """
Алгоритмы отсечения:
• Сазерленда-Коэна - для отрезков
• Сазерленда-Ходжмана - для многоугольника

Цвета:
• Синий - отрезки
• Красный - отсекающее окно
• Зеленый - результат отсечения
• Желтый - многоугольник

Формат входных данных:
n *число отрезков*
X1_1 Y1_1 X2_1 Y2_1
X1_2 Y1_2 X2_2 Y2_2
…
X1_n Y1_n X2_n Y2_n 
*координаты отрезков*
m *углов у многоугольника*
X1 Y1
X2 Y2
…
Xm Ym *координаты вершин*
Xmin Ymin Xmax Ymax 
*координаты отсекающего 
прямоугольного окна*
        """
        tk.Label(left_frame, text=info_text, justify=tk.LEFT, 
                bg="white", relief=tk.SUNKEN).pack(pady=10, fill=tk.X)
        
        self.canvas = tk.Canvas(main_frame, bg="white", width=800, height=700)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
    def calculate_scale_and_offset(self):
        all_points = []
        
        for line in self.lines:
            all_points.extend([line.p1, line.p2])
        
        if self.polygon:
            all_points.extend(self.polygon.points)
        
        if self.clip_window:
            all_points.extend([
                Point(self.clip_window['xmin'], self.clip_window['ymin']),
                Point(self.clip_window['xmax'], self.clip_window['ymax'])
            ])
        
        if not all_points:
            return 50, 400, 350 
        
        min_x = min(p.x for p in all_points)
        max_x = max(p.x for p in all_points)
        min_y = min(p.y for p in all_points)
        max_y = max(p.y for p in all_points)
        
        padding = max((max_x - min_x) * 0.1, (max_y - min_y) * 0.1, 1)
        min_x -= padding
        max_x += padding
        min_y -= padding
        max_y += padding
        
        data_width = max_x - min_x
        data_height = max_y - min_y
        
        canvas_width = 800
        canvas_height = 700
        
        scale_x = canvas_width / data_width if data_width > 0 else 50
        scale_y = canvas_height / data_height if data_height > 0 else 50
        scale = min(scale_x, scale_y) * 0.9  
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        offset_x = canvas_width / 2 - center_x * scale
        offset_y = canvas_height / 2 + center_y * scale  
        
        return scale, offset_x, offset_y
        
    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                
                self.lines = []
                self.polygon = None
                self.clip_window = None
                self.clipped_lines = []
                self.clipped_polygon = None
                
                index = 0
                
                n = int(lines[index].strip())
                index += 1
                
                for i in range(n):
                    coords = list(map(float, lines[index].strip().split()))
                    if len(coords) == 4:
                        p1 = Point(coords[0], coords[1])
                        p2 = Point(coords[2], coords[3])
                        self.lines.append(Line(p1, p2))
                    index += 1
                
                m = int(lines[index].strip())
                index += 1
                
                polygon_points = []
                for i in range(m):
                    coords = list(map(float, lines[index].strip().split()))
                    if len(coords) == 2:
                        polygon_points.append(Point(coords[0], coords[1]))
                    index += 1
                
                if polygon_points:
                    self.polygon = Polygon(polygon_points)
                
                if index < len(lines):
                    coords = list(map(float, lines[index].strip().split()))
                    if len(coords) == 4:
                        self.clip_window = {
                            'xmin': min(coords[0], coords[2]),
                            'ymin': min(coords[1], coords[3]),
                            'xmax': max(coords[0], coords[2]),
                            'ymax': max(coords[1], coords[3])
                        }
                
                self.scale, self.offset_x, self.offset_y = self.calculate_scale_and_offset()
                
                self.draw_scene()
                print(f"Загружено: {n} отрезков, {m}-угольник")
                print(f"Масштаб: {self.scale:.2f}, Смещение: ({self.offset_x:.1f}, {self.offset_y:.1f})")
                
            except Exception as e:
                print(f"Ошибка загрузки файла: {str(e)}")
    
    def draw_scene(self):
        self.canvas.delete("all")
        self.draw_coordinate_system()
        
        if self.clip_window:
            x1, y1 = self.transform_coords(self.clip_window['xmin'], self.clip_window['ymin'])
            x2, y2 = self.transform_coords(self.clip_window['xmax'], self.clip_window['ymax'])
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.clip_color, width=2)
        
        for line in self.lines:
            x1, y1 = self.transform_coords(line.p1.x, line.p1.y)
            x2, y2 = self.transform_coords(line.p2.x, line.p2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.original_color, width=2)
        
        if self.polygon:
            points = []
            for point in self.polygon.points:
                x, y = self.transform_coords(point.x, point.y)
                points.extend([x, y])
            
            if len(points) >= 6:
                self.canvas.create_polygon(points, fill="", outline=self.polygon_color, width=2)
        
        for line in self.clipped_lines:
            x1, y1 = self.transform_coords(line.p1.x, line.p1.y)
            x2, y2 = self.transform_coords(line.p2.x, line.p2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.clipped_color, width=3)
        
        if self.clipped_polygon:
            points = []
            for point in self.clipped_polygon.points:
                x, y = self.transform_coords(point.x, point.y)
                points.extend([x, y])
            
            if len(points) >= 6:
                self.canvas.create_polygon(points, fill="green", outline=self.clipped_color, width=3)
    
    def draw_coordinate_system(self):
        width = 800
        height = 700
        
        left_math = -self.offset_x / self.scale
        right_math = (width - self.offset_x) / self.scale
        bottom_math = (self.offset_y - height) / self.scale 
        top_math = self.offset_y / self.scale
        
        center_x = width / 2
        center_y = height / 2
        
        x_axis_y = self.transform_coords(0, 0)[1]
        self.canvas.create_line(0, x_axis_y, width, x_axis_y, fill="gray", width=1, arrow=tk.LAST)
        
        y_axis_x = self.transform_coords(0, 0)[0]
        self.canvas.create_line(y_axis_x, height, y_axis_x, 0, fill="gray", width=1, arrow=tk.LAST)
        
        self.canvas.create_text(width - 15, x_axis_y - 10, text="X", font=("Arial", 12, "bold"), fill="black")
        self.canvas.create_text(y_axis_x + 10, 15, text="Y", font=("Arial", 12, "bold"), fill="black")
        
        base_grid_step = 1.0
        while self.scale * base_grid_step < 30:
            base_grid_step *= 2
        while self.scale * base_grid_step > 100:
            base_grid_step /= 2
        
        grid_step = base_grid_step
        
        start_x = math.floor(left_math / grid_step) * grid_step
        end_x = math.ceil(right_math / grid_step) * grid_step
        
        for x in [i * grid_step for i in range(int(start_x / grid_step), int(end_x / grid_step) + 1)]:
            if abs(x) < 1e-10:  
                continue
                
            screen_x = self.transform_coords(x, 0)[0]
            self.canvas.create_line(screen_x, 0, screen_x, height, fill="lightgray", width=1)
            self.canvas.create_text(screen_x, x_axis_y + 12, text=f"{int(x)}", 
                                   font=("Arial", 8), fill="black")
        
        start_y = math.floor(bottom_math / grid_step) * grid_step
        end_y = math.ceil(top_math / grid_step) * grid_step
        
        for y in [i * grid_step for i in range(int(start_y / grid_step), int(end_y / grid_step) + 1)]:
            if abs(y) < 1e-10:
                continue
                
            screen_y = self.transform_coords(0, y)[1]
            self.canvas.create_line(0, screen_y, width, screen_y, fill="lightgray", width=1)
            self.canvas.create_text(y_axis_x + 12, screen_y, text=f"{int(y)}", 
                                   font=("Arial", 8), fill="black")
        
        zero_x, zero_y = self.transform_coords(0, 0)
        self.canvas.create_text(zero_x + 8, zero_y + 8, text="0", 
                               font=("Arial", 8), fill="black")
    
    def transform_coords(self, x, y):
        screen_x = self.offset_x + x * self.scale
        screen_y = self.offset_y - y * self.scale 
        return screen_x, screen_y
    
    def clip_lines(self):
        if not self.clip_window or not self.lines:
            print("Нет данных для отсечения отрезков")
            return
        
        self.clipped_lines = []
        
        for line in self.lines:
            clipped_line = self.cohen_sutherland_clip(line)
            if clipped_line:
                self.clipped_lines.append(clipped_line)
        
        self.draw_scene()
        print(f"Отсечено {len(self.clipped_lines)} отрезков")
    
    def cohen_sutherland_clip(self, line):
        x1, y1 = line.p1.x, line.p1.y
        x2, y2 = line.p2.x, line.p2.y
        
        xmin, ymin = self.clip_window['xmin'], self.clip_window['ymin']
        xmax, ymax = self.clip_window['xmax'], self.clip_window['ymax']
        
        def compute_code(x, y):
            code = 0
            if x < xmin:
                code |= 1  
            elif x > xmax:
                code |= 2  
            if y < ymin:
                code |= 4 
            elif y > ymax:
                code |= 8 
            return code
        
        code1 = compute_code(x1, y1)
        code2 = compute_code(x2, y2)
        
        while True:
            if code1 == 0 and code2 == 0:
                return Line(Point(x1, y1), Point(x2, y2))
            elif code1 & code2 != 0:
                return None
            else:
                code_out = code1 if code1 != 0 else code2
                
                if code_out & 8: 
                    x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                    y = ymax
                elif code_out & 4: 
                    x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                    y = ymin
                elif code_out & 2: 
                    y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                    x = xmax
                elif code_out & 1: 
                    y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                    x = xmin
                
                if code_out == code1:
                    x1, y1 = x, y
                    code1 = compute_code(x1, y1)
                else:
                    x2, y2 = x, y
                    code2 = compute_code(x2, y2)
    
    def clip_polygon(self):
        if not self.clip_window or not self.polygon:
            print("Нет данных для отсечения многоугольника")
            return
        
        clipped_polygon = self.sutherland_hodgman_clip(self.polygon)
        if clipped_polygon:
            self.clipped_polygon = clipped_polygon
            self.draw_scene()
            print("Многоугольник отсечен")
        else:
            print("Многоугольник полностью отсечен")
    
    def sutherland_hodgman_clip(self, polygon):
        xmin, ymin = self.clip_window['xmin'], self.clip_window['ymin']
        xmax, ymax = self.clip_window['xmax'], self.clip_window['ymax']
        
        clip_edges = [
            (Point(xmin, ymin), Point(xmin, ymax)),  
            (Point(xmax, ymin), Point(xmax, ymax)),  
            (Point(xmin, ymin), Point(xmax, ymin)),  
            (Point(xmin, ymax), Point(xmax, ymax))   
        ]
        
        output_list = polygon.points
        
        for edge in clip_edges:
            input_list = output_list
            output_list = []
            
            if not input_list:
                break
                
            s = input_list[-1]
            
            for point in input_list:
                if self.is_inside(point, edge):
                    if not self.is_inside(s, edge):
                        output_list.append(self.intersection(s, point, edge))
                    output_list.append(point)
                elif self.is_inside(s, edge):
                    output_list.append(self.intersection(s, point, edge))
                s = point
        
        if len(output_list) >= 3:
            return Polygon(output_list)
        return None
    
    def is_inside(self, point, edge):
        if edge[0].x == edge[1].x:  
            if edge[0].x == self.clip_window['xmin']:  
                return point.x >= edge[0].x
            else:  
                return point.x <= edge[0].x
        else:  
            if edge[0].y == self.clip_window['ymin']:  
                return point.y >= edge[0].y
            else:  
                return point.y <= edge[0].y
    
    def intersection(self, p1, p2, edge):
        if edge[0].x == edge[1].x:  
            x = edge[0].x
            y = p1.y + (p2.y - p1.y) * (x - p1.x) / (p2.x - p1.x)
        else: 
            y = edge[0].y
            x = p1.x + (p2.x - p1.x) * (y - p1.y) / (p2.y - p1.y)
        
        return Point(x, y)
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.lines = []
        self.polygon = None
        self.clip_window = None
        self.clipped_lines = []
        self.clipped_polygon = None
        self.scale = 50
        self.offset_x = 400
        self.offset_y = 350
        self.draw_coordinate_system()
        print("Холст очищен")

def main():
    root = tk.Tk()
    app = ClippingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
