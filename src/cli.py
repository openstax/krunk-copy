"""Krunk Copy: Get krunk with copying modules or downloading PDFs from CNX Legacy.
Usage:
  kcopy download_pdfs <server_url> (<collection_ids>...)
  kcopy copy_modules [--headless] (<from_server_url> <to_server_url> <module_ids>...)
  kcopy (-h | --help)

Examples:
  kcopy download_pdfs https://legacy-devb.cnx.org col23566 col23455 col23456
  kcopy download_pdfs https://legacy-qa.cnx.org col23678
  kcopy copy_modules https://legacy-devb.cnx.org  https://legacy-devb.cnx.org m25467
  kcopy copy_modules --headless https://legacy-qa.cnx.org https://legacy-devb.cnx.org m12345

Options:
  -h  --help    Show this screen
  --headless    Run the Chrome driver in headless mode

Note:
  - All legacy credentials are set via environmental variables. Make sure you have
    the following environment variables set or an error will occur:
      $LEGACY_USERNAME
      $LEGACY_PASSWORD
"""
import asyncio
import os
import sys
from datetime import datetime

from docopt import docopt

from src.modules import copy_modules
from src.pdfs import download_pdfs


def cli():
    arguments = docopt(__doc__)

    # Assign commands to variables
    pdfs = arguments["download_pdfs"]
    module = arguments["copy_modules"]

    # Assign arguments to variables
    server_url = arguments["<server_url>"]
    col_ids = arguments["<collection_ids>"]
    module_ids = arguments["<module_ids>"]
    to_server_url = arguments["<to_server_url>"]
    from_server_url = arguments["<from_server_url>"]

    # Assign options to variables
    headless = arguments["--headless"]

    if pdfs:
        print(f"Polling and downloading PDFs for {col_ids} at {server_url}")
        print(f"Started at: {datetime.utcnow()}")
        try:
            asyncio.run(download_pdfs(server_url, col_ids))
        except KeyboardInterrupt:
            pass

    if module:

        try:
            username = os.environ["LEGACY_USERNAME"]
            password = os.environ["LEGACY_PASSWORD"]
        except KeyError:
            print("You need to set LEGACY_USERNAME and LEGACY_PASSWORD environment variables")
            sys.exit()

        print(f"Initiating the module zip download and copy process for {module_ids}")
        print(f"Started at: {datetime.utcnow()}")

        try:
            asyncio.run(copy_modules(from_server_url, to_server_url, module_ids, headless, username, password))
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    cli()
