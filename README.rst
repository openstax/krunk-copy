krunk-copy
==========

A simple python command line application that takes in a series of collection ids or module ids and checks the query_ptool for a PDF file.

If the PDF file has a timestamp it will download the file to the User's Downloads directory.

Basics
======

This tool has two main functions.

1. downloads pdfs using the `query_ptool` endpoint to poll and download a pdf when ready.
2. copies a module from one CNX Legacy to another.

Requirements
============

- Python 3.6+
- Chrome Browser

The Chrome Browser is required for copying modules between servers.

Using an env.local file
=======================

To avoid setting environmental variables via the command line you can use a .env.local file.

First, make a copy of the `.env.example` file:

..

   cp env.local.example env.local

Fill out the file with the appropriate values.

Set the environmental variables:

..

   source .env.local

Command Line
============

    | kcopy --help

    Usage:
      | kcopy download_pdfs <server_url> (<collection_ids>...)
      | kcopy copy_modules [--headless] (<from_server_url> <to_server_url> <module_ids>...)
      | kcopy (-h | --help)

    Examples:
      | kcopy download_pdfs https://legacy-devb.cnx.org col23566 col23455 col23456
      | kcopy download_pdfs https://legacy-qa.cnx.org col23678
      | kcopy copy_modules https://legacy-devb.cnx.org  https://legacy-devb.cnx.org m25467
      | kcopy copy_modules --headless https://legacy-qa.cnx.org https://legacy-devb.cnx.org m12345
      | kcopy copy_modules https://legacy-qa.cnx.org https://legacy-devb.cnx.org m12345

    Options:
      | -h  --help    Show this screen
      | --headless    Run the Chrome driver in headless mode (w/ browser open)

    Note:
      | - All legacy credentials are set via environmental variables. Make sure you have
      |   the following environment variables set or an error will occur:
      |   $LEGACY_USERNAME
      |   $LEGACY_PASSWORD
