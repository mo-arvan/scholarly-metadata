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

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.ERROR)


def run_in_parallel_io_bound(func, iterable, max_workers=None, disable=False, **kwargs):
    """
    Run a function in parallel on a list of arguments
    :param disable: whether to disable the progress bar
    :param func: function to run
    :param iterable: list of arguments
    :param max_workers: maximum number of workers to use
    :param kwargs: keyword arguments to pass to the function
    :return: list of results
    """
    results = []
    number_of_entries = len(iterable)

    with tqdm(total=number_of_entries, disable=disable) as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_dict = {
                executor.submit(func, item, **kwargs): index
                for index, item in enumerate(iterable)
            }
            for future in concurrent.futures.as_completed(future_dict):
                results.append(future.result())
                progress_bar.update(1)
    return results


def run_in_parallel_cpu_bound(func, iterable, max_workers=None, disable=False, total=None, **kwargs):
    """
    Run a function in parallel on a list of arguments
    :param disable: whether to disable the progress bar
    :param func: function to run
    :param iterable: list of arguments
    :param max_workers: maximum number of workers to use
    :param kwargs: keyword arguments to pass to the function
    :return: list of results
    """
    results = []
    if hasattr(iterable, "len"):
        total = len(iterable)

    with tqdm(total=total, disable=disable) as progress_bar:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_dict = {
                executor.submit(func, item, **kwargs): index
                for index, item in enumerate(iterable)
            }
            for future in concurrent.futures.as_completed(future_dict):
                results.append(future.result())
                progress_bar.update(1)
    return results


def download_paper(info_tuple, headers, download_dir):
    """
    Download the paper from the interspeech conference.

    Args:
        url (str): The url of the paper.
    """
    conference, year, url = info_tuple
    file_name = url.split('/')[-1]

    download_dir_with_year = os.path.join(
        download_dir, f'{conference.lower()}_{year}')
    download_path = os.path.join(download_dir_with_year, file_name)
    if not os.path.exists(download_dir_with_year):
        os.makedirs(download_dir_with_year)

    if os.path.exists(download_path):
        return

    # download pdf file and save it in to a file
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        logging.info(f"Failed to download {url}")
        return
    with open(download_path, 'wb') as f:
        f.write(r.content)


def download_papers(url_list, download_dir):
    """
    Download the papers from the interspeech conference.

    Args:
        url_list (list): A list of paper urls.
    """
    headers = requests.utils.default_headers()

    download_fn = partial(download_paper, headers=headers,
                          download_dir=download_dir)

    run_in_parallel_io_bound(download_fn, url_list,
                             max_workers=24, disable=False)


def main():

    start_time = time.perf_counter()

    download_dir = 'papers'

    neurips_papers = pd.read_csv("results/neurips_papers.csv")
    interspeech_papers = pd.read_csv("results/interspeech_papers.csv")

    papers_url_list = []

    papers_url_list.extend(
        neurips_papers[["conference", "year", "Paper"]].to_records(index=False))

    papers_url_list.extend(
        interspeech_papers[["conference", "year", "url"]].to_records(index=False))

    download_papers(papers_url_list, download_dir)

    logger.info(f"Found {len(interspeech_papers)} papers.")
    return
    search_papers(download_dir, 'github.com')

    end_time = time.perf_counter()
    logger.info(f"Finished in {end_time - start_time} seconds")


if __name__ == '__main__':
    main()


def search_pdf(paper_path, search_term):
    """
    Search the paper for a search term.

    Args:
        paper_path (str): The path of the paper.
        search_term (str): The term to search for.
    """
    try:

        pdfReader = PyPDF2.PdfReader(paper_path)
        all_pages_text = "\n".join(
            [page.extract_text() for page in pdfReader.pages])

        all_pages_text = all_pages_text.replace('-\n', '')

        r = re.search(r"\d\.\s*Reference", all_pages_text)
        if r is not None:
            references_start = r.start()
        else:
            references_start = len(all_pages_text)

        text_excluding_references = all_pages_text[:references_start]
        return paper_path, search_term in text_excluding_references
    except Exception as e:
        logger.info(f"Failed to search {paper_path} for {search_term}")
        return paper_path, None


def search_papers(papers_dir, search_term):
    """
    Search the papers for a search term.

    Args:
        papers_dir (str): The directory containing the papers.
        search_term (str): The term to search for.
    """
    # get full path of all files in the papers directory including subdirectories
    all_files = []
    for root, dirs, files in os.walk(papers_dir):
        for file in files:
            if file.endswith('.pdf'):
                all_files.append(os.path.join(root, file))

    search_fn = partial(search_pdf, search_term=search_term)

    result = run_in_parallel_cpu_bound(search_fn, all_files,
                                       max_workers=16, disable=False)

    results_searched = [r for r in result if r]

    results_with_code = [r[0] for r in results_searched if r[1]]

    results_df = pd.DataFrame(result, columns=["file_path", "contains"])

    results_df.to_csv('results/interspeech.csv')
    logger.info(
        f"Found {len(results_with_code)} papers with code. out of {len(results_searched)} papers.")
