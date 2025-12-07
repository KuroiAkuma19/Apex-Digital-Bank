Apex Digital Bank: A Software Engineering Project
This project is a fully functional banking application built with Python and the modern ttkbootstrap GUI framework. More than just a simple application, it served as a practical proving ground for crucial software engineering concepts:

Complexity Testing: We intentionally designed key transaction functions (like "Send Money" and "Approve Request") to have specific Cyclomatic Complexity scores, ensuring we could systematically test every possible decision path within the code.
Verification Rigor: We performed both White-Box Testing (examining internal logic and data handling) and Black-Box Testing (validating user features against defined requirements) to ensure the system is robust and reliable.
Data Persistence: The system uses local JSON and log files (users.json, transactions.log, etc.) to securely store data and track history, simulating a production environment.
AI Integration: A key feature is the Arna AI Assistant, which uses the local Ollama API to handle quick banking queries and general financial questions, adding a layer of smart interaction.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
To run the application, you need Python and a few specific tools:

1. Python Environment
Install the necessary Python libraries via pip:
   pip install ttkbootstrap requests
ttkbootstrap handles the modern, themed graphical interface.
requests is used for communication with the AI Assistant's local API.

2. AI Assistant Setup (Ollama)
For the Arna AI feature to work, the Ollama service must be running locally.

Install Ollama: Follow the installation guide for your operating system.
Download the Model: The application is configured to use a specific model. Run this command in your terminal:
   ollama pull llama3.2
Ensure Service is Active: The Ollama service must be running in the background before you launch main.py.

3. Execution Steps(Once the setup is complete)
Ensure all project files are in the same directory.
Run the main application file from your terminal:
   python main.py
Log In: Use one of the provided accounts to begin testing the application's logic:
   Username: Lance | PIN (for transactions): 2903
   Username: Shervin | PIN (for transactions): 2805


Key Scenarios for Testing
Here are a few high-value tests to demonstrate the core logic:
Validate the Approved Request: Log in as Lance to check your transaction history. The entry for the $1,000.00 request from Shervin should be logged as "Receive (Request)" and marked "Success," confirming the entire complex logic path was executed correctly.
Test the Denied State: Log in as Shervin. The dashboard should not display the request for $2,000.00 from Lance, confirming that the system correctly filtered the request marked "denied" in the pending_requests.json file.
Check Arna AI: Open the AI Assistant and ask for your "last transactions" or your "balance" to see how the system pulls internal data and presents it through the AI interface.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Thank you for taking the time to review this software engineering project. We appreciate you exploring the design choices and the verified complexity of the Apex Digital Bank.