# TikTok Video Downloader

A Python-based GUI application for downloading TikTok videos using Tkinter. This tool allows users to download single videos, multiple videos, or (optionally) all videos from a TikTok channel.

---

## Tải Video TikTok

Ứng dụng giao diện người dùng (GUI) được viết bằng Python, sử dụng Tkinter, giúp tải video TikTok. Công cụ này hỗ trợ tải video đơn, nhiều video hoặc (tùy chọn) toàn bộ video từ một kênh TikTok.

---

## Features / Tính năng

### English
- **User-friendly GUI**: Built with Tkinter for easy interaction.
- **Download modes**:
  - Single video: Download one video by providing its URL.
  - Multiple videos: Download several videos concurrently (up to 10 at a time).
  - All videos from a channel: Download all videos from a specified TikTok user (disabled by default).
- **Concurrent downloads**: Supports downloading multiple videos simultaneously with a configurable limit.
- **Pause/Resume**: Pause and resume downloads at any time.
- **Error handling**: Logs errors and failed downloads to a `download.log` file.
- **Custom save location**: Choose where to save downloaded videos.

### Tiếng Việt
- **Giao diện thân thiện**: Sử dụng Tkinter, dễ dàng thao tác.
- **Chế độ tải**:
  - Video đơn: Tải một video bằng cách nhập URL.
  - Nhiều video: Tải đồng thời nhiều video (tối đa 10 video cùng lúc).
  - Tất cả video từ kênh: Tải toàn bộ video từ một người dùng TikTok (mặc định bị vô hiệu hóa).
- **Tải đồng thời**: Hỗ trợ tải nhiều video cùng lúc với giới hạn có thể tùy chỉnh.
- **Tạm dừng/Tiếp tục**: Tạm dừng và tiếp tục quá trình tải bất kỳ lúc nào.
- **Xử lý lỗi**: Ghi lại lỗi và các video tải thất bại vào file `download.log`.
- **Tùy chỉnh thư mục lưu**: Chọn thư mục để lưu video tải về.

---

## Requirements / Yêu cầu

### English
- Python 3.8 or higher
- Required Python libraries:
  - `tkinter` (usually included with Python)
  - `requests`
  - `asyncio`

### Tiếng Việt
- Python 3.8 trở lên
- Các thư viện Python cần thiết:
  - `tkinter` (thường đi kèm với Python)
  - `requests`
  - `asyncio`

---

## Installation / Cài đặt

### English
1. Clone the repository:
   ```bash
   git clone https://github.com/chillchill4share/tiktok-video-downloader
   cd tiktok-video-downloader
   ```
2. Install required libraries:
   ```bash
   pip install requests
   ```
3. (Optional) Ensure Tkinter is available. On some systems, you may need to install it:
   - Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-tk
     ```
   - Windows: Tkinter is included with Python by default.

### Tiếng Việt
1. Tải repository:
   ```bash
   git clone https://github.com/chillchill4share/tiktok-video-downloader
   cd tiktok-video-downloader
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install requests
   ```
3. (Tùy chọn) Đảm bảo Tkinter đã được cài đặt. Trên một số hệ thống, bạn có thể cần cài đặt:
   - Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-tk
     ```
   - Windows: Tkinter thường đi kèm với Python.

---

## Usage / Cách sử dụng

### English
1. Update TikTok cookies:
   - Open `api.py` and replace `your_session_id_here` and `your_ttwid_here` in the `COOKIES` dictionary with valid TikTok cookies.
   - Cookies are needed in cases where TikTok requires login to view the video.
   - You can obtain cookies by logging into TikTok in a browser and using the browser's developer tools (F12 → Network tab).
2. Run the application:
   ```bash
   python gui.py
   ```
3. In the GUI:
   - **Folder**: Choose where to save videos (default: `Output` folder in the project directory).
   - **Video/User Links**: Enter video URLs or usernames, separated by commas, semicolons, or new lines.
   - **Concurrent Downloads**: Set the number of videos to download simultaneously (1-10, default: 3).
   - **Mode**: Select "Single video" or "Multiple videos". (Channel download is disabled by default.)
   - Click **Start** to begin downloading.
4. Check the `download.log` file for logs and error details.

### Tiếng Việt
1. Cập nhật cookies TikTok:
   - Mở file `api.py` và thay thế `your_session_id_here` và `your_ttwid_here` trong dictionary `COOKIES` bằng cookies TikTok hợp lệ.
   - Cần sử dụng cookies trong trường hợp tiktok yêu cầu đăng nhập để xem video
   - Bạn có thể lấy cookies bằng cách đăng nhập TikTok trên trình duyệt và sử dụng công cụ phát triển (F12 → tab Network).
