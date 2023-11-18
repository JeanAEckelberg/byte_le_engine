import requests
import json
import urllib3
import os
from datetime import datetime, timezone, tzinfo


class ClientUtils:
    def __init__(self, csv_bool: bool) -> None:
        urllib3.disable_warnings()
        self.IP = 'http://134.129.91.211:8000/api/'
        self.PORT = 8000
        self.path_to_public = False
        self.use_csv: bool = csv_bool
        self.tournaments: list = []

    # convert utc to local time
    def convert_utc_to_local(self, utc_str: str = '2000-10-31T06:30:00Z') -> datetime:
        a: datetime = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%SZ')
        tz: tzinfo = datetime.now().astimezone().tzinfo
        a = a.replace(tzinfo=timezone.utc)

        return a.astimezone(tz)

    # get team types
    def get_team_types(self) -> dict:
        resp = requests.get(self.IP + 'team_types/',
                            verify=self.path_to_public)
        resp.raise_for_status()
        return json.loads(resp.content)

    # get unis
    def get_unis(self) -> dict:
        resp = requests.get(self.IP + 'universities/', verify=self.path_to_public)
        resp.raise_for_status()
        return json.loads(resp.content)

    # post get score over time - fix later
    def get_score_over_time(self, vid, group_run_id, team_uuid):
        resp = requests.post(
            self.IP + 'get_score_over_time', json={'vid': vid}, verify=self.path_to_public)
        resp.raise_for_status()
        jsn = json.loads(resp.content)
        print('The following is your team\'s performance in each group run')
        self.print_table(jsn)

    # post submission
    def submit_file(self, fil: bytes, vid: str) -> dict:
        data = {'submission_id': 0, 'submission_time': datetime.now(), 'file_txt': fil, 'team_uuid': vid}
        resp = requests.post(
            self.IP + 'submission', json=data, verify=self.path_to_public)
        resp.raise_for_status()
        return json.loads(resp.content)

    # gets the runs from a INDIVIDUAL get_submission
    def get_submission(self, subid: int, vid: str) -> None:
        resp = requests.get(
            self.IP + f'submission?submission_id={subid}&team_uuid={vid}', verify=self.path_to_public)
        resp.raise_for_status()
        jsn = json.loads(resp.content)
        jsn['submission_time'] = self.convert_utc_to_local(utc_str=jsn['submission_time']).strftime(
            '%m/%d/%Y, %H:%M:%S')
        self.print_table(jsn)

    # MULTIPLE get_submissions
    def get_submissions(self, vid: str) -> None:
        resp = requests.get(
            self.IP + f'submissions/{vid}', verify=self.path_to_public)
        resp.raise_for_status()
        jsn = json.loads(resp.content)
        jsn['submission_time'] = self.convert_utc_to_local(utc_str=jsn['submission_time']).strftime(
            '%m/%d/%Y, %H:%M:%S')
        self.print_table(jsn)

    # post team
    def register(self, uni_id: int, team_type_id: int, team_name: str) -> dict:
        data = {'uni_id': uni_id, 'team_type_id': team_type_id, 'team_name': team_name}
        resp = requests.post(
            self.IP + 'team', json=data, verify=self.path_to_public)
        resp.raise_for_status()
        return json.loads(resp.content)

    # get all runs
    def get_runs(self) -> dict:
        resp = requests.get(self.IP + f'run/', verify=self.path_to_public)
        resp.raise_for_status()
        return json.loads(resp.content)

    # get runs that match a tournament id and a team uuid
    def get_runs_filter(self, tournament_id: int, vid: str) -> None:
        resp = requests.get(self.IP + f'get_run?tournament_id={tournament_id}&team_uuid={vid}',
                            verify=self.path_to_public)
        resp.raise_for_status()
        jsn = json.loads(resp.content)
        jsn['run_time'] = self.convert_utc_to_local(utc_str=jsn['run_time']).strftime('%m/%d/%Y, %H:%M:%S')
        self.print_table(jsn)

    def get_code_from_submission(self, submission_id, vid):
        self.get_submission(submission_id, vid)

    # Building a comma-separated-values list table or ascii table based on passed in data below
    # The tables are used to build the leaderboard

    # helper method to format the csv or ascii table
    def get_longest_cell_in_cols(self, json, json_atribs):
        col_longest_length = {}
        for key in json_atribs:
            col_longest_length[key] = (len(key))
        for col in json_atribs:
            for row in json:
                if len(str(row[col])) > col_longest_length[col]:
                    col_longest_length[col] = len(str(row[col]))
        return col_longest_length

    # creates a line that separates rows of information in the table
    def get_seperator_line(self, col_longest_length, padding):
        rtn = ''
        for key in col_longest_length:
            rtn += '+' + ('-' * (col_longest_length[key] + padding))
        return rtn + '+'

    # prints table based on passed bool on instantiation
    def print_table(self, json):
        if self.use_csv:
            self.print_csv_table(json)
        else:
            self.print_ascii_table(json)

    # prints the csv table
    def print_csv_table(self, json):
        try:
            padding = 4
            json_atribs = json[0].keys()
            output = ''
            for index, key in enumerate(json_atribs):
                output += key
                if index != len(json_atribs) - 1:
                    output += ','
            output += '\n'
            for row in json:
                for index, col in enumerate(row):
                    if isinstance(row[col], int) or isinstance(row[col], float):
                        output += str(row[col])
                    else:
                        output += '"' + str(row[col]) + '"'
                    if index != len(row) - 1:
                        output += ','
                output += '\n'
            print(output)
        except BaseException as e:
            print(e)
            print(
                "Something went wrong. Maybe there isn't data for what you're looking for")

    # prints the ascii table
    def print_ascii_table(self, json):
        try:
            padding = 4
            json_atribs = json[0].keys()
            col_longest_length = self.get_longest_cell_in_cols(
                json, json_atribs)
            line_seperator = self.get_seperator_line(
                col_longest_length, padding)
            row_format = ''
            for key in json_atribs:
                row_format += "|{:^" + \
                              str(col_longest_length[key] + padding) + '}'
            row_format += '|'
            print(line_seperator)
            print(row_format.format(*json_atribs))
            for row in json:
                print(line_seperator)
                print(row_format.format(*[str(x) for x in row.values()]))
            print(line_seperator)
        except BaseException as e:
            print(e)
            print(
                "Something went wrong. Maybe there isn't data for what you're looking for")

    # get tournaments for leaderboard
    def get_tournaments(self, include_inelligible, tournament_id):
        resp = requests.get(self.IP + 'tournaments/', verify=self.path_to_public)
        resp.raise_for_status()
        return json.loads(resp.content)
        # convert to leaderboard here DO SOON
        # if not include_inelligible:
        #     print(
        #         f"The following is the leaderboard for eligible contestants for group run {group_info['group_run_id']}.")
        # else:
        #     print(
        #         f"The following is the leaderboard for all contestants for group run {group_info['group_run_id']}.")
        # print(
        #     f"""This group run ran with the launcher version {group_info['launcher_version']} on {group_info['start_run']}. Each client was run {group_info['runs_per_client']} times.""")
        # self.to_table(jsn["data"])

    # def to_leaderboard_record(self, group_runs: list[dict]):
    #
    #     to_return: dict = {
    #         "Team Name": group_runs
    #     }

    # finds uni_id and uni_name for building the leaderboard by calling get_unis() method
    def get_leaderboard_uni_info(self) -> dict:
        unis_info: list[dict] = self.get_unis()
        return {uni['uni_id']: uni['uni_name'] for uni in unis_info}

    # finds the type_type_id, team_name, and eligible
    def get_leaderboard_team_type_info(self) -> dict:
        team_types: list[dict] = self.get_team_types()
        return {team_type['team_type_id']: {'name': team_type['team_type_name'], 'eligible': team_type['eligible']}
                for team_type in team_types}

    # collects all data needed for building the leaderboard
    def get_leaderboard_info(self, uni_info: dict, team_info: dict) -> dict:
        tournaments: list[dict] = self.get_tournaments()
        result: dict = {}
        list_result: list = []

        for index, tournament in enumerate(tournaments):
            if not tournament['is_finished']:
                continue
            # A list of dictionaries that stores the tournament, its index in the list, and when it started
            list_result.append({
                'Index': index,
                'Tournament ID': tournament['tournament_id'],
                'Start Time': tournament['start_run']
            })

        self.print_table(list_result)

        tournament_id: int = self.__validate_to_int('Specify the index of the tournament you would like to view > ')

        for run in tournaments[tournament_id]['runs']:
            for submission_run_info in run:
                team_name: str = submission_run_info['team']['team_name']

                # makes a dict of {'Example Team Name': {all info needed to build leaderboard}}
                result[team_name] = {'Team Name': submission_run_info['team']['team_name'],
                                     'University': uni_info['uni_name'],
                                     'Points Awarded': submission_run_info['points_awarded'],
                                     'Team Type': team_info['team_type_name'],
                                     'Eligible': team_info['eligible']}
        filter()

        return result

    def __validate_to_int(self, prompt: str, cancel: str = '-1') -> int | None:
        while True:
            given: str = input(prompt)

            if given == cancel:
                return None
            try:
                return int(given)
            except:
                ...
