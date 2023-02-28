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
import seaborn as sns
import numpy as np
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.ERROR)


def main():

    results_df = pd.read_csv('results.csv', index_col=0)

    results_df = results_df.loc[np.logical_not(
        pd.isnull(results_df["contains"]))]

    results_df["year"] = results_df["file_path"].apply(
        lambda x: int(x.split("/")[1].split("_")[1]))

    results_grouped = results_df[["year", "contains"]].groupby(
        ["year", "contains"]).size().reset_index(name="count")

    # results_grouped.plot(x="year", y="count", kind="bar").get_figure().savefig(
    #     "results.png")
    print(results_grouped.head())

    # submissions_with_code_plot = sns.relplot(data=agg_result,
    #                                          x="year",
    #                                          y="submissions_with_code",
    #                                          hue="conference",
    #                                          style="conference",
    #                                          markers=True,
    #                                          kind="line",
    #                                          facet_kws={'legend_out': True}) \
    #     .set(xlabel="Year", ylabel="# Published Papers with Code")
    # submissions_with_code_plot._legend.set_title('Conference')
    ratio_list = []
    for r in results_grouped["year"].unique():
        total = results_grouped.loc[results_grouped["year"]
                                    == r]["count"].sum()
        only_with_code = results_grouped.loc[np.logical_and(results_grouped["year"] == r,
                                                            results_grouped["contains"] == True)]["count"].sum()
 
        ratio_list.append((r, only_with_code * 100 / total))

    ratio_df = pd.DataFrame(ratio_list, columns=["year", "ratio"])
    sns.set()

    results_grouped.plot(kind="bar", stacked=True, x="year", y="count", color="contains",
                         ).get_figure().savefig("results.png")

    # submission_with_code_ration_plot = sns.catplot(data=results_grouped,
    #                                                x="year",
    #                                                y="count",
    #                                                hue="contains",
    #                                                #    style="contains",
    #                                                #    markers=True,
    #                                                stacked=True,
    #                                                kind="bar",
    #                                                facet_kws={'legend_out': True}) \
    #     .set(xlabel="Year", ylabel="% Published Papers with Code")
    # # submission_with_code_ration_plot._legend.set_title('Conference')
    # submission_with_code_ration_plot.savefig("results" + ".png")
    # submission_with_code_ration_plot.savefig("results" + ".svg")
    # pdfFileObj = open('sample.pdf', 'rb')
    # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    # pageObj = pdfReader.getPage(0)
    # print(pageObj.extractText())


if __name__ == '__main__':
    sns.set_theme()
    sns.set_style("darkgrid")
    main()
