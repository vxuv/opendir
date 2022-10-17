import queue
import requests
from bs4 import BeautifulSoup
from typing import Generator, List

from .constants import FLAG

from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class OpenDirFileObj:
    """
    Summary:
        File Object for OpenDir, contains some general
        information about the file provided by the server.
    """
    def __init__(self, filename: str, date: str, size: str, description: str, is_dir: str, url: str):
        """Constructor for OpenDirFileObj

        Args:
            filename (str): Filepath
            date (str): Date of last modification
            size (str): Size of file
            description (str): Description of file
            is_dir (str): Whether or not the file is a directory
            url (str): URL to the file
        """
        self.filename = filename
        self.date = date
        self.size = size
        self.description = description
        self.is_dir = is_dir
        self.url = url
    
    def __str__(self) -> str:
        """String representation of OpenDirFileObj"""
        return f'OpenDirFileObj(filename={self.filename}, date={self.date}, size={self.size}, description={self.description}, is_dir={self.is_dir}, url={self.url})'


class OpenDir:
    """
    Summary:
        OpenDir Scraper
    """
    def __init__(self, host: str, timeout: int = 5):
        """
        Constructor for OpenDir

        Args:
            host (str): Host to scan
            timeout (int, optional): Timeout for requests. Defaults to 5.
        """
        self.host = host
        self.timeout = timeout
    
    def is_opendir(self, page_content: str) -> bool:
        """Checks if the page is an open
        directory.

        Args:
            page_content (str): Content of the webpage

        Returns:
            bool: Is a directory
        """
        if FLAG in page_content:
            return True
        return False

    def get_files(self, base_url: str, page_content: str) -> Generator[None, OpenDirFileObj, None]:
        """Gets the files from the page

        Args:
            base_url (str): Base URL
            page_content (str): HTML of the page

        Yields:
            Generator[OpenDirFileObj]: Listing of OpenDirFileObj
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        table = soup.find('table')
        if table != None:
            rows = table.find_all('tr')
            if rows != None:
                for row in rows:
                    items =  row.find_all('td')
                    if len(items) == 0:
                        continue
                    is_dir = items[0].find('img').get('alt') == '[DIR]'
                    filename = items[1].find('a').text
                    date = items[2].text.replace(' ', '')
                    size = items[3].text if items[3].text.replace(' ', '') != '  - ' else None
                    description = items[4].text.replace('&nbsp;', '')
                    url = f'{base_url}{filename}'
                    yield OpenDirFileObj(
                        filename=filename,
                        date=date,
                        size=size,
                        description=description,
                        is_dir=is_dir,
                        url=url
                    )

    def crawl_host(self) -> Generator[None, OpenDirFileObj, None]:
        """
        Summary:
            Crawls the host and returns all of the files
            as a generator.
        """
        scan_queue = queue.Queue()
        scan_queue.put(self.host)
        while not scan_queue.empty():
            host = scan_queue.get()
            req = requests.get(
                host,
                verify=False,
                timeout=self.timeout
            )
            if req.status_code == 200 and self.is_opendir(req.text):
                for file in self.get_files(host, req.content):
                    if file.is_dir:
                        scan_queue.put(file.url)
                    else:
                        yield file
