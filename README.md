# Penguin Scraping Backend

## Overview

The Penguin Scraping Backend is a service that handles web scraping for the PenguinLLM platform. It scrapes data from submitted websites and integrates relevant content into the PenguinLLM knowledge base.

## Features

- **Automated Web Scraping**: Scrapes all pages of websites submitted via the main PenguinLLM backend.
- **Integration with Knowledge Base**: Extracted data is sent to the PenguinLLM backend for processing and inclusion in the knowledge base.
- **Scalable Scraping**: Built using [Scrapy](https://scrapy.org/), capable of scraping large platforms like Fiverr and Upwork for extensive data gathering.

## Tech Stack

- **Web Scraping Framework**: [Scrapy](https://scrapy.org/) for scraping multiple pages of submitted websites.
- **Communication**: All API requests are handled via the main PenguinLLM backend.

## Installation and Setup

### Prerequisites

- **Python 3.9+**: Ensure Python is installed.
- **Scrapy**: Install Scrapy for handling the web scraping tasks.

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Saadmrp1038/penguin-scraping-backend.git
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Scraper

The scraping process is triggered automatically by the main PenguinLLM backend. There’s no need to manually run it unless for testing purposes.

---

This repository is part of the PenguinLLM project and works exclusively in coordination with the [PenguinLLM Backend](https://github.com/Saadmrp1038/penguin-llm-backend).

