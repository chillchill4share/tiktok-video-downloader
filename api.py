import asyncio
import requests
from logic import extract_video_id_from_url, EmptyResponseException, InvalidJSONException, retry_api
import logging
import re
import json

class TikTokDownloader:
    COOKIES = {
        "sessionid": "your_session_id_here",
        "ttwid": "your_ttwid_here"
    }

    def __init__(self):
        self.session = None
        self.configure_logging()
        self.initialize_session()

    def configure_logging(self):
        self.logger = logging.getLogger(__name__)

    def initialize_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Accept": "video/mp4,video/webm,video/ogg,text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.tiktok.com/",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "video",
            "Connection": "keep-alive",
        })
        self.session.cookies.update(self.COOKIES)
        self.logger.info("Khởi tạo session với cookies thành công")

    def standardize_url(self, url, mode):
        url = url.replace('\n', '').replace('%0A', '').strip()
        if not url:
            return None
        if mode in ["single", "multiple"]:
            if "tiktok.com" in url:
                try:
                    video_id = extract_video_id_from_url(url, headers=self.session.headers)
                    username = url.split("/@")[1].split("/")[0]
                    return f"https://www.tiktok.com/@{username}/video/{video_id}"
                except Exception:
                    self.logger.warning(f"Không thể chuẩn hóa URL video: {url}")
                    return None
            elif url.isdigit():
                return f"https://www.tiktok.com/@someone/video/{url}"
            else:
                self.logger.warning(f"URL video không hợp lệ: {url}")
                return None
        else:
            if "tiktok.com" in url:
                try:
                    username = url.split("/@")[1].split("/")[0].split("?")[0]
                    return f"https://www.tiktok.com/@{username}"
                except Exception:
                    self.logger.warning(f"Không thể chuẩn hóa URL kênh: {url}")
                    return None
            elif url.startswith("@"):
                return f"https://www.tiktok.com/{url}"
            else:
                self.logger.warning(f"URL kênh không hợp lệ: {url}")
                return None

    def extract_username_and_video_id(self, url_or_id):
        url_or_id = url_or_id.replace('\n', '').replace('%0A', '').strip()
        if "tiktok.com" in url_or_id and "/video/" in url_or_id:
            clean_url = url_or_id.split("?")[0]
            try:
                video_id = extract_video_id_from_url(clean_url, headers=self.session.headers)
                username = clean_url.split("/@")[1].split("/")[0]
                return username, video_id
            except Exception as e:
                self.logger.error(f"Lỗi trích xuất video ID từ {clean_url}: {str(e)}")
                return "unknown", url_or_id
        return "unknown", url_or_id

    def extract_video_id(self, url_or_id):
        url_or_id = url_or_id.replace('\n', '').replace('%0A', '').strip()
        if "tiktok.com" in url_or_id and "/video/" in url_or_id:
            clean_url = url_or_id.split("?")[0]
            try:
                video_id = extract_video_id_from_url(clean_url, headers=self.session.headers)
                return video_id
            except Exception as e:
                self.logger.error(f"Lỗi trích xuất video ID từ {clean_url}: {str(e)}")
                return url_or_id
        return url_or_id

    def extract_username_from_url(self, url):
        url = url.replace('\n', '').replace('%0A', '').strip()
        if "tiktok.com" in url:
            try:
                username = url.split("/@")[1].split("/")[0].split("?")[0]
                return username
            except Exception:
                self.logger.error(f"Lỗi trích xuất username từ {url}")
                return "unknown"
        elif url.startswith("@"):
            return url.lstrip("@")
        return url

    async def download_video(self, url_or_id):
        video_id = self.extract_video_id(url_or_id)
        self.logger.info(f"Bắt đầu tải video {video_id}")
        if "tiktok.com" in url_or_id:
            self.session.get(url_or_id)
        video_info = await self.get_video_info(url_or_id)
        download_addr = video_info["video"].get("playAddr", video_info["video"]["downloadAddr"])
        self.logger.info(f"Tải từ nguồn video {video_id}")
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.session.get(download_addr, stream=True, timeout=30)
                response.raise_for_status()
                video_bytes = bytearray()
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        video_bytes.extend(chunk)
                if len(video_bytes) < 1024:
                    self.logger.error(f"Thử {attempt + 1}: Video {video_id} quá nhỏ, kích thước={len(video_bytes)} bytes")
                    raise Exception(f"Kích thước video quá nhỏ: {len(video_bytes)} bytes")
                self.logger.info(f"Tải video {video_id} thành công, kích thước={len(video_bytes)} bytes")
                return bytes(video_bytes)
            except requests.RequestException as e:
                self.logger.error(f"Thử {attempt + 1} thất bại: Lỗi HTTP {e}")
                if attempt == max_attempts - 1:
                    raise Exception(f"Tải video {video_id} thất bại sau {max_attempts} lần thử")
                await asyncio.sleep(2)

    async def get_video_info(self, url_or_id):
        url_or_id = url_or_id.replace('\n', '').replace('%0A', '').strip()
        if "tiktok.com" not in url_or_id:
            url = f"https://www.tiktok.com/@someone/video/{url_or_id}"
        else:
            url = url_or_id.split("?")[0]
        self.logger.info(f"Lấy thông tin video {self.extract_video_id(url)}")
        r = self.session.get(url)
        if r.status_code != 200:
            self.logger.error(f"Lấy thông tin video thất bại: mã trạng thái={r.status_code}, URL={url}")
            raise Exception(f"Lấy thông tin video thất bại: mã trạng thái={r.status_code}")
        start = r.text.find('<script id="SIGI_STATE" type="application/json">')
        if start != -1:
            start += len('<script id="SIGI_STATE" type="application/json">')
            end = r.text.find("</script>", start)
            data = json.loads(r.text[start:end])
            video_info = data["ItemModule"][self.extract_video_id(url)]
        else:
            start = r.text.find('<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">')
            start += len('<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">')
            end = r.text.find("</script>", start)
            data = json.loads(r.text[start:end])
            video_info = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
        self.logger.info(f"Lấy thông tin video {self.extract_video_id(url)} thành công")
        return video_info

    async def get_user_videos(self, username):
        self.logger.info(f"Lấy danh sách video của {username}")
        url = f"https://www.tiktok.com/@{username}"
        r = self.session.get(url)
        if r.status_code != 200:
            self.logger.error(f"Lấy trang người dùng thất bại: mã trạng thái={r.status_code}, username={username}")
            raise Exception(f"Lấy trang người dùng thất bại: mã trạng thái={r.status_code}")
        start = r.text.find('<script id="SIGI_STATE" type="application/json">')
        if start != -1:
            start += len('<script id="SIGI_STATE" type="application/json">')
            end = r.text.find("</script>", start)
            data = json.loads(r.text[start:end])
            sec_uid = data["UserModule"]["users"][username]["secUid"]
        else:
            start = r.text.find('<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">')
            start += len('<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">')
            end = r.text.find("</script>", start)
            data = json.loads(r.text[start:end])
            sec_uid = data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["user"]["secUid"]

        videos = []
        cursor = 0
        while True:
            params = {"secUid": sec_uid, "count": 35, "cursor": cursor}
            r = retry_api(self.session, "https://www.tiktok.com/api/post/item_list/", params=params)
            data = r.json()
            for video in data.get("itemList", []):
                video_id = video["id"]
                download_addr = video["video"].get("playAddr", video["video"]["downloadAddr"])
                videos.append((video_id, download_addr))
            if not data.get("hasMore", False):
                break
            cursor = data.get("cursor")
        self.logger.info(f"Tìm thấy {len(videos)} video từ {username}")
        return videos
