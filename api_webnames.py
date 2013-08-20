import httplib
import requests


API_URL = 'https://www.webnames.ru:81/RegTimeSRS.pl'
API_TIMEOUT = 30
API_REVISION = 1
API_LANG = 'ru'

#set HTTP/1.0
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'


class RegTimeSRSApiException(BaseException):
    pass


class RegTimeSRSApi(object):
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def run_command(self, method, params):

        url = API_URL

        req_params = {
            'username': unicode(self.login),
            'password': unicode(self.password),
            'thisPage': unicode(method),
            'interface_revision': API_REVISION,
            'interface_lang': API_LANG,
        }
        req_params.update(params)

        data = {}

        #encode utf8 to windows-1251
        for k, v in req_params.items():
            if isinstance(v, unicode):
                data[k] = v.encode('windows-1251')
            else:
                data[k] = v

        try:
            result = requests.post(url, data, timeout=API_TIMEOUT)
        except (requests.ConnectionError, requests.HTTPError, requests.Timeout, requests.TooManyRedirects) as e:
            raise RegTimeSRSApiException(e)

        if result.status_code != 200:
            raise RegTimeSRSApiException("No valid response received. Status code %s" % result.status_code)

        if result.text.startswith('Error'):
            raise RegTimeSRSApiException(result.text[len('Error: '):])

        if not result.text.startswith('Success'):
            error = 'Api response error %s' % result.text
            raise RegTimeSRSApiException(error)

        return result.text[len('Success: '):]


class RegTimeSRSRegistrarApi(RegTimeSRSApi):
    def pispRegistration(self, domain_name, period, contacts, nss, notpaid=False):
        params = {
            'domain_name': domain_name,
            'period': period,
            'notpaid': int(notpaid),
        }
        params.update(contacts)
        params.update(nss)
        print params
        return self.run_command('pispRegistration', params)

    def pispInitiateTransfer(self, domain_name, period, authinfo, contacts, nss, notpaid=False):
        params = {
            'domain_name': domain_name,
            'period': period,
            'authinfo': authinfo,
            'notpaid': notpaid,
        } \
            .update(contacts) \
            .update(nss)
        return self.run_command('pispInitiateTransfer', params)

    def pispCheckDomain(self, domain_name, tlds=None):
        params = {
            'domain_name': domain_name,
        }
        if tlds:
            params['tlds'] = tlds
        return self.run_command('pispCheckDomain', params)

    def pispWhois(self, domain_name):
        return self.run_command('pispWhois', {domain_name: domain_name})

    def pispRenewDomain(self, domain_name, period, notpaid=False):
        params = {
            'domain_name': domain_name,
            'period': period,
            'notpaid': notpaid,
        }
        return self.run_command('pispRenewDomain', params)

    def pispRedelegation(self, domain_name, nss):
        params = nss
        params['domain_name'] = domain_name
        return self.run_command('pispRedelegation', params)

    def pispContactDetails(self, domain_name, contacts):
        params = contacts
        params['domain_name'] = domain_name
        return self.run_command('pispContactDetails', params)

    def pispGetApprovalStatus(self, domain_name):
        return self.run_command('pispGetApprovalStatus', {domain_name: domain_name})

    def pispDomainInfo(self, domain_name):
        return self.run_command('pispDomainInfo', {domain_name: domain_name})


class RegTimeSRSBillApi(RegTimeSRSApi):
    def pispGetPrice(self, tld=False, currency='RUR'):
        params = {}
        if tld:
            params['tld'] = tld
        if currency:
            params['currency'] = currency

        return self.run_command('pispDomainInfo', params)
