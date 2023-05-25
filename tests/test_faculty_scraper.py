import unittest
from bs4 import BeautifulSoup
import pandas

from FacultyScraper.FacultyScraper import FacultyScraper


class FacultyScraperTests(unittest.TestCase):
    def setUp(self):
        self.scraper = FacultyScraper(
            "https://engineering.buffalo.edu/computer-science-engineering/people/faculty-directory/full-time.html")

    def test_scrape_data(self):
        data = self.scraper.scrape_data()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)

    def test_find_email_addresses(self):
        self.scraper.soup = BeautifulSoup(
            '<a href="mailto:nasrinak@buffalo.edu"></a>', "html.parser")
        self.scraper.find_email_addresses()
        expected_emails = ["nasrinak@buffalo.edu"]
        self.assertEqual(self.scraper.unique_emails, expected_emails)

    def test_validate_email_format(self):
        valid_email = "nasrinak@buffalo.edu"
        invalid_email = "invalid-email"
        self.assertTrue(self.scraper.validate_email_format(valid_email))
        self.assertFalse(self.scraper.validate_email_format(invalid_email))

    def test_clean_data(self):
        self.scraper.list_of_dicts = [
            {
                "Name": "Dr. Nasrin Akhter",
                "College": "George Mason University",
                "Email": "nasrinak@buffalo.edu",
                "Subjects": [
                    "CSE 116—Introduction to Computer Science II (Spring 2021)",
                    "CSE 191—Introduction to Discrete Structures (Fall 2023, Summer 2023, Spring 2023, Fall 2022, Summer 2022, Spring 2022, Fall 2021, Summer 2021, Spring 2021)",
                    "CSE 331—Algorithms and Complexity (Spring 2023, Spring 2022)",
                    "CSE 469—Introduction to Data Mining (Fall 2021)"
                ],
                "Research": ["Computer science education"],
                "Profile": "https://engineering.buffalo.edu//computer-science-engineering/people/faculty-directory/full-time.host.html/content/shared/engineering/computer-science-engineering/profiles/faculty/teaching/akhter-nasrin.teaching.html"
            }
        ]
        self.scraper.clean_data()
        expected_data = [
            {
                "Name": "Dr. Nasrin Akhter",
                "College": "George Mason University",
                "Email": "nasrinak@buffalo.edu",
                "Subjects": [
                    "CSE 116—Introduction to Computer Science II (Spring 2021)",
                    "CSE 191—Introduction to Discrete Structures (Fall 2023, Summer 2023, Spring 2023, Fall 2022, Summer 2022, Spring 2022, Fall 2021, Summer 2021, Spring 2021)",
                    "CSE 331—Algorithms and Complexity (Spring 2023, Spring 2022)",
                    "CSE 469—Introduction to Data Mining (Fall 2021)"
                ],
                "Research": ["Computer science education"],
                "Profile": "https://engineering.buffalo.edu//computer-science-engineering/people/faculty-directory/full-time.host.html/content/shared/engineering/computer-science-engineering/profiles/faculty/teaching/akhter-nasrin.teaching.html"
            }
        ]
        self.assertEqual(self.scraper.list_of_dicts, expected_data)

    def test_find_professors(self):
        self.scraper.soup = BeautifulSoup(
            '<span class="name">Dr. Nasrin Akhter</span>', "html.parser")
        self.scraper.find_professors()
        expected_professors = ["Dr. Nasrin Akhter"]
        self.assertEqual(self.scraper.professors, expected_professors)

    def test_find_colleges(self):
        self.scraper.soup = BeautifulSoup(
            '<span class="school">George Mason University</span>', "html.parser")
        self.scraper.find_colleges()
        expected_colleges = ["George Mason University"]
        self.assertEqual(self.scraper.colleges, expected_colleges)

    def test_find_subjects(self):
        self.scraper.soup = BeautifulSoup(
            '<p class="subjects">Subject 1, Subject 2</p>', "html.parser")
        self.scraper.find_subjects()
        expected_subjects = ["Subject 1", "Subject 2"]
        self.assertEqual(self.scraper.subjects, expected_subjects)

    def test_find_research_topics(self):
        self.scraper.soup = BeautifulSoup(
            '<p class="research">Research topic 1, Research topic 2</p>', "html.parser")
        self.scraper.find_research_topics()
        expected_research_topics = ["Research topic 1", "Research topic 2"]
        self.assertEqual(self.scraper.research_topics,
                         expected_research_topics)

    def test_find_profiles(self):
        self.scraper.soup = BeautifulSoup(
            '<a href="/profile">Profile 1</a>', "html.parser")
        self.scraper.find_profiles()
        expected_profiles = ["/profile"]
        self.assertEqual(self.scraper.profiles, expected_profiles)

    def test_extract_subjects(self):
        self.scraper.subjects = ["Subject 1", "Subject 2"]
        self.scraper.extract_subjects("https://example.com")
        expected_subjects = [
            "Subject 1",
            "Subject 2",
            "CSE 116—Introduction to Computer Science II (Spring 2021)",
            "CSE 191—Introduction to Discrete Structures (Fall 2023, Summer 2023, Spring 2023, Fall 2022, Summer 2022, Spring 2022, Fall 2021, Summer 2021, Spring 2021)",
            "CSE 331—Algorithms and Complexity (Spring 2023, Spring 2022)",
            "CSE 469—Introduction to Data Mining (Fall 2021)"
        ]
        self.assertEqual(self.scraper.subjects, expected_subjects)

    def test_extract_research_topics(self):
        self.scraper.research_topics = ["Research topic 1", "Research topic 2"]
        self.scraper.extract_research_topics("https://example.com")
        expected_research_topics = [
            "Research topic 1",
            "Research topic 2",
            "Computer science education"
        ]
        self.assertEqual(self.scraper.research_topics,
                         expected_research_topics)

    def test_dump_to_csv(self):
        filename = "faculty_data.csv"
        self.scraper.list_of_dicts = [
            {
                "Name": "Dr. Nasrin Akhter",
                "College": "George Mason University",
                "Email": "nasrinak@buffalo.edu",
                "Subjects": [
                    "CSE 116—Introduction to Computer Science II (Spring 2021)",
                    "CSE 191—Introduction to Discrete Structures (Fall 2023, Summer 2023, Spring 2023, Fall 2022, Summer 2022, Spring 2022, Fall 2021, Summer 2021, Spring 2021)",
                    "CSE 331—Algorithms and Complexity (Spring 2023, Spring 2022)",
                    "CSE 469—Introduction to Data Mining (Fall 2021)"
                ],
                "Research": ["Computer science education"],
                "Profile": "https://engineering.buffalo.edu//computer-science-engineering/people/faculty-directory/full-time.host.html/content/shared/engineering/computer-science-engineering/profiles/faculty/teaching/akhter-nasrin.teaching.html"
            }
        ]
        self.scraper.dump_to_csv(filename)
        # Perform assertions to validate the CSV file


if __name__ == "__main__":
    unittest.main()
