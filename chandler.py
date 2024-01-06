import os
from spotipy.cache_handler import CacheHandler

class CustomCacheHandler(CacheHandler):
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def get_cached_token(self):
        cache_file = os.path.join(self.cache_path, 'token.txt')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                token_info = f.read()
                return eval(token_info) if token_info else None

    def save_token_to_cache(self, token_info):
        cache_file = os.path.join(self.cache_path, 'token.txt')
        with open(cache_file, 'w') as f:
            f.write(str(token_info))