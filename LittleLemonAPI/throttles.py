from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class TenCallsPerMinute(UserRateThrottle):
    scope = 'ten'
    