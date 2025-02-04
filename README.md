# Cold Email Generator-sales booster

## Overview

The **Cold Email Generator** is a Flask-based web application that
automates the creation of personalized cold emails for job
opportunities. Given a job posting URL, the system scrapes the job
details, extracts relevant information, and generates a professional
email using AI. The project integrates **Selenium**, **BeautifulSoup**,
**ChromaDB**, and **LangChain** to enhance email generation with
relevant portfolio links.

## Features

-   **Automated Job Scraping:** Extracts job descriptions, required
    skills, and responsibilities from job posting websites.
-   **Portfolio Matching:** Uses a vector database (ChromaDB) to find
    the most relevant portfolio links based on job requirements.
-   **AI-Powered Email Generation:** Utilizes **LangChain** with
    **Groq's Llama3-8b-8192** model to generate high-quality cold
    emails.
-   **Flask Web Interface:** User-friendly interface to input job URLs
    and retrieve generated emails instantly.

## Technologies Used

-   **Flask** - Web framework for handling HTTP requests.
-   **Selenium** - Automates web scraping for job postings.
-   **BeautifulSoup** - Parses and extracts job details from HTML
    content.
-   **ChromaDB** - Vector database for storing and retrieving relevant
    portfolio links.
-   **LangChain** - Framework for integrating large language models.
-   **Groq API** - Provides AI capabilities for generating email
    content.
-   **Pandas** - Handles CSV-based portfolio data.
-   **Dotenv** - Manages API keys securely.

## Installation

### Prerequisites

Ensure you have **Python 3.8+** installed and set up a virtual
environment.

``` sh
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### Install Dependencies

``` sh
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the project directory and add your API key:

``` env
GROQ_API_KEY=your_api_key_here
```

### Download ChromeDriver

Ensure **ChromeDriver** is installed and update the path in
`initialize_driver()`:

``` python
chromedriver_path = "C://path_to//chromedriver.exe"
```

## Usage

1.  **Start the Flask Server:**

    ``` sh
    python app.py
    ```

2.  **Access the Web App:** Open `http://127.0.0.1:5000/` in your
    browser.

3.  **Enter a Job URL:**

    -   The system scrapes job details.
    -   Finds relevant portfolio links.
    -   Generates a personalized cold email.

## API Endpoints

-   `GET /` - Loads the web interface.
-   `POST /process-job` - Accepts a job URL, scrapes details, fetches
    portfolio links, and returns a generated email.

## Troubleshooting

-   If **Chromedriver not found**, check and update the path in
    `initialize_driver()`.
-   If **Timeout Errors** occur, try increasing sleep time in
    `scrape_website()`.
-   If **Emails are not generated**, ensure the **Groq API key** is
    correctly set.

## Future Enhancements

-   Support for multiple job portals.
-   Improve portfolio link ranking.
-   Deploy on cloud platforms (AWS/GCP/Heroku).

## License

This project is licensed under the **MIT License**.
