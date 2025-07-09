from datetime import datetime, timezone, timedelta


class TimeInterval:

    def __init__(self):
        """
        Initialise with the current UTC time
        """
        self.utc_now = datetime.now(timezone.utc)

    @property
    def start_str(self):
        """
        Return the ISO formatted start timestamp.
        """
        utc_now_str = self.utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        return utc_now_str
    
    @property
    def end_str(self):
        """
        Return an ISO timestamp around four weeks in the future
        """
        four_weeks_future = self.utc_now + timedelta(days=4*7)
        # make sure the end time is Tuesday, Wednesday or Thursday
        day_of_week = four_weeks_future.isoweekday()
        if day_of_week == 1: 
            # Monday
            four_weeks_future += timedelta(days=1) # Tuesday
        if day_of_week == 5:
            # Friday
            four_weeks_future += timedelta(days=4) # next Tuesday
        if day_of_week == 6:
            # Saturday 
            four_weeks_future += timedelta(days=3) # next Tuesday
        if day_of_week == 7:
            # Sunday
            four_weeks_future += timedelta(days=2) # next Tuesday
        future_str = four_weeks_future.strftime("%Y-%m-%dT%H:%M:%SZ")
        return future_str




