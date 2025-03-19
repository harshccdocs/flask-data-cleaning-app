# Data Cleaning Tool - Flask Web Application

This is a simple **Flask web application** that allows users to upload CSV or Excel files, clean the data based on predefined rules, and download the cleaned data in CSV format.

### Features:
- Upload CSV or Excel files.
- Clean the data by extracting relevant fields (such as address, contact details, etc.).
- Fill missing data using available information from other columns.
- Clean phone numbers (remove leading country code "1").
- Download the cleaned data as a CSV file.

### Technologies Used:
- **Flask**: A lightweight web framework for building the web app.
- **Pandas**: A powerful library for data manipulation and cleaning.
- **Python 3.x**: The programming language used to build the application.

---

## Requirements

Before you begin, ensure you have Python 3.x installed on your system. You can check your Python version with:

```bash
python --version