2. Chạy ứng dụng:
   ```bash
   python gui.py
   ```
3. Trong giao diện:
   - **Thư mục lưu**: Chọn nơi lưu video (mặc định: thư mục `Output` trong thư mục dự án).
   - **Link video/user**: Nhập URL video hoặc tên người dùng, phân tách bằng dấu phẩy, chấm phẩy hoặc xuống dòng.
   - **Tải đồng thời**: Đặt số lượng video tải cùng lúc (1-10, mặc định: 3).
   - **Chế độ**: Chọn "Video đơn" hoặc "Nhiều video". (Tải toàn bộ kênh bị vô hiệu hóa mặc định.)
   - Nhấn **Bắt đầu tải** để bắt đầu.
4. Kiểm tra file `download.log` để xem chi tiết log và lỗi.

---

## Project Structure / Cấu trúc dự án

```
tiktok-video-downloader/
│
├── gui.py              # Main GUI application
├── api.py              # TikTok API interaction logic
├── logic.py            # Utility functions for URL processing and error handling
├── download.log        # Log file for download activities (generated after running)
├── Output/             # Default folder for downloaded videos
├── icon.ico            # (Optional) Icon file for the GUI
└── README.md           # Project documentation
```

---

## Notes / Lưu ý

### English
- **Cookies**: TikTok cookies (`sessionid` and `ttwid`) must be valid. Update them regularly as they may expire.
- **Channel Download**: The "All videos from channel" mode is disabled by default in the GUI. To enable it, modify `gui.py` by removing `state=tk.DISABLED` from the corresponding radiobutton.
- **Error Handling**: Check `download.log` for detailed error messages if downloads fail.
- **Dependencies**: Ensure all required libraries are installed to avoid runtime errors.

### Tiếng Việt
- **Cookies**: Cookies TikTok (`sessionid` và `ttwid`) phải hợp lệ. Cập nhật thường xuyên vì chúng có thể hết hạn.
- **Tải toàn bộ kênh**: Chế độ "Tất cả video từ kênh" bị vô hiệu hóa mặc định trong GUI. Để kích hoạt, sửa `gui.py` bằng cách xóa `state=tk.DISABLED` khỏi radiobutton tương ứng.
- **Xử lý lỗi**: Kiểm tra file `download.log` để xem thông báo lỗi chi tiết nếu tải thất bại.
- **Thư viện**: Đảm bảo cài đặt tất cả thư viện cần thiết để tránh lỗi khi chạy.

---

## Contributing / Đóng góp

### English
Contributions are welcome! Please:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

### Tiếng Việt
Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:
1. Fork repository.
2. Tạo nhánh mới (`git checkout -b feature/tính-năng-của-bạn`).
3. Commit thay đổi (`git commit -m 'Thêm tính năng của bạn'`).
4. Push lên nhánh (`git push origin feature/tính-năng-của-bạn`).
5. Tạo Pull Request.

---

## License / Giấy phép

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Dự án này được cấp phép theo Giấy phép MIT. Xem file [LICENSE](LICENSE) để biết chi tiết.

---

## Contact / Liên hệ

For questions or support, please open an issue on GitHub.

Nếu có câu hỏi hoặc cần hỗ trợ, vui lòng mở một issue trên GitHub.

## Acknowledgments / Lời cảm ơn

### English
A special thanks to the following authors for their inspiring work, which helped shape this project:
- [Isaac Kogan](https://github.com/isaackogan) for the [TikTokLive](https://github.com/isaackogan/TikTokLive) library, a powerful tool for interacting with TikTok LIVE events.
- [David Teather](https://github.com/davidteather) for the [TikTok-Api](https://github.com/davidteather/TikTok-Api), an excellent unofficial API wrapper for TikTok.

### Tiếng Việt
Lời cảm ơn đặc biệt đến các tác giả sau vì những công trình truyền cảm hứng, đã góp phần định hình dự án này:
- [Isaac Kogan](https://github.com/isaackogan) với thư viện [TikTokLive](https://github.com/isaackogan/TikTokLive), một công cụ mạnh mẽ để tương tác với các sự kiện TikTok LIVE.
- [David Teather](https://github.com/davidteather) với [TikTok-Api](https://github.com/davidteather/TikTok-Api), một wrapper API không chính thức tuyệt vời cho TikTok.

## Download Executable / Tải file thực thi

### English
Download the Windows executable from the [Releases](https://github.com/chillchill4share/tiktok-video-downloader/releases) page.

### Tiếng Việt
Tải file thực thi cho Windows từ trang [Releases](https://github.com/chillchill4share/tiktok-video-downloader/releases).