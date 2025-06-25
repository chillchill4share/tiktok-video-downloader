import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import os
import sys
import threading
import logging
from api import TikTokDownloader 

def setup_logging():
    log_level = logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # Thay đổi tên file log thành download.txt
    base_path = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_path, 'download.txt')
    if os.path.exists(log_path):
        try: os.remove(log_path)
        except OSError: pass
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    logging.info("Hệ thống logging đã được thiết lập.")

# --- THÊM MỚI: Hàm để tìm đường dẫn tài nguyên (icon) ---
def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả môi trường dev và PyInstaller """
    try:
        # PyInstaller tạo một thư mục tạm và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TikTokDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Video Downloader")
        self.root.geometry("680x600")
        self.root.resizable(False, False)
        
        # --- THÊM MỚI: Áp dụng icon cho cửa sổ ---
        try:
            icon_path = resource_path("icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            logging.warning(f"Không thể tải icon: {e}")

        self.downloader = TikTokDownloader()
        self.is_downloading = False
        self.reset_stats()
        
        self.folder_placeholder = "Nhấp để chọn hoặc để trống sẽ lưu vào thư mục Output"
        
        self.create_widgets()

    def reset_stats(self):
        self.success_count = 0
        self.failed_count = 0
        self.total_videos = 0
        self.processed_videos = 0
        self.failed_videos = []

    def create_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        input_frame = ttk.LabelFrame(self.root, text="Nhập liệu", padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        input_frame.columnconfigure(0, weight=1)

        ttk.Label(input_frame, text="Thư mục lưu:").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.folder_entry = ttk.Entry(input_frame, width=60)
        self.folder_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.browse_button = ttk.Button(input_frame, text="Chọn...", command=self.browse_folder)
        self.browse_button.grid(row=1, column=1, sticky="e", padx=(5, 0))
        
        self.folder_entry.insert(0, self.folder_placeholder)
        self.folder_entry.config(foreground="grey")
        self.folder_entry.bind("<FocusIn>", self.on_folder_focus_in)
        self.folder_entry.bind("<FocusOut>", self.on_folder_focus_out)

        ttk.Label(input_frame, text="Link video:").grid(row=2, column=0, sticky="w", pady=(5, 2))
        self.input_text = tk.Text(input_frame, height=8, font=('Segoe UI', 10), relief=tk.SOLID, borderwidth=1)
        self.input_text.grid(row=3, column=0, columnspan=2, sticky="ew")

        mode_frame = ttk.LabelFrame(self.root, text="Tùy chọn", padding="10")
        mode_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        self.mode_var = tk.StringVar(value="multiple")
        ttk.Label(mode_frame, text="Chế độ tải:").pack(side=tk.LEFT, padx=(5,10))
        self.radio_single = ttk.Radiobutton(mode_frame, text="Tải video đơn/nhiều", variable=self.mode_var, value="multiple")
        self.radio_single.pack(side=tk.LEFT, padx=5)
        self.radio_channel = ttk.Radiobutton(mode_frame, text="Tải toàn bộ kênh (Tạm khóa)", variable=self.mode_var, value="all", state=tk.DISABLED)
        self.radio_channel.pack(side=tk.LEFT, padx=5)

        concurrent_frame = ttk.Frame(mode_frame)
        concurrent_frame.pack(side=tk.RIGHT)
        ttk.Label(concurrent_frame, text="Tải đồng thời:").pack(side=tk.LEFT, padx=(0, 5))
        self.concurrent_entry = ttk.Entry(concurrent_frame, width=5)
        self.concurrent_entry.insert(0, "5")
        self.concurrent_entry.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        self.start_button = ttk.Button(control_frame, text="BẮT ĐẦU TẢI", command=self.start_download)
        self.start_button.pack()
        
        status_frame = ttk.LabelFrame(self.root, text="Trạng thái", padding="10")
        status_frame.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        status_frame.rowconfigure(2, weight=1)
        status_frame.columnconfigure(0, weight=1)

        self.progress_label = ttk.Label(status_frame, text="Sẵn sàng...")
        self.progress_label.grid(row=0, column=0, sticky="ew")
        self.progressbar = ttk.Progressbar(status_frame, orient="horizontal", length=100, mode="determinate")
        self.progressbar.grid(row=1, column=0, sticky="ew", pady=5)

        text_frame = ttk.Frame(status_frame)
        text_frame.grid(row=2, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self.status_text = tk.Text(text_frame, height=10, font=('Consolas', 9), relief=tk.SOLID, borderwidth=1, state=tk.DISABLED, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.config(yscrollcommand=scrollbar.set)

    def on_folder_focus_in(self, event):
        if self.folder_entry.get() == self.folder_placeholder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.config(foreground="black")

    def on_folder_focus_out(self, event):
        if not self.folder_entry.get():
            self.folder_entry.insert(0, self.folder_placeholder)
            self.folder_entry.config(foreground="grey")
    
    def log_status(self, message, level="info"):
        self.root.after(0, self._log_status, message, level)

    def _log_status(self, message, level):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{level.upper()}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        if level.lower() == "error": logging.error(message)
        else: logging.info(message)

    def update_progress(self):
        self.root.after(0, self._update_progress)

    def _update_progress(self):
        self.processed_videos = self.success_count + self.failed_count
        if self.total_videos > 0:
            percentage = (self.processed_videos / self.total_videos) * 100
            self.progressbar['value'] = percentage
            self.progress_label.config(text=f"Đang xử lý: {self.processed_videos}/{self.total_videos} | "
                                            f"Thành công: {self.success_count} | Thất bại: {self.failed_count}")
        else:
            self.progress_label.config(text=f"Thành công: {self.success_count} | Thất bại: {self.failed_count}")

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)
            self.folder_entry.config(foreground="black")

    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("Đang tải", "Quá trình tải đang diễn ra. Vui lòng chờ.")
            return
            
        urls_text = self.input_text.get("1.0", tk.END).strip()
        
        save_folder_input = self.folder_entry.get().strip()
        if not save_folder_input or save_folder_input == self.folder_placeholder:
            base_path = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
            self.save_folder = os.path.join(base_path, 'Output')
            self.log_status(f"Thư mục không được chọn, sử dụng mặc định: {self.save_folder}")
        else:
            self.save_folder = save_folder_input

        if not urls_text:
            messagebox.showerror("Lỗi", "Vui lòng nhập link video.")
            return
            
        try:
            self.max_concurrent = int(self.concurrent_entry.get().strip())
        except ValueError: self.max_concurrent = 5
            
        self.urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
        self.is_downloading = True
        self.start_button.config(state=tk.DISABLED, text="ĐANG TẢI...")
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.reset_stats()
        self.update_progress()
        threading.Thread(target=self.run_async_download, daemon=True).start()

    def download_finished(self):
        self.is_downloading = False
        self.start_button.config(state=tk.NORMAL, text="BẮT ĐẦU TẢI")
        summary_message = f"Hoàn tất! Thành công: {self.success_count}, Thất bại: {self.failed_count}."
        self.log_status(summary_message, "info")
        messagebox.showinfo("Hoàn tất", summary_message)
        if self.failed_videos:
            self.log_status("Danh sách video tải thất bại:", "warning")
            for url, reason in self.failed_videos:
                self.log_status(f"- {url}: {reason}", "warning")

    def run_async_download(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_downloads())
        except Exception as e:
            self.log_status(f"Lỗi không xác định trong luồng tải: {e}", "error")
        finally:
            self.root.after(0, self.download_finished)

    async def process_downloads(self):
        self.urls_to_download = self.urls
        self.total_videos = len(self.urls_to_download)
        self.update_progress()
        semaphore = asyncio.Semaphore(self.max_concurrent)
        tasks = [self.download_with_semaphore(semaphore, url) for url in self.urls_to_download]
        await asyncio.gather(*tasks)

    async def download_with_semaphore(self, semaphore, url):
        async with semaphore:
            try:
                username, video_id = self.downloader.extract_username_and_video_id(url)
                
                # Tạo thư mục theo tên kênh
                user_folder = os.path.join(self.save_folder, username)
                os.makedirs(user_folder, exist_ok=True)
                
                file_path = os.path.join(user_folder, f"{video_id}.mp4")

                if os.path.exists(file_path) and os.path.getsize(file_path) > 1024 * 50:
                    self.log_status(f"Video {video_id} đã tồn tại, bỏ qua.", "warning")
                    self.success_count += 1
                else:
                    self.log_status(f"Đang tải: {video_id}")
                    video_bytes = await self.downloader.download_video(url)
                    with open(file_path, "wb") as f: f.write(video_bytes)
                    self.log_status(f"Lưu thành công: {video_id}", "info")
                    self.success_count += 1
            except Exception as e:
                self.log_status(f"Tải thất bại: {self.downloader.extract_video_id(url)} - Lý do: {e}", "error")
                self.failed_count += 1
                self.failed_videos.append((url, str(e)))
            finally:
                self.update_progress()

if __name__ == "__main__":
    setup_logging()
    root = tk.Tk()
    app = TikTokDownloaderGUI(root)
    root.mainloop()
