import requests
import os
import logging
import asyncio

def extract_video_id_from_url(url, headers={}, proxy=None):
    url = requests.head(url=url, allow_redirects=True, headers=headers, proxies=proxy).url
    if "@" in url and "/video/" in url:
        return url.split("/video/")[1].split("?")[0]
    else:
        raise TypeError("Định dạng URL không được hỗ trợ.")

def retry_api(session, url, params=None, max_attempts=3, delay=2):
    """Thử lại API tối đa max_attempts lần nếu thất bại."""
    logger = logging.getLogger(__name__)
    for attempt in range(max_attempts):
        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Thử {attempt + 1} thất bại: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"API thất bại sau {max_attempts} lần thử: {str(e)}")
            asyncio.sleep(delay)

def handle_partial_file(file_path, min_size=1024):
    """Xóa file tải dở nếu kích thước nhỏ hơn min_size."""
    logger = logging.getLogger(__name__)
    if os.path.exists(file_path) and os.path.getsize(file_path) < min_size:
        try:
            os.remove(file_path)
            logger.info(f"Xóa file tải dở: {file_path}")
        except Exception as e:
            logger.error(f"Lỗi xóa file tải dở {file_path}: {str(e)}")

class TikTokException(Exception):
    def __init__(self, raw_response, message, error_code=None):
        self.error_code = error_code
        self.raw_response = raw_response
        self.message = message
        super().__init__(self.message)

class EmptyResponseException(TikTokException):
    pass

class InvalidJSONException(TikTokException):
    pass

class InvalidResponseException(TikTokException):
    pass
