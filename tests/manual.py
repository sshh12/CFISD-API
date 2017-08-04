import getpass
import pprint

from cfisdapi.grades import HomeAccessCenter

def main(username, password):
    """
    Manual Test

    Manually interacts with the api with given creds and prints
    the returned recursive dict/json.
    """
    hac = HomeAccessCenter(username)
    hac.login(password)

    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(hac.get_classwork())
    pp.pprint(hac.get_reportcard())


if __name__ == "__main__":

    user = raw_input('Username > ')
    passed = getpass.getpass('Password (Hidden) > ')

    main(user, passed)
