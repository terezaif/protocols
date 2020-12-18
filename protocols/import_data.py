import glob
import git
import pandas as pd
import markdown
from bs4 import BeautifulSoup
from faker import Faker
import json
import re

SECRET_NAMES = "data/secret_names.txt"
PATH = "../hh-2020-ds4-daily-review/"
PATHPATTERN = "../hh-2020-ds4-daily-review/*.md"
SPLIT_AFTER = "review/"


def get_filenames(
    pathpattern: str = PATHPATTERN, split_after: str = SPLIT_AFTER
) -> list:
    mdfiles = []
    for file in glob.glob(pathpattern):
        mdfiles.append(file.split(split_after, 1)[1])
    return mdfiles


def is_exists(filename, sha, repo):
    """Check if a file in current commit exist."""
    files = repo.git.show("--pretty=", "--name-only", sha)
    if filename in files:
        return True


def get_first_author_date(filename: str, commits, repo) -> (str, str):
    file_commits = []
    for commit in commits:
        if is_exists(filename, commit.hexsha, repo):
            file_commits.append(commit)
    author = file_commits[len(file_commits) - 1].author
    authored_date = file_commits[len(file_commits) - 1].authored_date

    return author.name, authored_date


def get_text(filename: str, path: str = PATH) -> str:
    """
    reading the file, extracting the html, and then the text
    """
    file = path + "/" + filename
    secretnames = json.load(open(SECRET_NAMES))
    regex = re.compile("(%s)" % "|".join(map(re.escape, secretnames.keys())))

    with open(file) as fp:
        md = fp.read()
        html = markdown.markdown(md)
        soup = BeautifulSoup(html, features="html.parser")

    text = soup.get_text().replace("\n", " ")
    newtext = regex.sub(lambda mo: secretnames[mo.string[mo.start() : mo.end()]], text)
    return newtext


def get_gitcommits(path: str = PATH) -> list:
    repo = git.Repo(path)
    commits = list(repo.iter_commits("master"))
    fake = Faker()
    fake_names = {}
    file_history = []
    files = get_filenames()
    for filename in files:
        author, timestamp = get_first_author_date(filename, commits, repo)
        file_text = get_text(filename, path)
        fake_name = fake_names.get(author, fake.name())
        fake_names[author] = fake_name
        print(filename, author, fake_name)
        author_dict = {}
        author_dict["filename"] = filename
        author_dict["author"] = fake_name
        author_dict["date_commit"] = timestamp
        author_dict["text"] = file_text
        file_history.append(author_dict)

    return file_history, fake_names


def get_secret_names(path: str = SECRET_NAMES) -> dict:
    return json.load(open(path))


if __name__ == "__main__":
    file_history, fakes = get_gitcommits()
    df = pd.DataFrame(file_history)
    df.to_csv("data/filecommits.csv")
    f = open("data/secret.txt", "w")
    f.write(str(fakes))
    f.close()
