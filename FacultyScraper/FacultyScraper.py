from bs4 import BeautifulSoup
import requests
import concurrent.futures
import pandas as pd
import re
import logging


class FacultyScraper:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.soup = None
        self.list_of_dicts = []
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger("FacultyScraper")
        logger.setLevel(logging.ERROR)
        file_handler = logging.FileHandler("scraper.log")
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def scrape_data(self):
        try:
            self.make_request()
            self.parse_html()
            self.find_email_addresses()
            self.find_professors()
            self.check_length()
            self.find_links()
            self.create_faculty_dicts()

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                subject_futures = [executor.submit(
                    self.extract_subjects, url) for url in self.links]
                research_futures = [executor.submit(
                    self.extract_research_topics, url) for url in self.links]

                subjects_list = [
                    future.result() for future in concurrent.futures.as_completed(subject_futures)]
                research_list = [
                    future.result() for future in concurrent.futures.as_completed(research_futures)]

            for i in range(len(self.list_of_dicts)):
                self.list_of_dicts[i]["Subjects"] = subjects_list[i]
                self.list_of_dicts[i]["Research"] = research_list[i]

            self.clean_data()
            return self.list_of_dicts
        except Exception as e:
            self.logger.error("An error occurred during scraping: %s", str(e))

    def make_request(self):
        self.response = self.session.get(self.url)

    def parse_html(self):
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def find_email_addresses(self):
        email_addresses = [
            link.get("href").replace("mailto:", "")
            for link in self.soup.find_all("a", href=lambda href: href and href.startswith("mailto:"))
        ]
        self.unique_emails = []
        for mail in email_addresses:
            if mail not in self.unique_emails:
                self.unique_emails.append(mail)

    def validate_email_format(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def clean_data(self):
        unique_emails = []
        cleaned_data = []

        for faculty in self.list_of_dicts:
            email = faculty["Email"]
            if email and email not in unique_emails:
                unique_emails.append(email)
                cleaned_data.append(faculty)

        self.list_of_dicts = cleaned_data

        for faculty in self.list_of_dicts:
            email = faculty["Email"]
            if email and not self.validate_email_format(email):
                faculty["Email"] = ""

        for faculty in self.list_of_dicts:
            for key, value in faculty.items():
                if value is None:
                    faculty[key] = ""

    def find_professors(self):
        professors = self.soup.find_all(
            "div", class_="profileinfo-teaser-name")
        self.names = []
        self.prof_college = []
        for div in professors:
            name_parts = div.text.split(',')
            name = name_parts[0].strip()
            self.prof_college.append(name_parts[2].strip())
            if "PhD" in name_parts[1]:
                new_name = "Dr. " + name
                self.names.append(new_name)
            else:
                self.names.append(name)

    def check_length(self):
        self.is_length_equal = len(self.unique_emails) == len(self.names)

    def find_links(self):
        professors = self.soup.find_all(
            "div", class_="profileinfo-teaser-name")
        self.links = [
            "https://engineering.buffalo.edu/" +
            div.find('a', class_='title')['href'][:-4] + "teaching.html"
            for div in professors
        ]

    def create_faculty_dicts(self):
        for name, college, email, profile_url in zip(self.names, self.prof_college, self.unique_emails, self.links):
            faculty_dict = {
                "Name": name,
                "College": college,
                "Email": email,
                "Subjects": [],
                "Research": [],
                "Profile": profile_url
            }
            self.list_of_dicts.append(faculty_dict)

    def extract_subjects(self, url):
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            div = soup.find("div", class_="text parbase section")
            ul = div.find("ul")
            subjects = []
            try:
                for li in ul.find_all("li"):
                    subjects.append(li.text)
            except:
                pass
            return subjects
        except Exception as e:
            self.logger.error(
                "An error occurred during subject extraction: %s", str(e))

    def extract_research_topics(self, url):
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            research_topics = []
            try:
                for div in soup.find_all("div", class_="profileinfo-interest title"):
                    raw_string = div.text[15:].strip()
                    research_topics.extend(raw_string.strip().split("; "))
            except:
                pass
            return research_topics
        except Exception as e:
            self.logger.error(
                "An error occurred during research topic extraction: %s", str(e))

    def dump_to_csv(self, filename):
        df = pd.DataFrame(self.list_of_dicts)
        df.to_csv(filename, index=False)
