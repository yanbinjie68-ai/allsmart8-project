#实现缓存机制
from functools import wraps
from datetime import datetime, timedelta
import json

class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.ttl = 300  # 5分钟
    
    def set(self, key, value):
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def get(self, key):
        if key in self.cache:
            item = self.cache[key]
            if (datetime.now() - item['timestamp']).total_seconds() < self.ttl:
                return item['value']
            else:
                del self.cache[key]
        return None
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

cache = SimpleCache()