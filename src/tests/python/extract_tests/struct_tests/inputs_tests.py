import logging
import unittest
from datetime import datetime
from unittest.mock import patch, Mock

from dp_extract.struct.inputs import Inputs


class TestInputs(unittest.TestCase):

    @patch.object(Inputs, Inputs.convert_datestr.__name__)
    @patch.object(logging, logging.info.__name__)
    def test_set_default_date(self, _logging_info: Mock, convert_datestr):
        inputs = Inputs(
            env='env',
            profile='profile',
            gcs_path='gcs_path',
            mode='mode',
            start_date='yesterday',
            end_date='today',
        )
        now = Mock
        convert_datestr.side_effect = [datetime(2018,4,30),datetime(2018,5,1)]
        inputs.set_default_date(now=now, timezone=7)

        _logging_info.assert_not_called()
        self.assertEqual(inputs.start_date, datetime(2018, 4, 30))
        self.assertEqual(inputs.end_date, datetime(2018, 5, 1))

    @patch.object(logging, logging.info.__name__)
    def test_set_default_date__not_set(self, _logging_info: Mock):
        inputs = Inputs(
            env='env',
            profile='profile',
            gcs_path='gcs_path',
            mode='mode',
            start_date='2018-08-01',
            end_date='2018-08-02',
        )
        expected_start_date = datetime(2018,8,1)
        expected_end_date = datetime(2018,8,2)
        inputs.start_date = '2018-08-01'
        inputs.end_date = '2018-08-02'

        inputs.set_default_date(now=datetime.utcnow(), timezone=7)

        _logging_info.assert_called_once()
        self.assertEqual(inputs.start_date, expected_start_date)
        self.assertEqual(inputs.end_date, expected_end_date)

    def test_convert_datestr(self):
        inputs = Inputs(
            env='env',
            profile='profile',
            gcs_path='gcs_path',
            mode='mode',
            start_date='today',
            end_date='yesterday',
        )
        now = datetime(2018,8,1)
        timezone = 0
        result_today = inputs.convert_datestr(now, 'today', timezone)
        result_yesterday = inputs.convert_datestr(now, 'yesterday', timezone)
        self.assertEqual(result_today, datetime(2018,8,1))
        self.assertEqual(result_yesterday, datetime(2018,7,31))
