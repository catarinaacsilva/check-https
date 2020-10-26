# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.3'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import re
import ssl
import idna
import logging
import requests
import urllib3

from socket import socket
from enum import Enum
from OpenSSL import SSL
from datetime import datetime
from oscrypto import tls
from urllib.parse import urlparse
from certvalidator import CertificateValidator, errors
from bs4 import BeautifulSoup

from webcache import WebCache, get_request, get_head, USER_AGENT_LINUX_CHROME
from html_similarity import style_similarity, structural_similarity


logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S')

logger = logging.getLogger('HTTPS')


# Disable InsecureRequestWarning: Unverified HTTPS request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Hsts(Enum):
    HSTS = 1
    NOT_HSTS = 2
    NOT_WORKING_HSTS = 3


class Redirects(Enum):
    REDIRECT_301 = 1
    REDIRECT_302 = 2
    REDIRECT_303 = 3
    REDIRECT_307 = 4
    REDIRECT_308 = 5
    NOT_REDIRECT = 6
    ERROR = 7
    TIMEOUT = 8


# Check if url is in the base domain
def same_domain(base, url):
    url_content = url.split('/')
    base_content = base.split('/')
    if url_content[2] == base_content[2]:
        return True
    return False


# Check if a URL is absolute
def is_absolute(url):
    return bool(urlparse(url).netloc)


# Get links recursive
# Not used right now...
def recursive_get_links(url, max_depth=3, urls=[], depth=0):
    #print("%s (%d)"%(url, depth))
    local_links = get_links(url)
    for ll in local_links:
        if not ll in urls and same_domain(ll, url):
            urls.append(ll)
            if (depth+1) <= max_depth or max_depth == -1:
                recursive_get_links(ll, max_depth, urls, depth+1)
    return urls


# Return a list with all the tags[atributes]
# https://stackoverflow.com/questions/31666584/beutifulsoup-to-extract-all-external-resources-from-html
def get_links(tag: str, attribute: str, soup):
   list = []
   for x in soup.findAll(tag):
       try:
           list.append(x[attribute])
       except KeyError:
           pass
   return list

# Get all local links from a webpage
def get_all_links(url: str, wc: WebCache):
    rv = []
    data = wc.get(url)
    if data is not None:
        soup = BeautifulSoup(data['html_rendered'], 'html.parser')
        #for link in soup.findAll('a', attrs={'href': re.compile("^http")}):
        #    url = link.get('href')
        #   rv.append(url)    
        resources = [('a', 'href'), ('img', 'src'), ('script', 'src'), ('link','href'), ('video','src'),
        ('audio', 'src'), ('iframe', 'src'), ('embed', 'src'), ('object', 'data'), ('source', 'src')]
        for r in resources:
            rv.extend(get_links(r[0], r[1], soup))
    return rv

# Get only the resources links
def get_resources_links(url: str, wc: WebCache):
    rv = []
    data = wc.get(url)
    if data is not None:
        soup = BeautifulSoup(data['html_rendered'], 'html.parser')
        #for link in soup.findAll('a', attrs={'href': re.compile("^http")}):
        #    url = link.get('href')
        #   rv.append(url)    
        resources = [('img', 'src'), ('script', 'src'), ('link','href'), ('video','src'),
        ('audio', 'src'), ('iframe', 'src'), ('embed', 'src'), ('object', 'data'), ('source', 'src')]
        for r in resources:
            rv.extend(get_links(r[0], r[1], soup))
    return rv


# Verify if a resource is media or not
def is_media_resource(url: str, timeout):
    head = get_head(url, timeout)
    if head is not None:
        content_type = head.headers.get('content-type').lower()
        print('ct '+content_type)
        if 'image' in content_type:
            return True
        elif 'audio' in content_type:
            return True
        elif 'video' in content_type:
            return True
        return False
    else:
        logger.warning('Resource timeout: %s', url)
        return False


# verify if a list of a resources is a HTTP
def no_http_resources(url: str, timeout: int, wc: WebCache):
    links = get_all_links(url, wc)
    for link in links:
        if is_absolute(link):
            protocol = link.split(':')
            logger.debug('Check %s', link)
            #print('Resource : '+link+' protocol '+protocol[0])
            if protocol[0] == 'http': #and is_media_resource(link, timeout):
                logger.warning('Invalid resource: %s', link)
                return False
    return True


# HTTP/HTTPS Similarity
def compare_websites(url: str, wc: WebCache, k=0.3):
    data1 = wc.get('http://{}'.format(url))
    data2 = wc.get('https://{}'.format(url))
    if data1 is None or data2 is None:
        return 0.0
    else:
        data1 = data1['html_rendered']
        data2 = data2['html_rendered']
        try:
            rv = k * structural_similarity(data1, data2) + \
                (1 - k) * style_similarity(data1, data2)
        except Exception as e:
            print(e)
            rv = 0.0
        return rv


# HSTS
def check_hsts(url: str, timeout: int):
    headers = {'User-Agent': USER_AGENT_LINUX_CHROME}
    response = get_head(url, headers=headers, timeout=timeout)
    if response is not None:
        if 'strict-transport-security' in response.headers:
            return Hsts.HSTS
        else:
            return Hsts.NOT_HSTS
    else:
        return Hsts.NOT_WORKING_HSTS


