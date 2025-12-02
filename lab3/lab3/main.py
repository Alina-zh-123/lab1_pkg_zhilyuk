import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps
import numpy as np
import cv2
import os

def to_grayscale(img: Image.Image) -> Image.Image:
    return ImageOps.grayscale(img)

def pil_to_np(img: Image.Image) -> np.ndarray:
    return np.array(img)

def np_to_pil(arr: np.ndarray, mode="L") -> Image.Image:
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode=mode)

def otsu_threshold(gray_img: Image.Image) -> Image.Image:
    arr = pil_to_np(to_grayscale(gray_img))
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    total = arr.size

    sum_total = np.dot(np.arange(256), hist)
    sumB = 0
    wB = 0
    max_var = 0
    threshold = 0

    for t in range(256):
        wB += hist[t]
        if wB == 0:
            continue
        wF = total - wB
        if wF == 0:
            break
        sumB += t * hist[t]
        mB = sumB / wB
        mF = (sum_total - sumB) / wF
        var_between = wB * wF * (mB - mF) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = t

    bin_img = (arr >= threshold) * 255
    return np_to_pil(bin_img)

def isodata_threshold(gray_img: Image.Image, max_iter=100, tol=0.5) -> Image.Image:
    arr = pil_to_np(to_grayscale(gray_img)).astype(np.float32)
    t = arr.mean()
    for _ in range(max_iter):
        lower = arr[arr <= t]
        upper = arr[arr > t]
        if lower.size == 0 or upper.size == 0:
            break
        t_new = 0.5 * (lower.mean() + upper.mean())
        if abs(t_new - t) < tol:
            t = t_new
            break
        t = t_new
    bin_img = (arr >= t + 5) * 255
    return np_to_pil(bin_img.astype(np.uint8))


