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


async def aiohttp_get(url: str) -> Dict:
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.read()
                return {'status': response.status, 'url': url, 'text': text}
            else:
                return {'status': response.status, 'url': url, 'text': None}


async def fetch_query_ptool_page(server_url: str, col_id: str):
    start_time = datetime.now(timezone.utc)

    url = await build_url(server_url, col_id, 'query_ptool')
    r = await aiohttp_get(url)

    r['start_time'] = start_time
    r['server_url'] = server_url
    r['col_id'] = col_id

    return r


async def make_time_obj(t: str) -> datetime.date:
    if 'Universal' in t:
        t = t.replace('Universal', 'UTC')
    return dateutil.parser.parse(t)


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


async def download_pdf_when_ready(server_url: str, col_id:str):
    r = await fetch_query_ptool_page(server_url, col_id)
    if r['status'] == 200:
        soup = BeautifulSoup(r['text'], 'html.parser')
        time_string = soup.findAll('td')[2].string
        # When we have a time string that means the PDF is available
        if time_string:
            time_obj = await make_time_obj(time_string)
            time_diff = r['start_time'] - time_obj
            print(f'PDF for col{col_id} is {time_diff} old')
            url = await build_url(server_url, col_id, 'pdf')
            await download_pdf(url, 'col' + col_id)
        else:
            print(f'The pdf is not ready for col{col_id}. Will wait and retry in 20 sec.')
            await asyncio.sleep(20)
            await download_pdf_when_ready(server_url, col_id)
    else:
        print(f'There was a problem with {server_url} and col_id {col_id}')
        return 0


async def build_url(base_url: str, col_id: str, endpoint: str) -> str:
    return '{base_url}/content/col{col_id}/latest/{endpoint}'.format(
        base_url=base_url,
        col_id=col_id,
        endpoint=endpoint
    )


async def main(server_url: str, col_ids: List) -> None:
    futures = [download_pdf_when_ready(server_url, col_id) for col_id in col_ids]

    await asyncio.wait(futures)


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
    print(f"Started at: {datetime.utcnow()}")
    try:
        asyncio.run(main(server_url, col_ids))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    cli()
