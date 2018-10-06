krunk-copy
==========

A simple python command line application that takes in a series of collection ids and checks the query_ptool for a PDF file.

If the PDF file has a timestamp it will download the file to the User's Downloads directory.

Basics
======

This tool utilizes the `query_ptool` endpoint and checks for a time in the pdf column.
If the time is displayed it will attempt to download the pdf from the pdf endpoint.

Command Line
============


    kcopy --help
    Krunk Copy: Get krunk with downloading collections from legacy.

    Usage:
      kcopy <server_url> <collection_ids>
      kcopy (-h | --help)

    Examples:
      kcopy https://legacy-devb.cnx.org 23566,23455,23456
      kcopy https://legacy-qa.cnx.org 23678
      kcopy https://legacy-devb.cnx.org "23456, 34567, 67864"

    Note:
      You may need to place quotes around collection ids because of your shell

