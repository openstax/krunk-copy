import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

import dateutil.parser

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from docopt import docopt

HOME_PATH = str(Path.home())
DOWNLOAD_PATH = os.path.join(HOME_PATH, 'Downloads')


async def fetch(url: str, ) -> Dict:
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.read()
                return {'status': response.status, 'url': url, 'text': text}
            else:
                return {'status': response.status, 'url': url, 'text': None}


async def download_pdf(url: str, filename: str, timestamp: bool = True) -> None:
    if timestamp:
        filename = datetime.now().strftime(filename + '-%Y%m%d-%H%M')

    filename = os.path.join(DOWNLOAD_PATH, filename + '.pdf')
    print('Downloading PDF to: {filename}'.format(filename=filename))

    async with ClientSession() as session:
        async with session.get(url) as response:
            with open(filename, 'wb') as f_handle:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f_handle.write(chunk)
            return await response.release()


async def build_url(base_url: str, col_id: int, endpoint: str) -> str:
    return '{base_url}/content/col{col_id}/latest/{endpoint}'.format(
        base_url=base_url,
        col_id=col_id,
        endpoint=endpoint
    )


async def poll_query_ptool(server_url: str, col_ids: List) -> None:
    start_time = datetime.now(timezone.utc)
    print('Polling started at {start_time}'.format(start_time=start_time))
    while col_ids:
        for index, col_id in enumerate(col_ids):
            url = await build_url(server_url, col_id, 'query_ptool')
            r = await fetch(url)

            if r['status'] == 200:
                soup = BeautifulSoup(r['text'], 'html.parser')
                time_string = soup.findAll('td')[2].string
                # When we have a time string that means the PDF is available
                if time_string:
                    time_obj = dateutil.parser.parse(time_string.replace('Universal', 'UTC'))
                    time_diff = start_time - time_obj
                    print('PDF for col{col_id} completed at {time} {time_diff} ago'.format(
                        col_id=col_id, time=time_obj, time_diff=time_diff))
                    url = await build_url(server_url, col_id, 'pdf')
                    await download_pdf(url, 'col' + col_id)
                    col_ids.pop(index)
            else:
                col_ids.pop(index)
                print('There was a problem with {url}'.format(url=r['url']))
                continue

        asyncio.sleep(30)


def run(server_url: str, col_ids: List) -> None:
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(poll_query_ptool(server_url, col_ids))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


def cli():
    cli_docs = """Krunk Copy: Get krunk with downloading collections from legacy.
Usage:
  kcopy <server_url> <collection_ids> 
  kcopy (-h | --help)

Examples:
  kcopy https://legacy-devb.cnx.org 23566,23455,23456
  kcopy https://legacy-qa.cnx.org 23678
  kcopy https://legacy-devb.cnx.org "23456, 34567, 67864"

Note:
  You may need to place quotes around collection ids because of your shell
    """
    arguments = docopt(cli_docs)

    server_url = arguments['<server_url>']
    col_ids = [col_id.strip()
               for col_id in arguments['<collection_ids>'].split(',')]

    print("Polling and downloading PDF's "
          "for {col_ids} at {server_url}".format(col_ids=col_ids,
                                                 server_url=server_url))

    run(server_url, col_ids)


if __name__ == '__main__':
    cli()