# Redirects
def test_redirects(url: str, protocol='https://'):
    headers = {'User-Agent': USER_AGENT_LINUX_CHROME}
    response = get_head(url, headers=headers, timeout=None)
    if response is not None:
        if response.history:
            if response.url.startswith(protocol):
                if response.history[-1].status_code == 301:
                    return Redirects.REDIRECT_301
                elif response.history[-1].status_code == 302:
                    return Redirects.REDIRECT_302
                elif response.history[-1].status_code == 303:
                    return Redirects.REDIRECT_303
                elif response.history[-1].status_code == 307:
                    return Redirects.REDIRECT_307
                elif response.history[-1].status_code == 308:
                    return Redirects.REDIRECT_308
            return Redirects.ERROR
        else:
            return Redirects.NOT_REDIRECT
    else:
        return Redirects.TIMEOUT


# verificar cadeia de certificação
# https://github.com/wbond/certvalidator/blob/master/docs/usage.md
def verify_cert(url: str, port=443):
    try:
        session = tls.TLSSession(manual_validation=True)
        connection = tls.TLSSocket(url, port, session=session)
        validator = CertificateValidator(
            connection.certificate, connection.intermediates)
        validator.validate_tls(connection.hostname)
        return True
    except Exception as e:
        logger.warning(e)
        return False


def check_https(hostname, port=443):
    try:
        hostname_idna = idna.encode(hostname)
        sock = socket()

        sock.connect((hostname, port))
        ctx = SSL.Context(SSL.SSLv23_METHOD)  # most compatible
        ctx.check_hostname = False
        ctx.verify_mode = SSL.VERIFY_NONE

        sock_ssl = SSL.Connection(ctx, sock)
        sock_ssl.set_connect_state()
        sock_ssl.set_tlsext_host_name(hostname_idna)
        sock_ssl.do_handshake()
        cert = sock_ssl.get_peer_certificate()
        crypto_cert = cert.to_cryptography()

        #x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
        #now = datetime.now()
        #not_after = datetime.strptime(x509.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ')
        #not_before = datetime.strptime(x509.get_notBefore().decode('utf-8'), '%Y%m%d%H%M%SZ')
        # if now > not_after or now < not_before:
        #    return Cert.EXPIRED
        # return Cert.VALID

        sock_ssl.close()
        sock.close()
        return True
    except Exception as e:
        return False


def tests_quality(url: str, wc: WebCache, port=443, timeout=10):
    # HTTPS
    has_https = check_https(url)

    # Certificate
    if has_https:
        valid_cert = verify_cert(url)
    else:
        valid_cert = False

    # Redirect
    if has_https:
        res = test_redirects('http://{}'.format(url))
        if res == Redirects.TIMEOUT or res == Redirects.NOT_REDIRECT or res == Redirects.ERROR:
            redirect = False
        else:
            redirect = True
        # Redirect 301
        if res == Redirects.REDIRECT_301:
            r301 = True
        else:
            r301 = False
    else:
        redirect = False
        r301 = False

    # HSTS
    if has_https:
        res = check_hsts('https://{}'.format(url), timeout)
        if res == Hsts.HSTS:
            has_hsts = True
        else:
            has_hsts = False
    else:
        has_hsts = False

    # No HTTP Resources
    if valid_cert:
        no_http = no_http_resources('https://{}'.format(url), timeout, wc)
    else:
        no_http = False

    return (has_https, valid_cert, redirect, r301, has_hsts, no_http)


def tests_defects(url: str, wc: WebCache, valid_cert, redirect, port=443, timeout=10):
    # HTTPS Redirect to HTTP
    if valid_cert:
        res = test_redirects('https://{}'.format(url), protocol='http://')
        if res == Redirects.TIMEOUT or res == Redirects.NOT_REDIRECT or res == Redirects.ERROR:
            https_redirect = False
        else:
            https_redirect = True

        # HTTPS Redirect 301 to HTTP
        if res == Redirects.REDIRECT_301:
            https_r301 = True
        else:
            https_r301 = False
    else:
        https_redirect = False
        https_r301 = False

    # Similarity
    if redirect:
        sim = 1.0
    elif valid_cert:
        sim = compare_websites(url, wc)
    else:
        sim = 0.0

    return (https_redirect, https_r301, sim)


def run_all_tests(url: str, wc: WebCache, port=443, timeout = 30):
    logger.debug('Test %s', url)
    qualities = tests_quality(url, wc, timeout=timeout)
    defects = tests_defects(url, wc, qualities[1], qualities[2], timeout=timeout)
    rv = {'qualities': qualities, 'defects': defects}

    if rv['qualities'][0]:
        rv['data'] = wc.get('https://{}'.format(url))
    else:
        rv['data'] = wc.get('http://{}'.format(url))
    return rv


#data = run_all_tests('www.cm-agueda.pt')
#print('{} {}'.format(data['qualities'], data['defects']))
#print(test_redirects('https://{}'.format('www.cm-alcoutim.pt'), protocol='http://'))
#data = run_all_tests('hrun.hopto.org')
#data = run_all_tests('cm-viladoporto.pt')
# print(data['qualities'])
# print(data['defects'])

#print(check_https('www.cm-abrantes.pt'))

#wc = WebCache()
#rv = run_all_tests('www.cm-vrsa.pt', wc)
#print(rv['qualities'])
#print(rv['defects'])
