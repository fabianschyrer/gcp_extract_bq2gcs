import logging
from datetime import datetime, timedelta
from typing import Union

import const


class Inputs:
    def __init__(self,
                 env: str,
                 profile: str,
                 gcs_path: str,
                 mode: str,
                 start_date: str,
                 end_date: str,
                 ):
        self.env = env
        self.profile = profile
        self.gcs_path = gcs_path
        self.mode = mode
        self.start_date = start_date
        self.end_date = end_date

    def set_default_date(self, now: datetime, timezone: int = 0):

        if self.start_date in (const.DATE_TODAY, const.DATE_YESTERDAY) and self.end_date in (const.DATE_TODAY, const.DATE_YESTERDAY):
            self.start_date = self.convert_datestr(now=now, datestr=self.start_date, timezone=timezone)
            self.end_date = self.convert_datestr(now=now, datestr=self.end_date, timezone=timezone)

        else:
            logging.info('running with specified "start_date" and "end_date".')
            self.start_date = datetime.strptime(self.start_date, const.INPUT_DATE_FORMAT)
            self.end_date = datetime.strptime(self.end_date, const.INPUT_DATE_FORMAT)

    def convert_datestr(self,now: datetime, datestr: str, timezone: int = 0) -> datetime:
        timezone = 0 if not timezone else timezone
        local = now + timedelta(hours=timezone)
        today = local.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        yesterday = today - timedelta(days=1)
        if datestr == const.DATE_TODAY:
            return today
        elif datestr == const.DATE_YESTERDAY:
            return yesterday
        else:
            raise ValueError("Date string not in correct format.")

