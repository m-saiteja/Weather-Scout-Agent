import time
from collections import deque

class SlidingWindowRateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    Tracks timestamps of requests per user or session thread.
    """

    def __init__(
                self,
                max_requests: int=5,
                window_seconds: int=60,
                min_cooldown: float=2.0
            ):
        self.max_requests=max_requests
        self.window_seconds=window_seconds
        self.min_cooldown=min_cooldown
        # maps session_id to deque of timestamps
        self.history: dict[str, deque] = {}
        
    def check_limit(self, session_id: str) -> tuple[bool, float]:
        """
        Check if session is rate-limited.
        Returns (is_allowedm wait_seconds).
        """
        now = time.time()
        if session_id not in self.history:
            self.history[session_id] = deque()

        timestamps = self.history[session_id]

        # cooldown check
        if timestamps and (now - timestamps[-1]) < self.min_cooldown:
            wait = self.min_cooldown - (now - timestamps[-1])
            return False, round(wait, 1)

        # Slide window: remove timestamps older than window_seconds
        while timestamps and timestamps[0] <= (now - self.window_seconds):
            timestamps.popleft()

        # check if limit exceeded
        if len(timestamps) >= self.max_requests:
            oldest = timestamps[0]
            wait = self.window_seconds - (now - oldest)
            return False, round(wait,1)

        # allow request
        timestamps.append(now)
        return True, 0.0         