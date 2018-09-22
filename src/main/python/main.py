import logging
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
import yaml

import const
from extract.extract_to_gcs import ExtractToGcs
from extract.struct.inputs import Inputs
from extract.struct.profile_config import ProfileConfig


def read_args(parser_args: ArgumentParser) -> Namespace:
    required = parser_args.add_argument_group('required arguments')
    required.add_argument('-env', '--environment',
                          help='Environment to run job')
    required.add_argument('-profile', '--profile',
                          help='Profile of job to get config from (.yaml)')
    required.add_argument('-gcs', '--gcs_path',
                          help='specific gcs destination bucket name. ')
    required.add_argument('-mode', '--mode',
                          help='Running mode : daily[default], monthly ')

    optional = parser_args.add_argument_group('optional arguments')
    optional.add_argument('-sdate', '--start_date',
                          default=const.START_YESTERDAY,
                          help='start datetime format: YYYY-mm-dd')
    optional.add_argument('-edate', '--end_date',
                          default=const.END_TODAY,
                          help='end datetime format: YYYY-mm-dd')

    return parser_args.parse_args()


def load_profile(table_name: str, project_name: str):
    profile_path = os.path.join(const.PROFILE_DIR, project_name, table_name + '.yaml')
    with open(profile_path, 'rb') as profile:
        table_info = yaml.load(profile)
        return table_info


def validate_args(parser_args: ArgumentParser, args) -> Inputs:
    environment = args.environment
    profile = args.profile
    gcs_path = args.gcs_path
    mode = args.mode

    start_date = args.start_date
    end_date = args.end_date

    #todo improve handle parameter in format Y-m-d HH:MM:SS
    if not start_date and not end_date:
        start_date = const.DATE_YESTERDAY
        end_date = const.DATE_TODAY
    # if (start_date == const.DATE_TODAY or const.DATE_YESTERDAY)\
    # #         and end_date == const.DATE_TODAY or const.DATE_YESTERDAY:
    # if (start_date and end_date) == (const.DATE_TODAY or const.DATE_YESTERDAY):
    #     start_date = None
    #     end_date = None
    #     pass
    #     # convert to datetime after get the timezone from profile ".yaml"
    #
    # else:
    #     start_date = datetime.strptime(args.start_date, const.INPUT_DATE_FORMAT)
    #     end_date = datetime.strptime(args.end_date, const.INPUT_DATE_FORMAT)

    if not mode or mode.upper() not in const.Mode.__dict__:
        parser_args.print_help()
        raise AttributeError('Please input mode in "daily" or "monthly"')

    inputs = Inputs(
        env=environment,
        profile=profile,
        gcs_path=gcs_path,
        mode=mode,
        start_date=start_date,
        end_date=end_date,
    )

    return inputs


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)-7s - %(message)s'
    )

    parser = ArgumentParser()
    args = read_args(parser)
    inputs = validate_args(parser, args)

    profile_config = ProfileConfig()
    profile_config.load_config(env=inputs.env, profile=inputs.profile)
    inputs.set_default_date(now=datetime.utcnow(), timezone=profile_config.timezone)
    logging.info('start_date: {}'.format(inputs.start_date))
    logging.info('end_date: {}'.format(inputs.end_date))

    with ExtractToGcs(inputs=inputs, profile=profile_config) as runner:
        runner.extract()