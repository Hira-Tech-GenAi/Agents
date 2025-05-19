# Job Application Assistant 🤖

## Overview

The **Job Application Assistant** is a tool designed to help users collect and organize their job application information, including their name, email, and skills. It uses AI to extract this information from user input and saves it in a JSON file. The project has multiple versions to suit different environments and use cases.

## Versions

There are three versions of the Job Application Assistant:

1. **Terminal-Based (Version 1)**: A simple command-line interface where users can input their details, and the assistant extracts and saves the information.
2. **Terminal-Based (Version 2)**: Another terminal-based version with slight variations in implementation (e.g., different regex patterns or features).
3. **Streamlit-Based**: A web-based interface using Streamlit, allowing users to interact via a browser and upload resumes for automatic info extraction.
4. **OpenAI Agent SDK**: An implementation using the OpenAI Agent SDK, offering advanced AI capabilities for information extraction.

## Features

- Extracts name, email, and skills from user input using regex.
- Saves extracted information to a JSON file (`application_info.json`).
- Checks for missing information and prompts the user accordingly.
- Supports both manual input and resume upload (in the Streamlit version).

## Requirements

- Python 3.8+
- Required libraries:
  - `langchain`
  - `langchain-google-genai`
  - `streamlit` (for the Streamlit version)
  - `python-dotenv`
  - `PyMuPDF` (for PDF extraction in the Streamlit version)
  - OpenAI SDK (for the OpenAI Agent version)
