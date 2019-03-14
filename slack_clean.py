import argparse
import requests
import time
import json
requests.packages.urllib3.disable_warnings()
    #the token is taken from this url: https://api.slack.com/custom-integrations/legacy-tokens while logged on
token = "yourToken"
    #name is your user name, yourID is found on your slack by clicking on your user and looking at the URL
    #i.e.https://<slack_workspace>.slack.com/messages/<teamID>/team/<userID>
users = [{"name": "yourName", "user":"yourID" }]

def main():
    """
    Entry point of the application
    :return: void
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--days", type=int, default=None, help="Delete files older than x days (optional)")
    options = parser.parse_args()

    try:
        print "[*] Fetching file list.."
        file_ids = list_file_ids(days=options.days)
    except KeyboardInterrupt:
        print "\b\b[-] Aborted"
        exit(1)

def calculate_days(days):
    """
    Calculate days to unix time
    :param days: int
    :return: int
    """
    return int(time.time()) - days * 24 * 60 * 60

def list_file_ids(days=None):
    print "[+] Fetching user list"
    users_uri = "https://slack.com/api/users.list"
    users_param = {'token':token}
    response_users = requests.get(users_uri, params=users_param).json()
    members_users = response_users['members']
    for user in members_users:
        print "[+] The name is", user['name'], "and the ID is", user['id'], "status is", user['deleted']
        if user['deleted'] is True:
            print "[!!!] User", user['name'], "is deleted, passing."
            continue
        user_name = user['name']
        print "delete files of user: "+user_name
        user_id = user['id']
        user_token = token
        if days:
            params = {'token': user_token, 'count': 1000, 'ts_to': calculate_days(days), 'user': user_id}
            print "ts_to: ", calculate_days(days)
        else:
            params = {'token': user_token, 'count': 1000, 'user': user_id}
        uri = 'https://slack.com/api/files.list'
        response = requests.get(uri, params=params).json()
        files = response['files']
        #return [f['id'] for f in files]
        print [f['id'] for f in files]
        for f in files:
            dresponse = json.loads(requests.get('https://slack.com/api/files.delete', params={'token': user_token, 'file': f['id']}).text)
            time.sleep(2)
            if dresponse["ok"]:
                print "[+] Deleted: ", f['id']
            else:
                print "[!] Unable to delete: ", f['id'] + ", reason:", dresponse["error"]

if __name__ == '__main__':
    main()