def adaptive_threshold(gray_img: Image.Image, block_size=11, C=2) -> Image.Image:
    arr = pil_to_np(to_grayscale(gray_img))
    thresh = cv2.adaptiveThreshold(
        arr, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        block_size, 
        C
    )
    return np_to_pil(thresh)

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений")

        self.original_img = None  
        self.display_original = None  
        self.result_img = None
        self.display_result = None

        self.build_layout()

    def build_layout(self):
        self.ctrl_frame = tk.Frame(self.root, padx=8, pady=8, bg="#EFFFFF")
        self.ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.view_frame = tk.Frame(self.root, padx=8, pady=8, bg="#EFFFFF")
        self.view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.ctrl_frame,
            text="Файл",
            font=("Arial", 11, "bold"),
            bg="#EFFFFF"
        ).pack(anchor="w")
        btn_open = tk.Button(self.ctrl_frame, text="Открыть изображение", bg="#EFFFFF", command=self.open_image)
        btn_open.pack(fill=tk.X, pady=2)

        btn_save = tk.Button(self.ctrl_frame, text="Сохранить результат", bg="#EFFFFF", command=self.save_result)
        btn_save.pack(fill=tk.X, pady=2)

        btn_reset = tk.Button(self.ctrl_frame, text="Сбросить (к оригиналу)", bg="#EFFFFF", command=self.reset_result)
        btn_reset.pack(fill=tk.X, pady=2)

        tk.Label(self.ctrl_frame, text=" ", bg="#EFFFFF").pack() 

        tk.Label(
            self.ctrl_frame,
            text="Сглаживание (низкочастотные)",
            bg="#EFFFFF",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")
        self.gauss_radius = tk.DoubleVar(value=2.0)
        tk.Label(self.ctrl_frame, text="Размер ядра", bg="#EFFFFF").pack(anchor="w")
        tk.Scale(self.ctrl_frame, bg="#EFFFFF", variable=self.gauss_radius, from_=0.5, to=10.0, resolution=0.5, orient=tk.HORIZONTAL).pack(fill=tk.X)
        tk.Button(self.ctrl_frame, text="Фильтр Гаусса", bg="#EFFFFF", command=self.apply_gaussian).pack(fill=tk.X, pady=2)
        self.box_radius = tk.IntVar(value=2)
        tk.Label(self.ctrl_frame, text="Размер ядра", bg="#EFFFFF").pack(anchor="w")
        tk.Scale(self.ctrl_frame, bg="#EFFFFF", variable=self.box_radius, from_=1, to=10, resolution=1, orient=tk.HORIZONTAL).pack(fill=tk.X)
        tk.Button(self.ctrl_frame, text="Усредняющий фильтр", bg="#EFFFFF", command=self.apply_box).pack(fill=tk.X, pady=2)

        tk.Label(self.ctrl_frame, text=" ", bg="#EFFFFF").pack()

        tk.Label(
            self.ctrl_frame,
            text="Глобальная пороговая обработка",
            font=("Arial", 11, "bold"),
            bg="#EFFFFF"
        ).pack(anchor="w")
        tk.Button(self.ctrl_frame, text="Метод Оцу", bg="#EFFFFF", command=self.apply_otsu).pack(fill=tk.X, pady=2)
        tk.Button(self.ctrl_frame, text="ISODATA", bg="#EFFFFF", command=self.apply_isodata).pack(fill=tk.X, pady=2)

        tk.Label(self.ctrl_frame, text=" ", bg="#EFFFFF").pack()

        tk.Label(
            self.ctrl_frame,
            text="Адаптивная пороговая обработка",
            font=("Arial", 11, "bold"),
            bg="#EFFFFF"
        ).pack(anchor="w")
        self.max_window_size = tk.IntVar(value=7)
        tk.Label(self.ctrl_frame, text="Размер окна", bg="#EFFFFF").pack(anchor="w")
        tk.Scale(self.ctrl_frame, bg="#EFFFFF", variable=self.max_window_size, from_=3, to=15, resolution=2, orient=tk.HORIZONTAL).pack(fill=tk.X)
        tk.Button(self.ctrl_frame, text="Адаптивный порог", bg="#EFFFFF", command=self.apply_adaptive_median).pack(fill=tk.X, pady=2)

        self.canvas = tk.Canvas(self.view_frame, bg="#EFFFFF")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.redraw)

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Открыть изображение",
            filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not path:
            return
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Ошибка открытия", str(e))
            return
        self.original_img = img
        self.result_img = img.copy()
        self.redraw()

    def save_result(self):
        if self.result_img is None:
            messagebox.showinfo("Нет результата", "Сначала примените обработку или откройте изображение.")
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить результат",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp"), ("TIFF", "*.tif;*.tiff")]
        )
        if not path:
            return
        try:
            self.result_img.save(path)
            messagebox.showinfo("Готово", f"Результат сохранён:\n{os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def reset_result(self):
        if self.original_img is None:
            return
        self.result_img = self.original_img.copy()
        self.redraw()

    def apply_gaussian(self):
        if self.result_img is None:
            return
        radius = float(self.gauss_radius.get())
        self.result_img = self.result_img.filter(ImageFilter.GaussianBlur(radius=radius))
        self.redraw()

    def apply_box(self):
        if self.result_img is None:
            return
        radius = int(self.box_radius.get())
        self.result_img = self.result_img.filter(ImageFilter.BoxBlur(radius))
        self.redraw()

    def apply_otsu(self):
        if self.result_img is None:
            return
        self.result_img = otsu_threshold(self.result_img)
        self.redraw()

    def apply_isodata(self):
        if self.result_img is None:
            return
        self.result_img = isodata_threshold(self.result_img)
        self.redraw()

    def apply_adaptive_median(self):
        if self.result_img is None:
            return
        max_window = int(self.max_window_size.get())
        if max_window % 2 == 0:
            max_window += 1
        self.result_img = adaptive_threshold(self.result_img, block_size=max_window, C=2)
        self.redraw()

    def make_preview(self, img: Image.Image, max_w, max_h):
        if img is None:
            return None
        w, h = img.size
        scale = min(max_w / max(w, 1), max_h / max(h, 1))
        scale = max(scale, 1e-6)
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        thumb = img.resize(new_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(thumb)

    def redraw(self, event=None):
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 0 or ch <= 0:
            return
        
        half_w = cw // 2
        
        self.canvas.create_text(half_w // 2, 20, text="До", anchor="n", font=("Arial", 11, "bold"))
        self.canvas.create_text(half_w + half_w // 2, 20, text="После", anchor="n", font=("Arial", 11, "bold"))

        if self.original_img is not None:
            left_img = self.make_preview(self.original_img, half_w - 40, ch - 80)
            if left_img:
                img_w = left_img.width()
                img_h = left_img.height()
                x_pos = (half_w - img_w) // 2
                y_pos = 40 + (ch - 80 - img_h) // 2
                self.canvas.create_image(x_pos, y_pos, image=left_img, anchor="nw")
                self.display_original = left_img

        if self.result_img is not None:
            right_img = self.make_preview(self.result_img, half_w - 40, ch - 80)
            if right_img:
                img_w = right_img.width()
                img_h = right_img.height()
                x_pos = half_w + (half_w - img_w) // 2
                y_pos = 40 + (ch - 80 - img_h) // 2
                self.canvas.create_image(x_pos, y_pos, image=right_img, anchor="nw")
                self.display_result = right_img

def main():
    root = tk.Tk()
    app = ImageApp(root)
    root.configure(bg="#EFFFFF")
    root.geometry("1100x650")
    root.mainloop()

if __name__ == "__main__":
    main()