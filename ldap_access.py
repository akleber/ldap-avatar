#!/usr/bin/python

import ldap
import pprint
import ConfigParser

def get_user_infos():

    user_infos = []

    config = ConfigParser.RawConfigParser()
    config.read('avatar.cfg')
    LDAP_SERVER = config.get('LDAP', 'SERVER')
    LDAP_USERNAME = config.get('LDAP', 'USERNAME')
    LDAP_PASSWORD = config.get('LDAP', 'PASSWORD')
    LDAP_BASE_DN = config.get('LDAP', 'BASE_DN')
    LDAP_FILTER = config.get('LDAP', 'FILTER')

    print(LDAP_BASE_DN)
    print(LDAP_FILTER)

    attrs = ['proxyAddresses','thumbnailPhoto']

    try:
        # build a client
        ldap_client = ldap.initialize(LDAP_SERVER)
        # perform a synchronous bind
        ldap_client.set_option(ldap.OPT_REFERRALS,0)
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        ldap_client.unbind()
        print 'Wrong username or password'
    except ldap.SERVER_DOWN:
        print 'AD server not available'

    result = ldap_client.search_s(LDAP_BASE_DN, ldap.SCOPE_SUBTREE, LDAP_FILTER, attrs)

    ldap_client.unbind()

    for dn,entry in result:
        if not 'proxyAddresses' in entry:
            continue

        proxyAddresses = entry['proxyAddresses']
        smtp_addresses = [ a[5:].lower() for a in proxyAddresses if a.lower().startswith('smtp:')]
        photo = entry['thumbnailPhoto'][0]

        user = (smtp_addresses, photo)
        user_infos.append(user)

    return user_infos


if __name__ == "__main__":
    user_infos = get_user_infos()

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(user_infos)
