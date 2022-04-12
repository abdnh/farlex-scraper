"""
Scrape quizzes from The Farlex Grammar Book
"""

from typing import Dict, Tuple
import time
import random
import csv
import argparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SITE_URL = "https://www.thefreedictionary.com/"
SECTIONS = (1, 2, 3)
PAGES_DIR = Path("pages")
PAGES_DIR.mkdir(exist_ok=True)
SLEEP_RANGE = (1, 5)
USER_AGENT = "Mozilla/5.0"


def url_from_title(title: str) -> str:
    return f"{SITE_URL}/{title}.htm"


def get_soup(title) -> Tuple[BeautifulSoup, bool]:
    filename = PAGES_DIR / f"{title}.htm"
    cached = False
    if filename.exists():
        text = filename.read_text(encoding="utf-8")
        cached = True
    else:
        text = requests.get(
            url_from_title(title), headers={"User-Agent": USER_AGENT}
        ).text
        filename.write_text(text, encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")

    return soup, cached


def get_quiz(title) -> Tuple[Dict, bool]:
    print(f"Fetching quizes from {title}")
    quiz = []
    soup, cached = get_soup(title)
    quiz_questions = soup.select("#quiz > p")
    if quiz_questions:
        for q in quiz_questions:
            cur_question = {"question_text": q.get_text()[3:], "choices": []}
            next_el = q.next_element
            while next_el.name != "p":
                if next_el.name == "input" and next_el.get("type") == "radio":
                    is_correct = False
                    if "cr" in next_el.get_attribute_list("class"):
                        is_correct = True
                    cur_question["choices"].append({"is_correct": is_correct})
                elif next_el.name == "label":
                    cur_question["choices"][-1]["choice_text"] = next_el.get_text()
                next_el = next_el.next_element
            quiz.append(cur_question)
        return quiz, cached
    return None, True


def write_quiz(writer, quiz, title) -> None:
    url = url_from_title(title)
    if not quiz:
        return
    for q in quiz:
        front = q["question_text"] + "<br>"
        back = ""
        ref = f'<a href="{url}">{url}</a>'
        for c in q["choices"]:
            if c["is_correct"] == True:
                back = c["choice_text"][:2]  # The letter of the choice
            front += "<br>" + c["choice_text"]
        writer.writerow([front, back, ref])


def download_section(writer, soup: BeautifulSoup, section_id: str) -> None:
    contents = soup.select(section_id + " > div")[1]
    titles = contents.select("a")
    for i in range(len(titles)):
        title = titles[i].get("href").rsplit(".", maxsplit=1)[0]
        quiz, cached = get_quiz(title)
        if quiz:
            write_quiz(writer, quiz, title)
        if not cached:
            time.sleep(random.randint(*SLEEP_RANGE))


def main() -> None:
    QUIZZES_DIR = Path("quizzes")
    QUIZZES_DIR.mkdir(exist_ok=True)
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--page",
        help="download a specific page by its URL slug (e.g. Parts-of-Speech)",
        required=False,
    )
    g.add_argument(
        "--section",
        type=int,
        choices=SECTIONS,
        help="download a whole section by its number (1: Grammar, 2: Punctuation, 3: Spelling and Pronunciation)",
        required=False,
    )
    args = parser.parse_args()

    if args.page:
        with open(
            Path(f"{QUIZZES_DIR}/{args.page}.csv"), "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            quiz, _ = get_quiz(args.page)
            write_quiz(writer, quiz, args.page)
    else:
        soup, _ = get_soup("The-Farlex-Grammar-Book")
        if args.section:
            section_i = args.section
            section_id = f"#toc{section_i}"
            section_name = (
                soup.select_one(f"#tocTab{section_i}")
                .get_text()
                .strip()
                .replace(" ", "_")
            )
            with open(
                f"{QUIZZES_DIR}/{section_name}.csv", "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                download_section(writer, soup, section_id)
        else:
            with open(
                f"{QUIZZES_DIR}/all_quizzes.csv", "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                section_ids = [f"#toc{i}" for i in SECTIONS]
                for section_id in section_ids:
                    download_section(writer, soup, section_id)


if __name__ == "__main__":
    main()
