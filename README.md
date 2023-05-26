# Faculty Scraper

Faculty Scraper is a Python web scraping tool designed to extract data from a faculty directory website. It retrieves information such as faculty names, colleges, email addresses, subjects taught, and research topics. The scraped data is stored in a list of dictionaries and can be exported to a CSV file for further analysis. For those interested in a more in-depth understanding, I highly recommend reading my article: [Medium Link](https://chitralpatil.medium.com/web-scraping-with-python-a-comprehensive-guide-to-extracting-faculty-data-and-boosting-performance-49bc9e2341b5). It covers the code implementation, step-by-step explanations, and the benefits of utilizing concurrent features for efficient data extraction.

## Dependencies

The following Python packages are required to run the scraper:

- `bs4` (BeautifulSoup): Used for HTML parsing.
- `requests`: Used for sending HTTP requests.
- `concurrent.futures`: Used for concurrent execution of scraping tasks.
- `pandas`: Used for data manipulation and CSV export.
- `re`: Used for email address validation.
- `logging`: Used for error handling and logging.

## Usage

1. Import the `FacultyScraper` class from the `faculty_scraper.FacultyScraper` module.

   ```python
   from faculty_scraper.FacultyScraper import FacultyScraper
   ```

2. Create an instance of the `FacultyScraper` class with the URL of the faculty directory website.

   ```python
   url = "https://example.com/faculty-directory"
   scraper = FacultyScraper(url)
   ```

3. Scrape the data from the faculty directory website.

   ```python
   data = scraper.scrape_data()
   ```

4. Dump the scraped data into a CSV file.

   ```python
   scraper.dump_to_csv("faculty_data.csv")
   ```

5. Retrieve the scraped data as a Pandas DataFrame.

   ```python
   df = scraper.return_df()
   ```

## Contributing

Contributions are welcome! If you would like to contribute to Faculty Scraper, follow these steps:

1. Fork the repository.

2. Create a new branch for your feature or bug fix.

3. Make your changes in the branch.

4. Commit your changes with descriptive commit messages.

5. Push your branch to your forked repository on GitHub.

6. Open a pull request from your branch to the main repository.

7. Provide a clear and descriptive title for your pull request, along with a detailed description of the changes you have made.

8. Wait for the project maintainers to review your pull request. They may provide feedback or ask for additional changes.

9. Once your pull request is approved and merged, your changes will become a part of the project.

Please note that by contributing to this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Example

Here's an example that demonstrates the usage of the `FacultyScraper` class:

```python
from faculty_scraper.FacultyScraper import FacultyScraper

url = "https://engineering.buffalo.edu/computer-science-engineering/people/faculty-directory/full-time.html"
scraper = FacultyScraper(url)
data = scraper.scrape_data()

scraper.dump_to_csv("Department of Computer Science and Engineering Faculty Data.csv")
df = scraper.return_df()
```
In this example, the `FacultyScraper` is initialized with the URL of the faculty directory website. The `scrape_data()` method is called to extract the faculty information, which is then dumped into a CSV file named `"Department of Computer Science and Engineering Faculty Data.csv"`. The scraped data is also returned as a Pandas DataFrame for further analysis.

Note: The current implementation of the scraper is specifically designed for the URL: "https://engineering.buffalo.edu/computer-science-engineering/people/faculty-directory/full-time.html". If you want to scrape a different faculty directory website, you will need to modify the code accordingly referer the steps at [Contributing](https://github.com/pChitral/University-at-Buffalo-Faculty-Web-Scraper#contributing).
