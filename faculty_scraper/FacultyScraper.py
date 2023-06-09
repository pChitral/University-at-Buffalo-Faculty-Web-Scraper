from bs4 import BeautifulSoup
import requests
import concurrent.futures
import pandas as pd
import re
import logging


class FacultyScraper:
    """
    A web scraping tool to extract data from a faculty directory website.

    Attributes:
        url (str): The URL of the faculty directory website.
        session (requests.Session): A session object to handle HTTP requests.
        soup (BeautifulSoup): A BeautifulSoup object to parse HTML content.
        list_of_dicts (list): A list of dictionaries containing faculty information.

    Methods:
        scrape_data(): Scrapes the data from the faculty directory website.
        make_request(): Sends an HTTP request to the specified URL.
        parse_html(): Parses the HTML content of the response.
        find_email_addresses(): Finds and stores the email addresses of faculty members.
        find_professors(): Finds and stores the names and colleges of faculty members.
        check_length(): Checks if the number of unique emails matches the number of faculty names.
        find_links(): Finds and stores the profile links of faculty members.
        create_faculty_dicts(): Creates faculty dictionaries with basic information.
        extract_subjects(): Extracts and stores the subjects taught by each faculty member.
        extract_research_topics(): Extracts and stores the research topics of each faculty member.
    """

    def __init__(self, url):
        """
        Initializes a FacultyScraper object.

        Args:
            url (str): The URL of the faculty directory website.
        """
        self.url = url
        self.session = requests.Session()
        self.soup = None
        self.list_of_dicts = []
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """
        Sets up a logger for error handling and logging.

        Returns:
            logging.Logger: The configured logger object.
        """
        logger = logging.getLogger("FacultyScraper")
        logger.setLevel(logging.ERROR)

        # Define log file handler
        file_handler = logging.FileHandler("scraper.log")
        file_handler.setLevel(logging.ERROR)

        # Define log message format
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add file handler to logger
        logger.addHandler(file_handler)

        return logger

    def scrape_data(self):
        """
        Scrapes the data from the faculty directory website.

        Returns:
            list: A list of dictionaries containing faculty information.
        """
        try:
            self.make_request()
            self.parse_html()
            self.find_email_addresses()
            self.find_professors()
            self.check_length()
            self.find_links()
            self.create_faculty_dicts()

            # Create a ThreadPoolExecutor with maximum threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Execute extract_subjects and extract_research_topics concurrently
                subject_futures = [executor.submit(
                    self.extract_subjects, url) for url in self.links]
                research_futures = [executor.submit(
                    self.extract_research_topics, url) for url in self.links]

                # Retrieve the results from the futures
                subjects_list = [
                    future.result() for future in concurrent.futures.as_completed(subject_futures)]
                research_list = [
                    future.result() for future in concurrent.futures.as_completed(research_futures)]

            # Update the subjects and research topics in the faculty dictionaries
            for i in range(len(self.list_of_dicts)):
                self.list_of_dicts[i]["Subjects"] = subjects_list[i]
                self.list_of_dicts[i]["Research"] = research_list[i]

            return self.list_of_dicts
        except Exception as e:
            self.logger.error("An error occurred during scraping: %s", str(e))

    def make_request(self):
        """
        Sends an HTTP request to the specified URL.
        """
        self.response = self.session.get(self.url)

    def parse_html(self):
        """
        Parses the HTML content of the response.
        """
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def find_email_addresses(self):
        """
        Finds and stores the email addresses of faculty members.
        """
        email_addresses = [
            link.get("href").replace("mailto:", "")
            for link in self.soup.find_all("a", href=lambda href: href and href.startswith("mailto:"))
        ]
        self.unique_emails = []
        for mail in email_addresses:
            if mail not in self.unique_emails:
                self.unique_emails.append(mail)

    def validate_email_format(self, email):
        """
        Validates if an email address is in the correct format.

        Args:
            email (str): Email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def clean_data(self):
        """
        Cleans the scraped data by removing duplicates and handling missing values.
        """
        unique_emails = []
        cleaned_data = []

        for faculty in self.list_of_dicts:
            email = faculty["Email"]
            if email and email not in unique_emails:
                unique_emails.append(email)
                cleaned_data.append(faculty)

        self.list_of_dicts = cleaned_data

        # Validate and clean email addresses
        for faculty in self.list_of_dicts:
            email = faculty["Email"]
            if email and not self.validate_email_format(email):
                faculty["Email"] = ""

        # Handle missing values
        for faculty in self.list_of_dicts:
            for key, value in faculty.items():
                if value is None:
                    faculty[key] = ""

    def find_professors(self):
        """
        Finds and stores the names and colleges of faculty members.
        """
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
        """
        Checks if the number of unique emails matches the number of faculty names.
        """
        self.is_length_equal = len(self.unique_emails) == len(self.names)

    def find_links(self):
        """
        Finds and stores the profile links of faculty members.
        """
        professors = self.soup.find_all(
            "div", class_="profileinfo-teaser-name")
        self.links = [
            "https://engineering.buffalo.edu/" +
            div.find('a', class_='title')['href'][:-4] + "teaching.html"
            for div in professors
        ]

    def create_faculty_dicts(self):
        """
        Creates faculty dictionaries with basic information.
        """
        for name, college, email, profile_url in zip(self.names, self.prof_college, self.unique_emails, self.links):
            faculty_dict = {
                "Name": name,
                "College": college,
                "Email": email,
                "Subjects": [],
                "Research": [],
                "Profile": profile_url  # Add the 'Profile' key with the URL
            }
            self.list_of_dicts.append(faculty_dict)

    def extract_subjects(self, url):
        """
        Extracts and returns the subjects taught by a faculty member.

        Args:
            url (str): The URL of the faculty member's profile page.

        Returns:
            list: A list of subjects taught by the faculty member.
        """
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
        """
        Extracts and returns the research topics of a faculty member.

        Args:
            url (str): The URL of the faculty member's profile page.

        Returns:
            list: A list of research topics of the faculty member.
        """
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
        """
        Dumps the scraped data to a CSV file.

        Args:
            filename (str): The name of the CSV file.
        """
        df = pd.DataFrame(self.list_of_dicts)
        df.to_csv(filename, index=False)

    def return_df(self,):
        """
        Returns the data in a pandas dataframe. 
        """
        df = pd.DataFrame(self.list_of_dicts)
        return df
