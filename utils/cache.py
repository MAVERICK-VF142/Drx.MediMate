from cachetools import TTLCache
import threading

# A cache with maxsize 100 items, and TTL of 600 seconds (10 minutes)
drug_cache = TTLCache(maxsize=100, ttl=600)

# Lock to prevent race conditions in threaded environments (e.g., Flask)
cache_lock = threading.Lock()

def get_cached_drug(drug_name):
    key = drug_name.strip().lower()
    with cache_lock:
        return drug_cache.get(key)

def set_cached_drug(drug_name, response):
    key = drug_name.strip().lower()
    with cache_lock:
        drug_cache[key] = response
