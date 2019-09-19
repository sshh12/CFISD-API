import requests
import getpass


SERVER_URL = 'http://localhost:5000'


def main(username, password):
    """
    Manual Request Test

    Manually interacts with the api with given creds
    and prints the response
    """
    test_post(password, '/api/transcript/' + username)
    test_post(password, '/api/reportcard/' + username)
    test_post(password, '/api/attendance/' + username)
    test_post(password, '/api/current/' + username)


def test_post(password, endpoint):
    print('POST ' + SERVER_URL + endpoint)
    resp = requests.post(SERVER_URL + endpoint, json={'password': password})
    print(resp.text)


if __name__ == "__main__":

    # user = input('Username > ')
    # passwd = getpass.getpass('Password (Hidden) > ')
    user = 's642344'
    passwd = '***REMOVED***'

    main(user, passwd)
