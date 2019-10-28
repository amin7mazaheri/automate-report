from bs4 import BeautifulSoup

from utils import get_page
from utils import logger

BASE_URL = "https://www.abuseipdb.com/check/"
FOUND_STR = "was found in our database!"
NOT_FOUND_STR = "was not found in our database"


def make_url(ip):
    logger.debug("making abusedb url for {ip}")
    return BASE_URL + ip


def get_url(url):
    logger.debug("requesting the {url} from abusedb")
    return get_page(url=url)


def parse_page(ip):
    logger.info("starting to look up {ip} for abusedb")

    url = make_url(ip=ip)
    page = get_url(url=url)

    if not page:  # if page has not received successfully
        return None

    soup = BeautifulSoup(page, 'html.parser')

    obj = dict()
    obj['ip'] = ip or None  # get the ip
    obj['isp'] = soup.title.string.split(" | ")[1]  # get the isp
    found_state_str = str(soup.select_one("div.well h3"))  # get found/unfound

    if FOUND_STR in found_state_str:

        logger.debug("found the attacker in abusedb system")
        obj['found'] = 1
        count, percent = soup.select("div.well p b")
        obj['count_reported'] = count.string  # How many reports?
        obj['abuse_assurance'] = percent.string  # How sure we are?
        obj['categories'] = list(set([x.string for x in soup.select("td.text-right span.label")]))
        # What catagories is this ip reported for?

    elif NOT_FOUND_STR in found_state_str:
        logger.debug("didn't find the attacker in abusedb system")
        obj['found'] = 0
    else:
        logger.warning("No data of report was parsed for {ip}")
    return {'abusedb': obj}
