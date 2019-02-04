import asyncio
import os
from datetime import datetime, timezone
from typing import List

from bs4 import BeautifulSoup

from src.constants import DOWNLOAD_PATH
from src.utils import (aiohttp_get,
                       build_url,
                       download_file, make_time_obj)


async def fetch_query_ptool_page(server_url: str, col_id: str):
    """ Gets the query_ptool_page and adds some more metadata to the request.

    """
    start_time = datetime.now(timezone.utc)

    url = await build_url(server_url, col_id, "query_ptool")
    r = await aiohttp_get(url)

    r["start_time"] = start_time
    r["server_url"] = server_url
    r["col_id"] = col_id
    return r


async def download_pdf(url: str, filename: str, timestamp: bool = True) -> None:
    """ Downloads a pdf to a specific path.

    """
    if timestamp:
        filename = datetime.now().strftime(filename + "-%Y%m%d-%H%M")

    filename = os.path.join(DOWNLOAD_PATH, filename + ".pdf")
    print("Downloading PDF to: {filename}".format(filename=filename))

    await download_file(url, filename)


async def download_pdf_when_ready(server_url: str, col_id:str):
    """ Checks the query_ptool_page for a time string and downloads the pdf.

    The PDF creation process can take several minutes. This command will check
    the status of the query_ptool_page by looking for a timestamp of when the
    PDF was generated. Upon finding a timestamp it will begin a download of the
    pdf. BeautifulSoup makes this very easy to do.

    """
    r = await fetch_query_ptool_page(server_url, col_id)
    pdf_url = await build_url(server_url, col_id, "pdf")
    if r["status"] == 200:
        soup = BeautifulSoup(r["text"], "html.parser")
        time_string = soup.findAll("td")[2].string
        # When we have a time string that means the PDF is available
        if time_string:
            time_obj = await make_time_obj(time_string)
            time_diff = r["start_time"] - time_obj
            print(f"PDF for col{col_id} is {time_diff} old")
            await download_pdf(pdf_url, col_id)
        else:
            print(f"The pdf is not ready for {col_id} at {r['url']}. "
                  f"Will wait and retry in 20 sec.")
            await asyncio.sleep(20)
            await download_pdf_when_ready(server_url, col_id)
    else:
        print(f"There was a problem with {server_url} and col_id {col_id}")
        return 0


async def download_pdfs(server_url: str, col_ids: List) -> None:
    """ Creates a list of download_pdf_when_ready futures and runs them.

    """
    futures = [download_pdf_when_ready(server_url, col_id) for col_id in col_ids]

    await asyncio.wait(futures)
