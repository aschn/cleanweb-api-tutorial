import requests
from urlparse import urljoin
from datetime import datetime
import time

class GitHubClient(object):
    """
    A wrapper for the GitHub API,
    with pagination, basic authentication, and throttling.
    """
    BASE_URL = 'https://api.github.com'

    def __init__(self, username=None, password=None):
        """Initialize with username and password"""
        self.username = username
        self.password = password

    def fetch_data(self, endpoint, method='get', **kwargs):
        """
        By default makes a GET request to https://api.github.com/endpoint,
        passing any kwargs to requests.
        Returns the JSON-decoded response content, concatenating consecutive pages.
        """
        # assemble url
        url = urljoin(self.BASE_URL, endpoint)

        # make request
        response = self._make_request(url, method, **kwargs)

        # extract JSON data
        data = response.json()
        
        # loop over all available next urls
        while self._has_next_url(response):
            # extract next url
            next_url = self._next_url(response)
            
            # make next request
            response = self._make_request(next_url, method, **kwargs)
            
            # concatenate JSON data
            data += response.json()
            
        # return
        return data
        
    def _make_request(self, url, method, **kwargs):
        """
        Makes request to url using method and kwargs, and handles errors.
        Attempts to authenticate if client is initialized with credentials.
        """
        # choose request method
        try:
            requester = getattr(requests, method.lower())
        except AttributeError:
            raise ValueError('%s is not a HTTP method' % method)
        
        # make request
        response = requester(url, **kwargs)
        
        # make request
        if self.username and self.password:
            response = requester(url, auth=(self.username, self.password), **kwargs)
        else:
            response = requester(url, **kwargs)
            
        # check response status for authentication error
        if response.status_code == 401:
            raise ValueError('Authentication error: %s' % response.json()['message'])

        # check response status for throttling
        if response.status_code == 403:
            # get time to wait
            wait_time = self._throttle_wait_time()
            
            # log
            print 'Throttling error: waiting for %d seconds' % wait_time
            
            # wait
            time.sleep(wait_time)
            
            # request recursively
            self._make_request(url, method, **kwargs)

        # return response
        return response

    def _has_next_url(self, response):
        """Returns True if a next url is available, False if not"""
        if 'link' in response.headers.keys():
            return True
        else:
            return False
        
    def _next_url(self, response):
        """Returns the next url"""
        # split link header into next and last rels
        links = response.headers['link'].split(',')
        print links

        # loop over link,rel pairs
        for linkrel in links:
            ugly_link, rel = linkrel.split(';')
            if 'next' in rel:
                link = ugly_link.lstrip('<').rstrip('>')
                return link
        
        # if got here, no next link
        return None

    def _throttle_wait_time(self, url='https://api.github.com/rate_limit'):
        """Returns the number of seconds to wait before throttling is reset"""
        # request throttling info
        response = requests.get(url)
        
        # decode data
        data = response.json()
        
        # get reset time from timestamp
        reset_timestamp = data['resources']['core']['reset']
        reset_datetime = datetime.fromtimestamp(reset_timestamp)
        
        # compute time to wait
        wait_time = reset_datetime - datetime.now()
        wait_seconds = wait_time.total_seconds()
        
        # return
        return wait_seconds
