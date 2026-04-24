import redis
import json
import logging
from typing import List, Dict, Optional

class LongTermMemory:
    """
    Long-term memory using Redis with a local in-memory fallback if Redis is unavailable.
    """
    def __init__(self, host='localhost', port=6379, db=0):
        self.use_fallback = False
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.client.ping() # Check connection
            print("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError:
            print("WARNING: Redis not found at localhost:6379. Using In-Memory Fallback.")
            self.use_fallback = True
            self.fallback_storage = {
                "prefs": {},
                "facts": {},
                "sessions": {}
            }

        # TTLs in seconds
        self.TTL_PREFS = 90 * 24 * 60 * 60  # 90 days
        self.TTL_FACTS = 30 * 24 * 60 * 60  # 30 days
        self.TTL_SESSIONS = 7 * 24 * 60 * 60 # 7 days

    def set_user_preference(self, user_id: str, key: str, value: str):
        if self.use_fallback:
            if user_id not in self.fallback_storage["prefs"]:
                self.fallback_storage["prefs"][user_id] = {}
            self.fallback_storage["prefs"][user_id][key] = value
            return

        hash_key = f"user:{user_id}:prefs"
        self.client.hset(hash_key, key, value)
        self.client.expire(hash_key, self.TTL_PREFS)

    def get_user_preferences(self, user_id: str) -> Dict[str, str]:
        if self.use_fallback:
            return self.fallback_storage["prefs"].get(user_id, {})
        return self.client.hgetall(f"user:{user_id}:prefs")

    def add_user_fact(self, user_id: str, fact: str):
        if self.use_fallback:
            if user_id not in self.fallback_storage["facts"]:
                self.fallback_storage["facts"][user_id] = set()
            self.fallback_storage["facts"][user_id].add(fact)
            return

        set_key = f"user:{user_id}:facts"
        self.client.sadd(set_key, fact)
        self.client.expire(set_key, self.TTL_FACTS)

    def get_user_facts(self, user_id: str) -> List[str]:
        if self.use_fallback:
            return list(self.fallback_storage["facts"].get(user_id, []))
        return list(self.client.smembers(f"user:{user_id}:facts"))

    def add_session(self, user_id: str, session_data: Dict):
        if self.use_fallback:
            if user_id not in self.fallback_storage["sessions"]:
                self.fallback_storage["sessions"][user_id] = []
            self.fallback_storage["sessions"][user_id].insert(0, session_data)
            self.fallback_storage["sessions"][user_id] = self.fallback_storage["sessions"][user_id][:10]
            return

        list_key = f"user:{user_id}:sessions"
        self.client.lpush(list_key, json.dumps(session_data))
        self.client.ltrim(list_key, 0, 9)
        self.client.expire(list_key, self.TTL_SESSIONS)

    def get_recent_sessions(self, user_id: str) -> List[Dict]:
        if self.use_fallback:
            return self.fallback_storage["sessions"].get(user_id, [])
        sessions = self.client.lrange(f"user:{user_id}:sessions", 0, -1)
        return [json.loads(s) for s in sessions]
