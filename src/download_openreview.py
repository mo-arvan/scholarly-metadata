import openreview
import time
import logging
import argparse
import os
import pandas as pd
import PyPDF2
import requests
import requests.utils
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import re
from multiprocessing import Pool
from functools import partial
import concurrent.futures
import pandas as pd
import logging

import time

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager


# https://github.com/Lionelsy/Conference-Accepted-Paper-List


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)



def main():
    start_time = time.perf_counter()

    neurips_papers = get_neurips_papers(2015, 2023)

    print("Done")

    # if 'OPENREVIEW_USERNAME' not in os.environ or 'OPENREVIEW_PASSWORD' not in os.environ:
    #     logger.error(
    #         "Please set the environment variables OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD")
    #     return

    # openreview_username, openreview_password = os.environ[
    #     "OPENREVIEW_USERNAME"], os.environ["OPENREVIEW_PASSWORD"]

    # client = openreview.Client(baseurl='https://api.openreview.net',
    #                            username=openreview_username, password=openreview_password)

    # conference_list = ["ICLR.cc",
    #                    #    "ICML.cc",
    #                    #    "NeurIPS.cc"
    #                    ]
    # start_year = 2018
    # end_year = 2023
    # results_dict = {}
    # for conference in conference_list:
    #     for year in range(start_year, end_year):
    #         conference_id = f"{conference}/{year}/Conference"
    #         notes = client.get_all_notes(
    #             signature=conference_id)
    #         results_dict[(conference, year)] = notes

    # def get_note_dict(conference_year, note):
    #     note_dict = note.content
    #     note_dict["conference"] = conference_year[0]
    #     note_dict["year"] = conference_year[1]
    #     return note_dict
    # papers = []
    # starting_year = 2018
    # ending_year = 2023
    # headers = requests.utils.default_headers()
    # for year in range(starting_year, ending_year + 1):
    #     url = f'https://openreview.net/group?id=ICLR.cc/{year}/Conference'
    #     r = requests.get(url, headers=headers)
    #     soup = BeautifulSoup(r.text, 'html.parser')

    #     # find all elemnts with class 'paper'
    #     paper_urls = soup.find_all('a', class_='w3-text')

    #     # get the href attribute of each element
    #     paper_urls = [year + "/" + paper['href'].replace('html', 'pdf')
    #                   for paper in paper_urls if paper['href'].endswith('html')]

    #     # for paper_url in paper_urls:
    #     #     paper = get_paper(paper_url)
    #     #     papers.append(paper)
    #     papers.extend(paper_urls)

    # final_result = []
    # for conference_year, notes in results_dict.items():
    #     final_result.extend([get_note_dict(conference_year, note)
    #                         for note in notes])

    # invite_list = r = client.get_all_invitations(
    #     regex=r"ICLR.cc/\d+/(c|C)onference/-/\w*(s|S)ubmission")
    # # selected_venues = ["ICLR.cc", "ICML.cc", "NeurIPS.cc"]

    # notes = client.get_all_notes(invitation=invite_list[0].id)
    # for note in notes:
    #     print(note.content['title'])

    # for note in groups:
    #     print(note.content['title'])

    end_time = time.perf_counter()

    logger.info(f"Total time: {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
