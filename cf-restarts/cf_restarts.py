import subprocess
import getpass
import json
import re
import sys

from subprocess import TimeoutExpired, CalledProcessError, CompletedProcess

from unittest import mock


def logout():
    try:
        subprocess.run(['cf', 'logout'], check=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
    except subprocess.CalledProcessError as err:
        print("other error: ", err)


def login(account, password):
    try:
        subprocess.run(['cf', 'login', '-a', account['endpoint'], '-o', account['org'], '-s', account['space'], '-u',
                        account['user'], '-p', password], check=True, stdout=subprocess.PIPE, timeout=5).stdout.decode("utf-8")
    except TimeoutExpired:
        sys.exit("Could not login to org: %s, user: %s, please check your password" % (account['org'], account['user']))
    except CalledProcessError as err:
        print("other error", err)


def get_stopped_apps(user):
    result = None
    try:
        result = subprocess.run(['cf', 'apps'], check=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
    except subprocess.CalledProcessError as err:
        print("other error: ", err)

    app_names = []
    if result:
        result = result.split('\n')[4:-1]
    else:
        return app_names

    for line in result:
        application = re.compile(r"\s+").split(line)
        application_name = application[0]
        status = application[1]
        print("user: " + user + " app name: " + application_name + "   status: " + status)
        if status == 'stopped':
            app_names.append(application_name)

    return app_names


def restart_apps(app_names):
    for app in app_names:
        restart_status = subprocess.run(['cf', 'restart', app], check=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
        print(restart_status)


if __name__ == '__main__':

    password = getpass.getpass('Input password: ')

    with open('cf_accounts.json') as accounts_file:
        accounts = json.load(accounts_file)

    for account in accounts:
        logout()
        login(account, password)
        restart_apps(get_stopped_apps(account['user']))

    logout()


# unit tests


def test_get_stopped_apps():
    subprocess.run = mock.MagicMock(return_value=CompletedProcess("", 0, b"Getting apps in org orgname / space dev as user@username...\nOK\n\nname    requested state   instances   memory   disk   urls\napp1   stopped           1/1         256M     1G     app1.eu-gb.mybluemix.net\napp2   started           1/1         256M     1G     app2.eu-gb.mybluemix.net\napp3   stopped           1/1         256M     1G     app3.eu-gb.mybluemix.net\n", None))

    assert get_stopped_apps('user') == ['app1', 'app3']


def test_get_stopped_apps_no_stopped_apps():
    subprocess.run = mock.MagicMock(return_value=CompletedProcess("", 0, b"Getting apps in org orgname / space dev as user@username...\nOK\n\nname    requested state   instances   memory   disk   urls\napp1   started           1/1         256M     1G     app1.eu-gb.mybluemix.net\n", None))

    assert get_stopped_apps('user') == []
