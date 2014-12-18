#!/usr/bin/env python3

# real    0m6.080s
# user    0m1.557s
# sys     0m0.176s


from pyquery import PyQuery as pq
import json
from lxml.etree import XMLSyntaxError
import asyncio
import functools
import aiohttp

host = "http://kinox.to"
conn = aiohttp.connector.TCPConnector(share_cookies=True)

def get(url):
    f = Future()
    return f


@asyncio.coroutine
def get_hoster_url(rel, referer):
    url = '{}/aGET/Mirror/{}'.format(host, rel)
    resp = yield from aiohttp.request('get', url, headers= {
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }, connector=conn)
    text = yield from resp.text()
    try:
        respdict = json.loads(text)
    except ValueError:
        return "<no hoster|val{}>".format(resp.status)
    d = pq(respdict["Stream"])
    ret = d("a")[0].attrib["href"]
    if ret.startswith("/Out/?s="):
        ret = ret[8:]
    return ret


@asyncio.coroutine
def get_mirrors_by_episode(rel, season, episode):
    url = '{}/aGET/MirrorByEpisode/{}&Season={}&Episode={}'.format(host, rel, season, episode)
    resp = yield from aiohttp.request('get', url, connector=conn)
    text = yield from resp.text()
    try:
        ret = pq(text)("li")
    except XMLSyntaxError:
        ret = []
        print ("S{}E{} {}".format(season, episode, "<no hoster|xml {} {}>".format(resp.status, text)))
        import sys
        sys.exit(0)
    return ret, resp.status, text


@asyncio.coroutine
def print_hoster_url(rel, season, episode, referer):
    try:
        mirrors, status, text = yield from get_mirrors_by_episode(rel, season, episode)
        m = mirrors[0]
    except IndexError:
        print ("S{}E{} {}".format(season, episode, "<no hoster|idx {} {}>".format(status, text)))
    else:
        hoster_url = yield from get_hoster_url(m.attrib["rel"], referer)
        print ("S{}E{} {}".format(season, episode, hoster_url))


# @asyncio.coroutine
def main(url, min_episode=(0, 0), max_episode=None):
    resp = yield from aiohttp.request('get', url, connector=conn)
    text = yield from resp.text()
    d = pq(text)
    # d = pq(filename="test.html")
    rel = d('#SeasonSelection')[0].attrib['rel']
    print(rel)
    futures = []
    for e in d("#SeasonSelection option"):
        season = e.attrib["value"]
        episodes = e.attrib["rel"].split(",")
        for episode in episodes:
            if (int(season), int(episode)) < min_episode:
                continue
            if max_episode and (int(season), int(episode)) > max_episode:
                break
            futures.append(asyncio.async(print_hoster_url(rel, season, episode, url)))
            # yield from asyncio.sleep(0.01)
    return futures


def stop_loop_if_empty(fut, loop, futures):
    futures.remove(fut)
    if not futures:
        loop.stop()


@asyncio.coroutine
def one():
    yield from asyncio.sleep(1)
    print("one ..")
    return "hans"

@asyncio.coroutine
def test():
    import time
    f = asyncio.async(one())
    yield from asyncio.sleep(2)
    print(f.result())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # futures = loop.run_until_complete(main("http://kinox.to/Stream/The_Big_Bang_Theory-1.html"))
    # for fut in futures:
    #     fut.add_done_callback(functools.partial(stop_loop_if_empty, loop=loop, futures=futures))
    # try:
    #     loop.run_forever()
    # finally:
    #     loop.close()
    loop.run_until_complete(test())
