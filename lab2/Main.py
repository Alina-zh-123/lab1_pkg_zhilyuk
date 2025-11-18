import os
import cv2
import numpy as np
from tkinter import *
from tkinter import ttk, filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from PIL import Image
import time

class ImageInfoApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.processing = False
        self.max_workers = 4  
        
    def setup_ui(self):
        self.root.title("Информация об изображениях")
        self.root.geometry("1000x600")
        
        self.status_label = Label(text="Готов к работе")
        self.status_label.pack(pady=5)
        
        frame = Frame(self.root)
        frame.pack(fill=BOTH, expand=1, padx=10, pady=5)

        columns = ("name", "size", "resolution", "depth", "format")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)

        self.tree.heading("name", text="Имя файла")
        self.tree.heading("size", text="Размер (пиксели)")
        self.tree.heading("resolution", text="Разрешение (DPI)")
        self.tree.heading("depth", text="Глубина цвета")
        self.tree.heading("format", text="Сжатие")

        self.tree.column("name", width=200)
        self.tree.column("size", width=120)
        self.tree.column("resolution", width=150)
        self.tree.column("depth", width=150)
        self.tree.column("format", width=150)

        scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=1)
        
        button_frame = Frame(self.root)
        button_frame.pack(side=BOTTOM, pady=10)
        
        self.btn_load = Button(button_frame, text="Выбрать папку", command=self.load_folder, state=NORMAL)
        self.btn_load.pack(side=LEFT, padx=5)
        
    def get_image_info_fast(self, path):
        try:
            name = os.path.basename(path)
            file_ext = os.path.splitext(path)[1].lower()
            
            try:
                with Image.open(path) as img:
                    width, height = img.size
                    size = f"{width}x{height}"
                    
                    dpi = img.info.get('dpi')
                    if dpi and dpi != (0, 0):
                        resolution = f"{dpi[0]}x{dpi[1]} DPI"
                    else:
                        resolution = self.get_default_dpi(file_ext)
                    
                    mode = img.mode
                    depth_info = self.get_depth_from_pil_mode(mode, file_ext)
                    
            except Exception as e:
                return self.get_image_info_opencv(path)
            
            compression_info = self.get_compression_info_fast(path, file_ext)
            
            return (name, size, resolution, depth_info, compression_info)
            
        except Exception as e:
            return (os.path.basename(path), "Error", "Error", "Error")

    def get_image_info_opencv(self, path):
        try:
            img = cv2.imread(path)
            if img is None:
                with open(path, 'rb') as f:
                    img_array = np.frombuffer(f.read(), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is None:
                return (os.path.basename(path), "Error", "Error", "Error", "Не удалось открыть")
            
            name = os.path.basename(path)
            height, width = img.shape[:2]
            size = f"{width}x{height}"
            
            file_ext = os.path.splitext(path)[1].lower()
            resolution = self.get_dpi_from_image(path)
            depth_info = self.get_depth_info(img, path)
            compression_info = self.get_compression_info_fast(path, file_ext)
            
            return (name, size, resolution, depth_info, compression_info)
            
        except Exception as e:
            return (os.path.basename(path), "Error", "Error", "Error", str(e))

    def get_depth_from_pil_mode(self, mode, file_ext):
        mode_depth = {
            '1': '1 bit',
            'L': '8 bit',
            'P': '8 bit',
            'RGB': '24 bit',
            'RGBA': '32 bit',
            'CMYK': '32 bit',
            'YCbCr': '24 bit',
            'I': '32 bit',
            'F': '32 bit'
        }
        
        depth = mode_depth.get(mode, f"Unknown mode: {mode}")
        
        if file_ext == '.gif' and mode == 'P':
            return "8 bit, Indexed (256 colors)"
        
        return depth

    def get_default_dpi(self, file_ext):
        dpi_map = {
            '.bmp': '96x96 DPI',
            '.jpg': '72x72 DPI', 
            '.jpeg': '72x72 DPI',
            '.png': '96x96 DPI',
            '.tif': '300x300 DPI',
            '.tiff': '300x300 DPI',
            '.gif': '72x72 DPI',
            '.pcx': '96x96 DPI'
        }
        return dpi_map.get(file_ext, 'N/A')

    def get_compression_info_fast(self, path, file_ext):
        try:
            file_size = os.path.getsize(path)
            file_size_kb = file_size // 1024
            
            compression_map = {
                '.bmp': 'BMP',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.png': 'PNG',
                '.tif': 'TIFF',
                '.tiff': 'TIFF', 
                '.gif': 'LZW',
                '.pcx': 'RLE'
            }
            
            compression = compression_map.get(file_ext, 'Unknown')
            return f"{compression}, {file_size_kb}KB"
        except:
            return "N/A"

    def scan_folder_fast(self, folder):
        supported_formats = (".jpg", ".jpeg", ".gif", ".bmp", ".png", ".tif", ".tiff", ".pcx")
        image_files = []
        
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(supported_formats):
                    full_path = os.path.join(root, file)
                    image_files.append(full_path)
        
        total_files = len(image_files)
        self.update_status(f"Найдено {total_files} файлов. Обработка...")
        
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {executor.submit(self.get_image_info_fast, path): path for path in image_files}
            
            for future in as_completed(future_to_path):
                if not self.processing:
                    break
                    
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if completed % 10 == 0 or total_files < 20:
                        self.update_status(f"Обработано {completed}/{total_files} файлов")
                        self.root.update_idletasks()
                        
                except Exception as e:
                    print(f"Ошибка при обработке файла: {e}")
        
        return results

    def load_folder(self):
        if self.processing:
            return
            
        folder = filedialog.askdirectory()
        if folder:
            thread = threading.Thread(target=self.process_folder, args=(folder,))
            thread.daemon = True
            thread.start()

    def process_folder(self, folder):
        self.processing = True
        
        start_time = time.time()
        
        try:
            self.root.after(0, self.clear_table)
            
            images = self.scan_folder_fast(folder)
            
            if self.processing:
                self.root.after(0, lambda: self.add_results_to_table(images))
                
                end_time = time.time()
                processing_time = end_time - start_time
                self.update_status(f"Готово! Обработано {len(images)} файлов за {processing_time:.2f} сек")
                
        except Exception as e:
            self.update_status(f"Ошибка: {str(e)}")
        finally:
            self.processing = False
            self.root.after(0, self.processing_finished)

    def add_results_to_table(self, images):
        success_count = 0
        error_count = 0
        
        for img in images:
            self.tree.insert("", END, values=img)
            if "Error" in img[1]:
                error_count += 1
            else:
                success_count += 1
        
        self.update_status(f"Успешно: {success_count}, Ошибок: {error_count}")

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def stop_processing(self):
        self.processing = False
        self.update_status("Обработка остановлена пользователем")

    def processing_finished(self):
        self.progress.stop()
        self.btn_load.config(state=NORMAL)

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))

    def get_depth_info(self, img, path):
        try:
            dtype = img.dtype
            if dtype == np.uint8:
                bits_per_channel = 8
            elif dtype == np.uint16:
                bits_per_channel = 16
            elif dtype == np.float32:
                bits_per_channel = 32
            elif dtype == np.float64:
                bits_per_channel = 64
            else:
                bits_per_channel = "Unknown"
            
            if len(img.shape) == 2:
                channels = 1
                color_type = "Grayscale"
            elif len(img.shape) == 3:
                channels = img.shape[2]
                if channels == 3:
                    color_type = "BGR"
                elif channels == 4:
                    color_type = "BGRA"
                else:
                    color_type = f"{channels} channels"
            else:
                channels = "Unknown"
                color_type = "Unknown"
            
            if isinstance(bits_per_channel, int) and isinstance(channels, int):
                total_bits = bits_per_channel * channels
            else:
                total_bits = "Unknown"
            
            file_ext = os.path.splitext(path)[1].lower()
            if file_ext in ['.gif']:
                return "8 bit, Indexed (256 colors)"
            elif file_ext in ['.bmp']:
                bmp_depth = self.get_bmp_bit_depth(path)
                if bmp_depth:
                    return f"{bmp_depth}, {color_type}"
            
            if total_bits != "Unknown":
                return f"{total_bits} bit, {color_type}"
            else:
                return f"{bits_per_channel} bit/channel, {color_type}"
                
        except Exception as e:
            return "Unknown"

    def get_bmp_bit_depth(self, path):
        try:
            with open(path, 'rb') as f:
                header = f.read(30)
                if header[0:2] != b'BM':
                    return None
                bit_count = int.from_bytes(header[28:30], byteorder='little', signed=False)
                bit_depth_map = {1: "1 bit", 4: "4 bit", 8: "8 bit", 16: "16 bit", 24: "24 bit", 32: "32 bit"}
                return bit_depth_map.get(bit_count, f"{bit_count} bit")
        except:
            return None

    def get_dpi_from_image(self, path):
        try:
            if path.lower().endswith('.bmp'):
                dpi = self.get_bmp_dpi(path)
                if dpi:
                    return dpi
                return "96x96 DPI"
            elif path.lower().endswith(('.jpg', '.jpeg')):
                return self.get_jpeg_dpi(path) or "72x72 DPI"
            elif path.lower().endswith('.png'):
                return "96x96 DPI"
            elif path.lower().endswith(('.tiff', '.tif')):
                return "300x300 DPI"
            elif path.lower().endswith('.gif'):
                return "72x72 DPI"
            elif path.lower().endswith('.pcx'):
                return "96x96 DPI"
        except:
            pass
        return "N/A"

    def get_bmp_dpi(self, path):
        try:
            with open(path, 'rb') as f:
                header = f.read(70)
                if header[0:2] != b'BM':
                    return None
                ppm_x = int.from_bytes(header[38:42], byteorder='little', signed=False)
                ppm_y = int.from_bytes(header[42:46], byteorder='little', signed=False)
                if ppm_x > 0 and ppm_y > 0:
                    dpi_x = round(ppm_x / 39.3701)
                    dpi_y = round(ppm_y / 39.3701)
                    return f"{dpi_x}x{dpi_y} DPI"
        except:
            pass
        return None

    def get_jpeg_dpi(self, path):
        try:
            with open(path, 'rb') as f:
                data = f.read()
                pos = 0
                while pos < len(data) - 1:
                    if data[pos] == 0xFF and data[pos + 1] == 0xE0:
                        length = int.from_bytes(data[pos + 2:pos + 4], byteorder='big')
                        if data[pos + 4:pos + 9] == b'JFIF\0':
                            density_unit = data[pos + 11]
                            x_density = int.from_bytes(data[pos + 12:pos + 14], byteorder='big')
                            y_density = int.from_bytes(data[pos + 14:pos + 16], byteorder='big')
                            if density_unit == 1:
                                return f"{x_density}x{y_density} DPI"
                            elif density_unit == 2:
                                return f"{x_density*2.54}x{y_density*2.54} DPI"
                    pos += 1
        except:
            pass
        return None

if __name__ == "__main__":
    root = Tk()
    app = ImageInfoApp(root)
    root.mainloop()
