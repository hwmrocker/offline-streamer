#!/usr/bin/env python3

# real    1m41.833s
# user    0m2.135s
# sys 0m0.189s

import requests
from pyquery import PyQuery as pq
import json
from lxml.etree import XMLSyntaxError

host = "http://kinox.to"


def get_hoster_url(rel, referer):
    url = '{}/aGET/Mirror/{}'.format(host, rel)
    resp = requests.get(url, headers= {
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    })
    respdict = json.loads(resp.text)
    d = pq(respdict["Stream"])
    ret = d("a")[0].attrib["href"]
    if ret.startswith("/Out/?s="):
        ret = ret[8:]
    return ret


def get_mirrors_by_episode(rel, season, episode):
    url = '{}/aGET/MirrorByEpisode/{}&Season={}&Episode={}'.format(host, rel, season, episode)
    return pq(url)("li")


def main(url, min_episode=(0,0)):
    d = pq(url)
    rel = d('#SeasonSelection')[0].attrib['rel']
    print(rel)
    for e in d("#SeasonSelection option"):
        season = e.attrib["value"]
        episodes = e.attrib["rel"].split(",")
        for episode in episodes:
            if (int(season), int(episode)) < min_episode:
                continue
            try:
                mirrors = get_mirrors_by_episode(rel, season, episode)
            except XMLSyntaxError:
                print ("S{}E{} {}".format(season, episode, "<no hoster>"))
                continue
            # print(mirrors)
            m = mirrors[0]
            # print("{}, {}".format(m, m.attrib))
            hoster_url = get_hoster_url(m.attrib["rel"], url)
            print ("S{}E{} {}".format(season, episode, hoster_url))

if __name__ == "__main__":
    main("http://kinox.to/Stream/The_Big_Bang_Theory-1.html")

# http://kinox.to/aGET/Mirror/The_Big_Bang_Theory-1&Hoster=8&Season=8&Episode=1
# http://kinox.to/aGet/Mirror/The_Big_Bang_Theory-1&Hoster=8&Season=8&Episode=1
