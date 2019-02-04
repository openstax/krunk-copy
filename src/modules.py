import asyncio
import concurrent.futures
import os
import re
from tempfile import TemporaryDirectory
from typing import List, Union, Dict

from selenium.common.exceptions import NoSuchElementException

from src.constants import DOWNLOAD_PATH
from src.pages.login_form import LoginForm
from src.selenium import create_chrome_driver
from src.utils import build_url, download_file, aiohttp_get, fix_cnx_zip


async def copy_modules(from_server_url: str,
                       to_server_url: str,
                       module_ids: List,
                       headless: str,
                       username: str,
                       password: str) -> None:
    """The main controller function for copying modules to a server.

    This function combines code that is non-blocking and blocking. First, we
    create a set of tasks that downloads modules to the local machine; this is
    all non-blocking asyncio code. The results are gathered for these tasks and
    are then passed to a set of futures that will run in a
    `ThreadPoolExecutor`. This is necessary b/c that code is blocking and uses
    selenium.

    """
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    tasks = [download_module(from_server_url, module_id) for module_id in module_ids]

    modules = await asyncio.gather(*tasks)
    futures = [loop.run_in_executor(
        executor,
        copy_module_to_server,
        to_server_url,
        module["zip_path"],
        module["title"],
        headless,
        username,
        password)
        for module in modules]
    return await asyncio.wait(futures, return_when=asyncio.ALL_COMPLETED)


async def get_module_title(source_url: str, module_id: str):
    """Gets the module page and uses a regex to extract the title

    """
    module_title_regex = re.compile(r"id=\"cnx_content_title\">(\w.+)<\/")

    module_url = await build_url(source_url, module_id, "latest")
    module_page = await aiohttp_get(module_url)
    module_title = re.search(module_title_regex, module_page["text"]).group(1)
    if module_title:
        return module_title
    else:
        raise Exception(f"No title found for {module_id}")


async def download_module(source_url: str, module_id: str) -> Dict:
    """Downloads a module as a zip file to upload to another server.

    """
    print(f"downloading module id {module_id}")
    zip_url = await build_url(source_url, module_id, 'latest/module_export?format=zip')
    filename = os.path.join(module_id + ".zip")
    module_title = await get_module_title(source_url, module_id)

    zip_path = os.path.join(DOWNLOAD_PATH, filename)

    await download_file(zip_url, zip_path)
    print(f"download complete. File located at {zip_path}")

    return dict(zip_path=zip_path, title=module_title)


def copy_module_to_server(to_server_url: str,
                          zip_path: str,
                          title: str,
                          headless: str,
                          username: str,
                          password: str) -> None:
    """Copies a downloaded module zip to a server using the Chrome web browser.

    This function utilizes selenium and the Chrome webdriver to drive the
    browser as a user and upload a zip file to a CNX Legacy server. The module
    creation workflow involves a multi-part form that requires specific steps to
    be completed. The workflow goes as such.

      1. Login to the server.
      2. Select create a module.
      3. Accept license agreement. Click Next.
      4. Fill out some metadata about the module. In this case, only the title.
         Click Next.
      5. Select `zip` for module import. Select zip to be uploaded. Click Next.
      6. View uploaded content. Select Publish.
      7. Confirm publishing of the module. This step takes the longest.

    The original zip file that is downloaded contains an index.cnxml.html file
    which will cause errors during publishing. This function also created a
    fixed version where this file has been removed.

    When this process is complete the url of the completed module is printed to
    the screen.
    """
    print(f"starting the module upload process for {zip_path} to {to_server_url}")

    selenium = create_chrome_driver(headless)

    # Login to CNX Legacy
    print(f"logging into the legacy server {to_server_url} as {username}")
    login_page = LoginForm(selenium, to_server_url).open()
    my_cnx = login_page.login(username, password)

    # Go to create a module and accept the license agreement
    print(f"accepting license agreement for the module")
    cc_license = my_cnx.create_module()
    metadata_edit = cc_license.agree().submit()

    # Enter the title on the first metadata page. All other fields are left blank
    print(f"creating module with title '{title}''")
    module_edit = metadata_edit.fill_in_title(title).submit()
    module_temp_url = module_edit.current_url
    print(f"temp module located at {module_temp_url}")

    # Fix the downloaded zip by removing the index.cnxml.html file
    print(f"removing index.cnxml.html file from the downloaded module zip for upload")
    fixed_zip_path = fix_cnx_zip(zip_path)
    print(f"fixed zip saved at {zip_path}")

    # Select zip for import and upload
    print(f"uploading module zip from {fixed_zip_path} to {to_server_url}")
    module_import = module_edit.select_import_format("zip").click_import()
    module_edit = module_import.fill_in_filename(fixed_zip_path).submit()

    # Publish the imported zip file
    print(f"attempting to publish the module ...")
    content_publish = module_edit.publish()
    confirm_publish = content_publish.submit()
    try:
        content_published = confirm_publish.submit()
    except NoSuchElementException:
        raise Exception("There was no publish button found. Check that you have publish permissions")

    if content_published.title == title:
        print(f"uploaded module located at {content_published.current_url}")
    else:
        raise Exception("There was a problem with publishing the module. Review the log.")





