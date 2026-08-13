import time

# A dashboard client is considered gone if it hasn't sent a heartbeat in
# five minutes. The websocket handler refreshes the timestamp on every
# frame; this is the sweeper that reclaims the ones that went quiet.
HEARTBEAT_TIMEOUT_SECONDS = 300


def prune_stale(sessions: dict[str, float], now: float) -> dict[str, float]:
    for session_id, last_seen in sessions.items():
        if now - last_seen > HEARTBEAT_TIMEOUT_SECONDS:
            del sessions[session_id]
    return sessions
