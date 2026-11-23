# Personal Expense Tracker & Visualization



A Python-based personal finance analytics application that processes financial transactions, automatically categorizes expenses, monitors monthly budgets, generates visualizations, and exports financial reports.



The project demonstrates practical skills in Python programming, data analysis, database management, automation, financial reporting, and interactive dashboard development.



## Project Overview



The Personal Expense Tracker & Visualization project helps users understand their income, expenses, savings, and spending habits through automated financial analysis.



It uses SQLite for transaction storage, pandas for data processing, Matplotlib and Seaborn for visualizations, and Streamlit for an interactive financial dashboard.



## Key Features



\- CSV transaction ingestion and data validation

\- Automatic transaction categorization using keyword-based rules

\- SQLite database for storing financial records

\- Monthly income, expense, and savings analysis

\- Category-wise spending analysis

\- Monthly and daily spending trends

\- Payment-method visualizations

\- Monthly budget tracking and overspending alerts

\- Cumulative spending versus budget visualization

\- Interactive Streamlit dashboard

\- CSV financial report generation

\- Excel financial reporting with multiple worksheets

\- Month-specific Excel report exports

\- Automated testing using pytest



## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Application development |

| pandas | Financial data processing |

| SQLite | Transaction and budget storage |

| Matplotlib | Financial charts |

| Seaborn | Statistical visualizations |

| Streamlit | Interactive dashboard |

| Plotly | Interactive dashboard charts |

| XlsxWriter | Excel report formatting |

| openpyxl | Excel file validation |

| pytest | Automated testing |



## Project Structure



```text

Personal-Expense-Tracker-Visualization/

â”œâ”€â”€ data/

â”œâ”€â”€ db/

â”œâ”€â”€ images/

â”œâ”€â”€ outputs/

â”œâ”€â”€ src/

â”‚   â”œâ”€â”€ analyze.py

â”‚   â”œâ”€â”€ app\_streamlit.py

â”‚   â”œâ”€â”€ budget.py

â”‚   â”œâ”€â”€ categorize.py

â”‚   â”œâ”€â”€ generate\_sample\_data.py

â”‚   â”œâ”€â”€ ingest.py

â”‚   â”œâ”€â”€ models.py

â”‚   â”œâ”€â”€ plots.py

â”‚   â””â”€â”€ report.py

â”œâ”€â”€ tests/

â”‚   â”œâ”€â”€ test\_database.py

â”‚   â”œâ”€â”€ test\_ingest.py

â”‚   â””â”€â”€ test\_categorize.py

â”œâ”€â”€ main.py

â”œâ”€â”€ requirements.txt

â””â”€â”€ README.md

```



## Installation and Setup



### 1. Clone the repository



```bash

git clone YOUR\_REPOSITORY\_URL

cd Personal-Expense-Tracker-Visualization

```



Replace `YOUR\_REPOSITORY\_URL` with the actual GitHub repository URL after publishing.



### 2. Create a virtual environment



```powershell

python -m venv .venv

```



### 3. Install dependencies



On Windows PowerShell, use the virtual environment's Python executable directly:



```powershell

.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



## Running the Application



Launch the interactive Streamlit dashboard:



```powershell

.\\.venv\\Scripts\\python.exe -m streamlit run src/app\_streamlit.py

```



Open the local address displayed by Streamlit in your browser.



## Financial Visualizations



The application generates the following visualizations:



1\. Category-wise expense analysis

2\. Monthly spending trends

3\. Payment-method distribution

4\. Daily spending trends

5\. Cumulative spending versus budget



Generate the standard charts:



```powershell

.\\.venv\\Scripts\\python.exe -m src.plots

```



## Financial Reporting



Generate monthly financial reports:



```powershell

.\\.venv\\Scripts\\python.exe -m src.report

```



The reporting module generates:



\- `outputs/financial\_report.csv`

\- `outputs/financial\_report.xlsx`



The Excel workbook includes:



\- Monthly Summary

\- Transactions

\- Category Summary



A month-specific report can also be generated using the `export\_month` function.



## Budget Monitoring



The application compares spending against monthly category budgets and identifies:



\- Categories within budget

\- Categories approaching their budget limits

\- Categories exceeding their allocated budgets



## Automated Testing



Run the complete automated test suite:



```powershell

.\\.venv\\Scripts\\python.exe -m pytest -v

```



Verified testing results on November 23, 2026:



\*\*25 tests passed, 0 failed.\*\*



The tests cover database integrity, CSV ingestion, and transaction categorization.



Check dependency integrity:



```powershell

.\\.venv\\Scripts\\python.exe -m pip check

```



Verified result: No broken requirements found.



## Demonstration Results



The project was tested using sample financial data covering September through November 2026.



| Financial Metric | Value |

|---|---:|

| Total Income | â‚¹45,000 |

| Total Expenses | â‚¹17,873 |

| Net Savings | â‚¹27,127 |

| Savings Rate | 60.28% |

| Transactions | 30 |

| Months Analyzed | 3 |



These figures are demonstration results from sample data, not real financial records.



## Screenshots



Screenshots of the Streamlit dashboard, budget alerts, financial charts, and generated reports can be added here after the repository is prepared.



## Skills Demonstrated



\- Python programming

\- Data cleaning and validation

\- SQL and relational databases

\- Rule-based transaction classification

\- Financial data analysis

\- Data visualization

\- Dashboard development

\- Excel and CSV automation

\- Automated software testing

\- Modular project architecture



## Future Improvements



Potential future enhancements include:



\- Machine-learning-based transaction categorization

\- Forecasting future expenses

\- Personalized spending recommendations

\- Additional interactive filters

\- User authentication

\- Cloud deployment



## Project Status



The core application, financial reporting, visualizations, and automated test suite have been implemented and tested locally.



GitHub publication and final repository documentation checks are pending.



## Disclaimer



This project is intended for educational, demonstration, and portfolio purposes. Financial data used in demonstrations is synthetic or sample data.
