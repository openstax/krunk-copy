import os
import re
import zipfile
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import Dict

import dateutil.parser
from aiohttp import ClientSession

from src.constants import DOWNLOAD_PATH


async def make_time_obj(t: str) -> datetime.date:
    if "Universal" in t:
        t = t.replace("Universal", "UTC")
    return dateutil.parser.parse(t)


async def aiohttp_get(url: str) -> Dict:
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.read()
                return {"status": response.status, "url": url, "text": text.decode('utf-8')}
            else:
                raise Exception(f"There was a problem retrieving the {url}. "
                                f"Status Code: {response.status}")


async def download_file(url: str, filename: str) -> None:
    async with ClientSession() as session:
        async with session.get(url) as response:
            with open(filename, "wb") as f_handle:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f_handle.write(chunk)
            return await response.release()


async def build_url(base_url: str, item_id: str, endpoint: str) -> str:
    return "{base_url}/content/{item_id}/latest/{endpoint}".format(
        base_url=base_url,
        item_id=item_id,
        endpoint=endpoint
    )


def fix_cnx_zip(zip_path):
    """Fixes a downloaded cnx zip file by removing the index.cnxml.html file.

    When a zip is uploaded that contains an index.cnxml.html file it causes an
    Integrity error during publishing. To avoid this we search the downloaded
    zip file for the index.cnxml.html file. If one is found we extract the zip
    into a temporary directory remove the file and create a new zip with
    `_fixed.zip` appended to it.

    """
    def create_zip(dir_path, archive_path):
        zip = zipfile.ZipFile(archive_path, 'w')
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                new_filepath = os.path.join(root, file)
                zip.write(new_filepath, os.path.basename(new_filepath))
        zip.close()

    # Get the name of the module zip file from the path
    zip_name = zip_path.split("/")[-1]
    module_id = zip_name.replace(".zip", "")
    new_zip_name = f"{module_id}_fixed.zip"
    new_zip_path = os.path.join(DOWNLOAD_PATH, new_zip_name)
    cnx_index_regex = re.compile(r".*/index.cnxml.html")

    zip = zipfile.ZipFile(zip_path, "r")

    # Find the directory name the zip will extract as
    temp_item = zip.namelist()[0]
    temp_dir_name = temp_item[:temp_item.find('/')]

    for filename in zip.namelist():
        if re.search(cnx_index_regex, filename):
            # Extract zip to a temp dir
            with TemporaryDirectory() as tmp_dir:
                extract_path = os.path.join(tmp_dir, temp_dir_name)
                zip.extractall(path=tmp_dir)

                # Remove the index.cnxml.html file from the archive
                os.remove(os.path.join(extract_path, "index.cnxml.html"))

                # Create a new zip with the removed file
                create_zip(extract_path, new_zip_path)

                break

    return new_zip_path

