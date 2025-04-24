import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import asyncio
from api import TikTokDownloader
import os
import sys
import threading
import logging
from tkinter import ttk
from logic import handle_partial_file

class TikTokDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tải Video TikTok")
        self.root.resizable(False, False)
        self.file_lock = threading.Lock()
        self.configure_logging()
        self.configure_icon()
        self.downloader = TikTokDownloader()
        self.success_count = 0
        self.failed_count = 0
        self.is_downloading = False
        self.is_paused = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()  
        self.current_tasks = []
        self.remaining_urls = []
        self.total_videos = 0
        self.failed_videos = []
        self.initialize_widgets()
        self.setup_tooltips()

    def configure_logging(self):
        base_path = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_path, 'download.log')
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
                logging.info("Xóa file log cũ thành công")
            except Exception as e:
                logging.error(f"Lỗi xóa file log cũ: {e}")
        logging.basicConfig(filename=log_path, level=logging.INFO,
                           format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')

    def configure_icon(self):
        base_path = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(sys._MEIPASS, 'icon.ico') if hasattr(sys, '_MEIPASS') else os.path.join(base_path, 'icon.ico')
        if not os.path.exists(icon_path) and hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
                logging.info("Áp dụng biểu tượng thành công")
            except Exception as e:
                logging.warning(f"Lỗi áp dụng biểu tượng: {e}")
        else:
            logging.warning("Không tìm thấy biểu tượng, sử dụng mặc định")

    def initialize_widgets(self):
        input_width = 60

        tk.Label(self.root, text="Thư mục lưu:", anchor="e", width=15).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.folder_entry = tk.Entry(self.root, width=input_width, fg="grey")
        self.folder_entry.insert(0, "E:\\Videos")
        self.folder_entry.bind("<FocusIn>", self.handle_folder_placeholder_clear)
        self.folder_entry.bind("<FocusOut>", self.handle_folder_placeholder_restore)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3)

        tk.Button(self.root, text="Chọn", command=self.browse_folder).grid(row=0, column=4, padx=5, pady=5)

        tk.Label(self.root, text="Link video/user:", anchor="e", width=15).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.input_text = tk.Text(self.root, height=10, width=input_width, fg="grey")
        self.input_text.insert("1.0", "https://www.tiktok.com/@abc/video/5314633447174692735")
        self.input_text.bind("<FocusIn>", self.handle_input_placeholder_clear)
        self.input_text.bind("<FocusOut>", self.handle_input_placeholder_restore)
        self.input_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        tk.Button(self.root, text="Clear", command=self.clear_input_line, state=tk.DISABLED).grid(row=1, column=4, padx=5, pady=5, sticky="n")
        tk.Button(self.root, text="Clear All", command=self.clear_input_all, state=tk.DISABLED).grid(row=1, column=4, padx=5, pady=5, sticky="s")

        tk.Label(self.root, text="Tải đồng thời:", anchor="e", width=15).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.concurrent_entry = tk.Entry(self.root, width=10)
        self.concurrent_entry.insert(0, "3")
        self.concurrent_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.stats_label = tk.Label(self.root, text="Thành công: 0 | Thất bại: 0", anchor="center", width=input_width)
        self.stats_label.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        self.mode_var = tk.StringVar(value="single")
        tk.Radiobutton(self.root, text="Video đơn", variable=self.mode_var, value="single").grid(row=4, column=1, padx=2, pady=5)
        tk.Radiobutton(self.root, text="Nhiều video", variable=self.mode_var, value="multiple").grid(row=4, column=2, padx=2, pady=5)
        tk.Radiobutton(self.root, text="Tất cả từ kênh", variable=self.mode_var, value="all", state=tk.DISABLED).grid(row=4, column=3, padx=2, pady=5)

        self.start_button = tk.Button(self.root, text="Bắt đầu tải", command=self.start_download)
        self.start_button.grid(row=5, column=1, padx=5, pady=5)

        self.pause_button = tk.Button(self.root, text="Tạm dừng", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.grid(row=5, column=2, padx=5, pady=5)

        self.stop_button = tk.Button(self.root, text="Dừng", command=self.stop_download, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=3, padx=5, pady=5)

        tk.Label(self.root, text="Trạng thái:", anchor="e", width=15).grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.status_text = tk.Text(self.root, height=10, width=input_width)
        self.status_text.grid(row=6, column=1, columnspan=3, padx=5, pady=5)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=6, column=4, sticky="ns")
        self.status_text.config(yscrollcommand=scrollbar.set)

        tk.Button(self.root, text="Clear Status", command=self.clear_status).grid(row=6, column=4, padx=5, pady=5, sticky="s")

    def handle_folder_placeholder_clear(self, event):
        if self.folder_entry.get() == "E:\\Videos":
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.config(fg="black")

    def handle_folder_placeholder_restore(self, event):
        if not self.folder_entry.get():
            self.folder_entry.insert(0, "E:\\Videos")
            self.folder_entry.config(fg="grey")

    def handle_input_placeholder_clear(self, event):
        if self.input_text.get("1.0", tk.END).strip() == "https://www.tiktok.com/@abc/video/5314633447174692735":
            self.input_text.delete("1.0", tk.END)
            self.input_text.config(fg="black")

    def handle_input_placeholder_restore(self, event):
        if not self.input_text.get("1.0", tk.END).strip():
            self.input_text.insert("1.0", "https://www.tiktok.com/@abc/video/5314633447174692735")
            self.input_text.config(fg="grey")

    def setup_tooltips(self):
        self.tooltips = {
            self.folder_entry: "Chọn thư mục để lưu video tải về",
            self.input_text: "Nhập link video hoặc tên người dùng, phân tách bằng dấu phẩy, chấm phẩy hoặc xuống dòng",
            self.concurrent_entry: "Số lượng video tải đồng thời (tối đa 10)",
            self.status_text: "Hiển thị trạng thái quá trình tải"
        }
        for widget, tip in self.tooltips.items():
            widget.bind("<Enter>", lambda e, t=tip, w=widget: self.show_tooltip(e, t, w))
            widget.bind("<Leave>", lambda e: self.hide_tooltip())

    def show_tooltip(self, event, text, widget):
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.folder_entry.config(fg="black")

    def update_stats_label(self):
        self.stats_label.config(text=f"Thành công: {self.success_count} | Thất bại: {self.failed_count}")
        self.root.update()

    def clear_input_line(self):
        try:
            current_line = self.input_text.index(tk.INSERT).split('.')[0]
            self.input_text.delete(f"{current_line}.0", f"{current_line}.end")
            logging.info("Xóa dòng hiện tại trong ô nhập URL")
        except Exception as e:
            logging.error(f"Lỗi xóa dòng: {str(e)}")

    def clear_input_all(self):
        self.input_text.delete("1.0", tk.END)
        logging.info("Xóa toàn bộ ô nhập URL")

    def clear_status(self):
        self.status_text.delete("1.0", tk.END)
        logging.info("Xóa ô trạng thái")

    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.pause_button.config(text="Tạm dừng")
            logging.info("Tiếp tục tải")
            threading.Thread(target=self.run_async_download, args=(self.remaining_urls, self.save_folder, self.mode, self.max_concurrent), daemon=True).start()
        else:
            self.is_paused = True
            self.pause_event.clear()
            for task in self.current_tasks:
                task.cancel()
            self.current_tasks.clear()
            self.pause_button.config(text="Tiếp tục")
            self.status_text.insert(tk.END, "Đã tạm dừng tải.\n")
            self.status_text.see(tk.END)
            self.root.update()
            logging.info("Tạm dừng tải")

    def stop_download(self):
        self.is_downloading = False
        self.is_paused = False
        self.pause_event.set()
        for task in self.current_tasks:
            task.cancel()
        self.current_tasks.clear()
        self.remaining_urls.clear()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.status_text.insert(tk.END, "Đã dừng toàn bộ tải. Phiên kết thúc.\n")
        self.status_text.see(tk.END)
        self.root.update()
        logging.info("Dừng toàn bộ tải")

    def start_download(self):
        if self.is_downloading:
            messagebox.showerror("Lỗi", "Đang tải, vui lòng chờ hoàn tất hoặc dừng phiên hiện tại.")
            return

        input_text = self.input_text.get("1.0", tk.END).strip()
        save_folder = self.folder_entry.get().strip()
        mode = self.mode_var.get()
        concurrent_str = self.concurrent_entry.get().strip()

        if input_text == "https://www.tiktok.com/@abc/video/5314633447174692735":
            messagebox.showerror("Lỗi", "Vui lòng nhập link hoặc tên người dùng hợp lệ.")
            return

        if not input_text:
            messagebox.showerror("Lỗi", "Vui lòng nhập link hoặc tên người dùng.")
            return

        self.success_count = 0
        self.failed_count = 0
        self.failed_videos = []
        self.update_stats_label()

        if save_folder == "E:\\Videos" or not save_folder:
            base_path = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
            save_folder = os.path.join(base_path, 'Output')
            logging.info(f"Không chọn thư mục, sử dụng mặc định: {save_folder}")
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, save_folder)
            self.folder_entry.config(fg="black")
        else:
            save_folder = os.path.join(save_folder, 'Output')
            logging.info(f"Sử dụng thư mục lưu: {save_folder}")

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        try:
            max_concurrent = int(concurrent_str) if concurrent_str else 3
            if max_concurrent < 1 or max_concurrent > 10:
                raise ValueError("Số lượng tải đồng thời phải từ 1 đến 10")
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng tải đồng thời không hợp lệ. Sử dụng mặc định (3).")
            max_concurrent = 3

        urls = []
        video_ids_seen = set()
        for line in input_text.replace(";", ",").replace("\n", ",").split(","):
            line = line.strip()
            if line and line != "https://www.tiktok.com/@abc/video/5314633447174692735":
                normalized_url = self.downloader.standardize_url(line, mode)
                if normalized_url:
                    video_id = self.downloader.extract_video_id(normalized_url)
                    if video_id not in video_ids_seen:
                        video_ids_seen.add(video_id)
                        urls.append(normalized_url)
                    else:
                        logging.info(f"Loại bỏ link trùng lặp: {video_id}")

        if not urls:
            messagebox.showerror("Lỗi", "Không có link hợp lệ để tải.")
            return

        self.is_downloading = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.input_text.tag_add("clear_enabled", "1.0", tk.END)
        self.root.nametowidget(self.input_text.winfo_parent()).nametowidget("!button2").config(state=tk.NORMAL)  # Clear
        self.root.nametowidget(self.input_text.winfo_parent()).nametowidget("!button3").config(state=tk.NORMAL)  # Clear All

        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"Bắt đầu tải ({len(urls)} video)...\n")
        self.status_text.see(tk.END)
        self.root.update()

        if mode == "all" and len(urls) > 1:
            first_url = urls[0]
            response = messagebox.askyesno(
                "Cảnh báo",
                f"Chỉ sử dụng link đầu tiên để tải toàn bộ kênh: {first_url}\nBạn có muốn thay đổi link không?",
            )
            if response:
                new_url = simpledialog.askstring("Nhập link mới", "Nhập link kênh mới (@username hoặc URL đầy đủ):")
                if new_url:
                    new_url = self.downloader.standardize_url(new_url.strip(), mode)
                    if new_url:
                        urls = [new_url]
                        self.input_text.delete("1.0", tk.END)
                        self.input_text.insert("1.0", new_url)
                    else:
                        messagebox.showerror("Lỗi", "Link không hợp lệ, sử dụng link đầu tiên.")
                else:
                    messagebox.showerror("Lỗi", "Không có link mới, sử dụng link đầu tiên.")

        self.save_folder = save_folder
        self.mode = mode
        self.max_concurrent = max_concurrent
        threading.Thread(target=self.run_async_download, args=(urls, save_folder, mode, max_concurrent), daemon=True).start()

    def run_async_download(self, urls, save_folder, mode, max_concurrent):
        try:
            asyncio.run(self.download_videos(urls, save_folder, mode, max_concurrent))
        except Exception as e:
            self.status_text.insert(tk.END, f"Lỗi tổng thể: {str(e)}\n")
            logging.error(f"Lỗi tổng thể: {str(e)}")
        finally:
            if not self.is_paused:
                self.is_downloading = False
                self.start_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                self.status_text.insert(tk.END, "Hoàn tất tải.\n")
                if self.failed_videos:
                    self.status_text.insert(tk.END, "Video thất bại:\n")
                    for video_id in self.failed_videos:
                        self.status_text.insert(tk.END, f"- {video_id}\n")
                self.status_text.see(tk.END)
                self.root.update()
                logging.info("Kết thúc phiên tải")

    async def download_videos(self, urls, save_folder, mode, max_concurrent):
        self.remaining_urls = urls.copy()
        try:
            if mode == "single":
                for url in urls:
                    await self.pause_event.wait()
                    if not self.is_downloading:
                        break
                    self.status_text.insert(tk.END, f"Tải video: {self.downloader.extract_video_id(url)}\n")
                    self.status_text.see(tk.END)
                    self.root.update()
                    try:
                        await self.download_single(url, save_folder)
                        self.remaining_urls.remove(url)
                    except Exception as e:
                        video_id = self.downloader.extract_video_id(url)
                        self.failed_videos.append(video_id)
                        self.status_text.insert(tk.END, f"Lỗi video {video_id}: {str(e)}\n")
                        logging.error(f"Lỗi tải video {url}: {str(e)}")
                    self.status_text.see(tk.END)
                    self.root.update()
            elif mode == "multiple":
                await self.download_multiple(urls, save_folder, max_concurrent)
            else:  # all
                self.status_text.insert(tk.END, f"Lấy danh sách video từ kênh...\n")
                self.status_text.see(tk.END)
                self.root.update()
                username = self.downloader.extract_username_from_url(urls[0])
                videos = await self.downloader.get_user_videos(username)
                self.total_videos = len(videos)
                self.status_text.insert(tk.END, f"Tìm thấy {self.total_videos} video.\n")
                self.status_text.see(tk.END)
                self.root.update()
                video_urls = [f"https://www.tiktok.com/@{username}/video/{video_id}" for video_id, _ in videos]
                self.remaining_urls = video_urls.copy()
                await self.download_multiple(video_urls, save_folder, max_concurrent)
        except Exception as e:
            self.status_text.insert(tk.END, f"Lỗi: {str(e)}\n")
            logging.error(f"Lỗi: {str(e)}")

    async def download_single(self, url, save_folder):
        try:
            await self.pause_event.wait()
            if not self.is_downloading:
                raise asyncio.CancelledError("Tải bị hủy")
            username, video_id = self.downloader.extract_username_and_video_id(url)
            user_folder = os.path.join(save_folder, username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            file_path = os.path.join(user_folder, f"{video_id}.mp4")
            handle_partial_file(file_path)
            video_bytes = await self.downloader.download_video(url)
            with self.file_lock:
                if not os.path.exists(file_path):
                    with open(file_path, "wb") as f:
                        f.write(video_bytes)
            self.success_count += 1
            self.update_stats_label()
            self.status_text.insert(tk.END, f"Đã tải: {file_path} ({self.success_count}/{self.total_videos if self.mode == 'all' else len(self.remaining_urls)})\n")
            logging.info(f"Lưu video {video_id} thành công tại {file_path}")
        except Exception as e:
            self.failed_count += 1
            self.failed_videos.append(video_id)
            self.update_stats_label()
            logging.error(f"Lỗi lưu video {url}: {str(e)}")
            raise

    async def download_multiple(self, urls, save_folder, max_concurrent):
        for i in range(0, len(urls), max_concurrent):
            await self.pause_event.wait()
            if not self.is_downloading:
                break
            batch_urls = urls[i:i + max_concurrent]
            tasks = []
            semaphore = asyncio.Semaphore(max_concurrent)

            async def download_with_semaphore(url):
                async with semaphore:
                    try:
                        self.status_text.insert(tk.END, f"Tải video: {self.downloader.extract_video_id(url)}\n")
                        self.status_text.see(tk.END)
                        self.root.update()
                        await self.download_single(url, save_folder)
                        self.remaining_urls.remove(url)
                    except Exception as e:
                        video_id = self.downloader.extract_video_id(url)
                        self.status_text.insert(tk.END, f"Lỗi video {video_id}: {str(e)}\n")
                        logging.error(f"Lỗi tải video {url}: {str(e)}")
                    finally:
                        self.status_text.see(tk.END)
                        self.root.update()

            for url in batch_urls:
                task = asyncio.create_task(download_with_semaphore(url))
                self.current_tasks.append(task)
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)
            self.current_tasks.clear()

    def save_video(self, video_id, video_bytes, file_path):
        try:
            with self.file_lock:
                if not os.path.exists(file_path):
                    with open(file_path, "wb") as f:
                        f.write(video_bytes)
            self.success_count += 1
            self.update_stats_label()
            self.status_text.insert(tk.END, f"Đã tải: {file_path}\n")
            logging.info(f"Lưu video {video_id} thành công tại {file_path}")
        except Exception as e:
            self.failed_count += 1
            self.failed_videos.append(video_id)
            self.update_stats_label()
            logging.error(f"Lỗi lưu video {video_id}: {str(e)}")
            raise
        finally:
            self.status_text.see(tk.END)
            self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokDownloaderGUI(root)
    root.mainloop()
