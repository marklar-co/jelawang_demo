TRANSCRIPT = [
    "Alice: The reconnect flow is still flaky when the auth token expires during a websocket session.",
    "Bob: We saw something similar in the last regression cycle, but I don't think we had coverage for multi-tab refresh.",
    "4dw334g: Is that handled in the auth middleware or the websocket gateway?",
    "Alice: Mostly gateway, but the middleware owns token refresh. We should check existing Jira before opening another ticket.",
    "Alice: Bob missed the cache invalidation step last time, so let's make sure that doesn't happen again.",
    "Bob: We need a test case where the token expires during reconnect and another where Redis is briefly unavailable.",
    "Alice: Action item: add retry telemetry and confirm whether AUTH-231 already covers this.",
    "4dw334g: I can document the flow once someone points me to the right service.",
]
