import pytest
from unittest.mock import patch
from src.rate_limiter import SlidingWindowRateLimiter

pytestmark = pytest.mark.unit


def test_allows_initial_request():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60, min_cooldown=2.0)
    allowed, wait = limiter.check_limit("session_1")
    assert allowed is True
    assert wait == 0.0


def test_enforces_cooldown_between_rapid_requests():
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60, min_cooldown=2.0)
    
    with patch("time.time") as mock_time:
        # First request at t = 100.0
        mock_time.return_value = 100.0
        allowed, _ = limiter.check_limit("session_1")
        assert allowed is True

        # Second request 1 second later (violates 2.0s cooldown)
        mock_time.return_value = 101.0
        allowed, wait = limiter.check_limit("session_1")
        assert allowed is False
        assert wait == 1.0


def test_blocks_after_exceeding_max_requests():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60, min_cooldown=0.0)

    with patch("time.time") as mock_time:
        mock_time.return_value = 100.0
        assert limiter.check_limit("session_1")[0] is True
        
        mock_time.return_value = 105.0
        assert limiter.check_limit("session_1")[0] is True

        # 3rd request inside the 60s window exceeds limit
        mock_time.return_value = 110.0
        allowed, wait = limiter.check_limit("session_1")
        assert allowed is False
        assert wait == 50.0


def test_slides_window_and_recovers_capacity():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60, min_cooldown=0.0)

    with patch("time.time") as mock_time:
        mock_time.return_value = 100.0
        limiter.check_limit("session_1")
        
        mock_time.return_value = 105.0
        limiter.check_limit("session_1")

        # Advance past 60s window (t = 161.0) -> Oldest timestamp expires
        mock_time.return_value = 161.0
        allowed, wait = limiter.check_limit("session_1")
        assert allowed is True
        assert wait == 0.0


def test_isolates_different_sessions():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=60, min_cooldown=0.0)

    with patch("time.time") as mock_time:
        mock_time.return_value = 100.0
        assert limiter.check_limit("user_alice")[0] is True
        assert limiter.check_limit("user_bob")[0] is True
