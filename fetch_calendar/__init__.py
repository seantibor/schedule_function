import datetime
import logging
import requests

import azure.functions as func

cal_url = "https://pinecrest.myschoolapp.com/podium/feed/iCal.aspx?z=IE2Q2JOSvocc5htG%2fMsqOq%2byIgbNcfsG5vP2X4b7NUizOPFXg4M%2f4NzSesaHhBst8Zgy0neMKzmfrh6hqFkFUa%2fGGcckH9Kpciw2t%2fGKSzHP78KMZ%2f7ou8dEMz08tiLMEm4haAF64xj7VP%2fjJxMVbSCrdPYru9N9eqVIdkhikwArpV%2bLCyQOnbsNlScI6X0ofo4IRSsEPqT%2b5M6%2fTNlyFVbD4zegiwttrFqbhQpHxE5zIioSdC7OgKH%2bQK%2b6uDOG5aSZvifng%2bVXLMidpdbYM8RWhdykcNNhFyz6pPYfTDnVmA7uyDXFXskkpHmOoxzD5g96tG4loQp6d41JjKumii5EAbCAmtm8kVTGDgz6j1y7haShfO4GdU3aInAQsFZ7LsMuu20EX5llV4o0wKPrYB%2fyiA2bma2Q%2bnV7xIFvWhjaNuVrc3XI3D%2fDLCwW9LPYIO8awdlFCCe8FJ4vA%2bEXdxym5gPJgqcTb0v4MsKBvWmCqjKhgwoQvtuEOP4Y04n%2f%2bgSFtZN29DneH%2f4ebDQ8yDSzOYI9Ic3Lai4faChLnSR1qh%2fV2oBLITHsq6Zt5c2RaIjA8P9YNpgM8Zu%2bU9gStM6M%2f6ljr6JFWh218HyB4zpP2dESDQq%2b3fET2ICMzuV3E%2flv0xiB1ToH2VvOYaKP%2bbLG9pb3Lzglwx6pE%2bsgiVUTPdxb4XBLgNVl6hCTPvEUCENlqCgfQp6m8dRQfJwfHuwaBDwL58IyrKACM2yonSdT3PfCimUqJEY7GaLa18sgWtpM3e2Ue4vOM1qUFncaxGfyK1Uni2WSNsgcFSY0iSdzyDCDwstMNmfo5ueByjyQgMakAsJuBfFZqc5IFllA59MgAGrTBzrCwknKk4zn5Zb9yW%2blqxUO0QOe45O7OvLw9gJ%2f8%2fx5YYUN8hymc3CxeBc3Eua8Rczt68gWIXAOpWmtYZxYNEuY3gyMHOqhxdIhU6l5GeuC5hqv8%2bZycCzl%2b5ZeEC3hKUoElJ8oxdJ9PHBE9%2b6r3qpCqUsd7b8uctMZSycH0xbJdxOk85joT1hrjKLAUia5aTs2%2f87EG%2b7cLrxZBCnkx%2f5nD8WyYP%2f6S42m6HCzxuqAFZ3UXQv3WSNE7QPDL1E%2fxP7byBzjmerHNxrDYDtxA%2bXbBXYtot%2b1xvXyFxSFyLEKBlWAz2kBmGDmrMd1jsorB2sh4LsPrQD6RWwuBYn2pCUQvQVLGpVMhgIby13RZ1pIqrLqKZB%2f6S2Mfy8DVC%2fONSCn%2bd3fMWWSgI4bXtBjOnz85Lqy8jTLqxUkiGX0f0Zso%2fkIQf69xVOczmu4YA6zyMXpFd%2fTegPfgIzRe4BwVZRbEXoO%2bhFOXdk4DdSNJrIA%2bbEnuXpVzPJDiHBSRO1PFTu6ieQPllTLYOTgxbKyZLK4HMSPaLl6NU1jMNRAK9OwuNjcvtmcR2dMi2CMJAPoAHRU0tX%2bPqr%2b1PARzpdm%2b7P5zzmczWsVCDWY1%2bdBXDogGxdLAovHCQs7xg8AktcXLkcBbk9MUDSKRB1zmZseta2Xh6Z%2bQ0TY7M3a3cGPaQefrtjvlPyn5Xp5Yip7gEDWf25Ks%2be97L2zOJbB7W%2fH6nAAmxcXntPn9Q%2bvEegeBTZcT521Pi%2bBU4iHlg7fAP85NPaXWbU8R7aVgkDA%2bsMPrJiPxJRvS3FRyciB"

def main(mytimer: func.TimerRequest, outputblob: func.Out[func.InputStream]) -> None:

    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    logging.info(
        "Python calendar fetch timed trigger function ran at %s", utc_timestamp
    )

    r = requests.get(cal_url, headers=headers)
    if r.status_code == requests.codes.ok:
        ical = r.text
        outputblob.set(ical)
    else:
        logging.error(
            "Could not fetch Pine Crest calendar with error code %s", r.status_code
        )
