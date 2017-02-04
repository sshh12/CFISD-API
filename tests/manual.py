import getpass
import pprint

from cfisdapi.grades import HomeAccessCenter

def test(username, password):
    hac = HomeAccessCenter(username)
    hac.login(password)

    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(hac.get_classwork())
    pp.pprint(hac.get_reportcard())
    

if __name__ == "__main__":
    u = raw_input('Username > ')
    p = getpass.getpass('Password (Hidden) > ')
    test(u, p)
