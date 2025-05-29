from datetime import datetime, timezone, timedelta


class TimeInterval:

    def __init__(self):
        self.utc_now = datetime.now(timezone.utc)

    @property
    def start_str(self):
        utc_now_str = self.utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        return utc_now_str
    
    @property
    def end_str(self):
        four_weeks_future = self.utc_now + timedelta(days=4*7)
        future_str = four_weeks_future.strftime("%Y-%m-%dT%H:%M:%SZ")
        return future_str




