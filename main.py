import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
import json
import os
import random
import datetime 
from tkinter import scrolledtext 
from tkinter.ttk import Treeview 
import requests # For making API calls to Ollama

# Constants
DATA_FILE = "users.json"
TRANSACTION_LOG_FILE = "transactions.log" 
REQUESTS_FILE = "pending_requests.json" 
CURRENCY = "USD"
MINIMUM_BALANCE = 1000
DEFAULT_STARTING_BALANCE = 500000

# OLLAMA Configuration (Ensure Ollama is running locally)
OLLAMA_API_URL = "http://localhost:11434/api/generate" 
OLLAMA_MODEL = "qwen2.5" # Change to your preferred model

WEALTH_TIERS = [
    (10000000000000, "You have truly ascended the Matrix..."),
    (10000000000, "What color is your Bugatti today?"),
    (10000000, "Buss itna paisa chaiye zindagi main"),
]

# File handling and utility functions

def load_data(file_path):
    """Loads a JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                content = f.read()
                return json.loads(content) if content else {}
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(data, file_path):
    """Saves data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def generate_account_number(data):
    while True:
        acc_no = str(random.randint(100000, 999999))
        if all(user.get("account_no") != acc_no for user in data.values()):
            return acc_no

def generate_request_id(requests_data):
    """Generates a unique ID for a new request."""
    while True:
        req_id = f"req_{int(datetime.datetime.now().timestamp())}{random.randint(100,999)}"
        if req_id not in requests_data:
            return req_id

# Log Transaction function
def log_transaction(acc_no, type, amount, status, target_acc_no=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "account_no": acc_no,
        "type": type,
        "amount": amount,
        "status": status,
        "target_acc_no": target_acc_no
    }
    
    logs = load_data(TRANSACTION_LOG_FILE)
    if not isinstance(logs, list):
        logs = []
        
    logs.append(log_entry)
    save_data(logs, TRANSACTION_LOG_FILE)


# Main Application Class
class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apex Digital Bank")
        self.root.geometry("1100x900") 
        self.data = load_data(DATA_FILE)
        self.current_user = None
        self.current_acc_no = None
        
        self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_frame(self, title, back_command=None):
        self.clear_screen()
        frame = ttk.Frame(self.root, padding=40) 
        frame.pack(expand=True, fill="both", padx=50, pady=50) 

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        if back_command:
            ttk.Button(frame, text="< Back", bootstyle="link-light", command=back_command).grid(
                row=0, column=0, columnspan=2, pady=(0, 20), sticky="nw"
            )
            title_row = 1
        else:
            title_row = 0

        # Text color is now handled by the theme
        ttk.Label(frame, text=title, font=("Arial", 24, "bold")).grid( 
            row=title_row, column=0, columnspan=2, pady=(10, 40), sticky="n"
        )
        return frame

    def _add_input(self, frame, label_text, row, show=None):
        # Text color is now handled by the theme
        ttk.Label(frame, text=label_text, font=("Arial", 12, "bold")).grid( 
            row=row, column=0, pady=10, sticky="w", padx=10
        )
        entry = ttk.Entry(frame, width=30, show=show, font=("Arial", 12))
        entry.grid(row=row, column=1, pady=10, sticky="w", padx=10)
        return entry

    # Login/Signup/Dashboard Methods

    def show_login(self):
        frame = self.setup_frame("Access Your Account")
        
        center_frame = ttk.Frame(frame, padding=30)
        center_frame.grid(row=2, column=0, columnspan=2, sticky="n")
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)
        
        self.login_user = self._add_input(center_frame, "Username:", 0)
        self.login_pass = self._add_input(center_frame, "Password:", 1, show="*")

        ttk.Button(center_frame, text="LOG IN", bootstyle="primary", command=self.login, padding=12).grid(
            row=2, column=0, columnspan=2, pady=(30, 15), sticky="ew"
        )
        ttk.Button(center_frame, text="Create New Account", bootstyle="info-outline", command=self.show_signup, padding=10).grid(
            row=3, column=0, columnspan=2, pady=10, sticky="ew"
        )

    def login(self):
        username = self.login_user.get()
        password = self.login_pass.get()
        
        self.data = load_data(DATA_FILE) 

        if username in self.data and self.data[username].get("password") == password:
            self.current_user = username
            self.current_acc_no = self.data[username].get("account_no")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_signup(self):
        frame = self.setup_frame("New User Registration", back_command=self.show_login)

        center_frame = ttk.Frame(frame, padding=30)
        center_frame.grid(row=2, column=0, columnspan=2, sticky="n")
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)

        self.signup_user = self._add_input(center_frame, "Choose Username:", 0)
        self.signup_pass = self._add_input(center_frame, "Create Password:", 1, show="*")
        self.signup_pin = self._add_input(center_frame, "4-Digit PIN (for Transactions):", 2, show="*")

        ttk.Button(center_frame, text="REGISTER", bootstyle="success", command=self.signup, padding=12).grid(
            row=3, column=0, columnspan=2, pady=(30, 15), sticky="ew"
        )

    def signup(self):
        username = self.signup_user.get()
        password = self.signup_pass.get()
        pin = self.signup_pin.get()

        if username in self.data:
            messagebox.showerror("Error", "Username already exists!")
            return
        if not pin.isdigit() or len(pin) != 4:
            messagebox.showerror("Error", "PIN must be exactly 4 digits")
            return

        acc_no = generate_account_number(self.data)
        self.data[username] = {
            "password": password, "pin": pin, 
            "balance": DEFAULT_STARTING_BALANCE, "account_no": acc_no
        }
        save_data(self.data, DATA_FILE)
        messagebox.showinfo("Success", f"Account created!\nAccount No: {acc_no}")
        self.show_login()

    def show_dashboard(self):
        frame = self.setup_frame("Account Dashboard")
        
        # Refresh data
        self.data = load_data(DATA_FILE)
        if self.current_user not in self.data:
            messagebox.showerror("Error", "User data not found. Logging out.")
            self.show_login()
            return
            
        balance = self.data[self.current_user].get("balance", 0)
        
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=2)
        
        details_frame = ttk.Frame(frame, padding=30, bootstyle="secondary-toolwindow") 
        details_frame.grid(row=2, column=0, padx=20, pady=15, sticky="nsew")
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)

        # Labels will now be visible on dark theme
        ttk.Label(details_frame, text=f"Welcome, {self.current_user}", font=("Arial", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10), sticky="w"
        )
        ttk.Label(details_frame, text=f"Account No: {self.current_acc_no}", font=("Arial", 14)).grid(
            row=1, column=0, columnspan=2, pady=5, sticky="w"
        )
        ttk.Separator(details_frame, bootstyle="light").grid(row=2, column=0, columnspan=2, sticky="ew", pady=20)

        ttk.Label(details_frame, text="Current Balance", font=("Arial", 16, "bold")).grid(
            row=3, column=0, pady=(10, 0), sticky="w"
        )
        self.balance_label = ttk.Label(
            details_frame, 
            text=self._format_currency(balance), 
            font=("Arial", 22, "bold"), 
            bootstyle="success" 
        )
        self.balance_label.grid(row=4, column=0, columnspan=2, pady=(5, 10), sticky="w")
        
        buttons_frame = ttk.Frame(frame, padding=10)
        buttons_frame.grid(row=2, column=1, padx=20, pady=15, sticky="nsew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(buttons_frame, text="Available Transactions", font=("Arial", 18, "bold")).grid(
            row=0, column=0, pady=(10, 25), sticky="n"
        )
        
        buttons = [
            ("Deposit Funds", "success", self.show_deposit_page),
            ("Withdraw Funds", "primary", self.show_withdraw_page),
            ("Send Money", "info", self.show_send_money_page), 
            ("Request Money", "warning", self.show_request_money_page),
            ("Transaction History/Statements", "secondary", self.show_statements_page)
        ]
        
        button_row = 1
        for (text, style, cmd) in buttons:
            ttk.Button(buttons_frame, text=text, bootstyle=style, command=cmd, padding=12).grid(
                row=button_row, column=0, pady=10, sticky="ew"
            )
            button_row += 1
            
        
        all_requests = load_data(REQUESTS_FILE)
        pending_for_me = []
        if isinstance(all_requests, dict):
            pending_for_me = [
                req for req in all_requests.values() 
                if req.get('source_acc_no') == self.current_acc_no and req.get('status') == 'pending'
            ]
        
        if pending_for_me:
            ttk.Separator(buttons_frame).grid(row=button_row, column=0, sticky="ew", pady=15)
            button_row += 1
            
            ttk.Button(
                buttons_frame, 
                text=f"Pending Requests ({len(pending_for_me)})", 
                bootstyle="danger", 
                command=self.show_pending_requests_page, 
                padding=12
            ).grid(row=button_row, column=0, pady=10, sticky="ew")

            
        # Bottom Frame (Logout and AI Assistant)
        bottom_frame = ttk.Frame(frame)
        bottom_frame.grid(row=3, column=0, columnspan=2, pady=(40, 0), sticky="s", padx=250)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(bottom_frame, text="Arna AI", bootstyle="info", command=self.open_ai_assistant, padding=12).grid(
            row=0, column=0, padx=10, sticky="ew"
        )
        
        ttk.Button(bottom_frame, text="Logout", bootstyle="danger", command=self.show_login, padding=12).grid(
            row=0, column=1, padx=10, sticky="ew"
        )


    # Transaction History / Statements
    def show_statements_page(self):
        frame = self.setup_frame("Transaction History", back_command=self.show_dashboard)
        
        all_logs = load_data(TRANSACTION_LOG_FILE)
        if not isinstance(all_logs, list):
            all_logs = []
            
        user_logs = [log for log in all_logs if log.get('account_no') == self.current_acc_no]
        
        if not user_logs:
            ttk.Label(frame, text="No transactions recorded yet.", font=("Arial", 14)).grid(
                row=2, column=0, columnspan=2, pady=50, sticky="n"
            )
            return

        table_frame = ttk.Frame(frame)
        table_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        
        frame.grid_rowconfigure(2, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("#1", "#2", "#3", "#4", "#5")
        self.tree = Treeview(
            table_frame, columns=columns, show="headings", height=20, bootstyle="table" 
        )

        self.tree.heading("#1", text="Date/Time", anchor=tk.W)
        self.tree.heading("#2", text="Type", anchor=tk.W)
        self.tree.heading("#3", text="Amount", anchor=tk.E)
        self.tree.heading("#4", text="Target/Source Acc", anchor=tk.CENTER)
        self.tree.heading("#5", text="Status", anchor=tk.CENTER)

        self.tree.column("#1", width=150, anchor=tk.W)
        self.tree.column("#2", width=120, anchor=tk.W)
        self.tree.column("#3", width=120, anchor=tk.E)
        self.tree.column("#4", width=150, anchor=tk.CENTER)
        self.tree.column("#5", width=80, anchor=tk.CENTER)

        for log in reversed(user_logs):
            amount = log.get('amount', 0)
            amount_display = self._format_currency(abs(amount))
            log_type = log.get('type')
            
            tag = 'danger' if amount < 0 or log_type in ["Withdrawal", "Send", "Send (Request)"] else 'success'
            
            self.tree.insert(
                "", 
                tk.END, 
                values=(
                    log.get('timestamp', 'N/A'), 
                    log_type, 
                    amount_display, 
                    log.get('target_acc_no', 'N/A'),
                    log.get('status', 'N/A')
                ), 
                tags=(tag,)
            )

        self.tree.tag_configure('danger', foreground='red', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('success', foreground='green', font=('Arial', 10, 'bold'))

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
    # AI Assistant Methods (Live Ollama Integration)
    def open_ai_assistant(self):
        """Opens a new window for the AI Assistant chat."""
        self.ai_window = ttk.Toplevel(self.root) 
        self.ai_window.title("AI Assistant Arna")
        self.ai_window.geometry("500x600")
        self.ai_window.grab_set() 

        ttk.Label(self.ai_window, text="Arna chatbot!", font=("Arial", 16, "bold")).pack(pady=20)
        
        self.chat_display = scrolledtext.ScrolledText(self.ai_window, wrap=tk.WORD, state='disabled', height=25)
        self.chat_display.pack(padx=10, pady=10, fill="x")

        input_frame = ttk.Frame(self.ai_window)
        input_frame.pack(padx=10, pady=10, fill="x")
        
        self.chat_input = ttk.Entry(input_frame, width=50)
        self.chat_input.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind("<Return>", lambda event: self._ai_placeholder_response())
        
        ttk.Button(input_frame, text="Send", command=self._ai_placeholder_response, bootstyle="info").pack(side=tk.RIGHT)
        
        self._append_message(f"Arna: Hello Myself Arna! I am your banking AI Assistant . Try asking me for your 'balance', your 'last transactions', or a general question like 'What is compound interest?'", "white")

    def _append_message(self, message, color):
        self.chat_display.config(state='normal')
        tag_name = f"tag_{color}"
        try:
            self.chat_display.tag_config(tag_name, foreground=color)
        except:
             pass

        self.chat_display.insert(tk.END, message + "\n", tag_name)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def _ai_placeholder_response(self):
        user_message = self.chat_input.get()
        if not user_message.strip():
            return
        
        self.chat_input.delete(0, tk.END)
        self._append_message(f"You: {user_message}", "yellow")
        self.root.after(100, lambda: self._generate_ai_response(user_message))

    def _get_user_logs(self):
        all_logs = load_data(TRANSACTION_LOG_FILE)
        if not isinstance(all_logs, list): all_logs = []
        user_logs = [log for log in all_logs if log.get('account_no') == self.current_acc_no]
        return list(reversed(user_logs))

    def _generate_ai_response(self, user_message):
        message = user_message.lower()
        response = ""
        
        # 1. Internal Banking Queries
        if "balance" in message or "money" in message and not any(word in message for word in ["send", "deposit", "withdraw"]):
            balance = self._format_currency(self.data[self.current_user].get('balance', 0))
            response = f"Arna: Your current balance is {balance}. For security, I cannot execute transfers."
            self._append_message(response, "white")
            return

        elif "history" in message or "transactions" in message or "statement" in message or "past activity" in message:
            recent_logs = self._get_user_logs()
            
            if not recent_logs:
                response = "Arna: I checked the logs, and there is no transaction history recorded for this account yet."
            else:
                count = min(len(recent_logs), 3)
                logs_to_show = recent_logs[:count]
                response = f"Arna: Here are your **last {len(logs_to_show)} transactions**:\n"
                
                for log in logs_to_show:
                    amount = self._format_currency(abs(log.get('amount', 0)))
                    action = "sent/withdrawn" if log.get('amount', 0) < 0 or log.get('type') in ["Withdrawal", "Send", "Send (Request)"] else "received/deposited"
                    response += f"  - {log.get('timestamp', 'N/A').split(' ')[0]}: {amount} {action} ({log.get('type', 'N/A')})\n"
            self._append_message(response, "white")
            return
            
        elif any(verb in message for verb in ["send", "deposit", "withdraw", "transfer", "request", "move money"]):
             response = "AI: For strict security policies, I cannot directly initiate or complete transactions. Please use the dedicated buttons on the dashboard."
             self._append_message(response, "red")
             return

        # 2. General Finance Questions (Ollama API Call)
        try:
            prompt = f"You are a helpful banking assistant. Answer the user's question concisely. Question: {user_message}"
            payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            api_response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
            api_response.raise_for_status() 
            response_data = api_response.json()
            response = f"Arna: {response_data.get('response', 'Sorry, I received an empty response.')}"
        except requests.exceptions.ConnectionError:
            response = f"Arna: **Connection Error.** Please ensure **Ollama is running**."
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                 response = f"Arna: **Model Error (404).** The model **{OLLAMA_MODEL}** may not be installed."
            else:
                response = f"Arna: An HTTP error occurred: {e}"
        except Exception as e:
            response = f"Arna: An unexpected error occurred: {e}"

        self._append_message(response, "white")
        
    # Helper Methods for Transactions

    def _update_balance_display(self):
        try:
            balance = self.data[self.current_user]["balance"]
            self.balance_label.config(text=self._format_currency(balance))
        except (tk.TclError, AttributeError, KeyError):
            pass 

    def _format_currency(self, amount):
        return f"{CURRENCY} {amount:,.2f}" 

    def _get_wealth_message(self, balance):
        for threshold, message in WEALTH_TIERS:
            if balance >= threshold:
                return message
        return ""

    def _verify_pin(self, prompt, correct_pin):
        for i in range(3, 0, -1):
            entered_pin = simpledialog.askstring("PIN Verification", f"{prompt} (Attempts left: {i})", show="*")
            if entered_pin is None: return False
            if entered_pin == correct_pin: return True
        messagebox.showerror("Failed", "Transaction failed! Incorrect PIN.")
        return False
        
    def _handle_transaction_result(self, title, base_message):
        final_balance = self.data[self.current_user]["balance"]
        wealth_message = self._get_wealth_message(final_balance)
        full_message = f"{base_message}\n\n{wealth_message}" if wealth_message else base_message
        messagebox.showinfo(title, full_message)
        self._update_balance_display()

    def _create_transaction_page(self, title, entry_labels, callback, button_style="primary"):
        frame = self.setup_frame(title, back_command=self.show_dashboard)
        
        center_frame = ttk.Frame(frame, padding=30)
        center_frame.grid(row=2, column=0, columnspan=2, sticky="n")
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)
        
        entries = {}
        for i, label in enumerate(entry_labels):
            entries[label] = self._add_input(center_frame, label, i)
            
        ttk.Button(center_frame, text=f"Confirm {title.split(' ')[0]}", bootstyle=button_style, command=lambda: callback(entries), padding=12).grid(
            row=len(entry_labels), column=0, columnspan=2, pady=30, sticky="ew"
        )
        
    # Transaction logic

    def show_deposit_page(self):
        self._create_transaction_page("Deposit Funds", ["Amount to Deposit:"], self.deposit, "success")

    def deposit(self, entries):
        try: amount = int(entries["Amount to Deposit:"].get())
        except ValueError: messagebox.showerror("Error", "Enter a valid integer amount."); return
        if amount <= 0: messagebox.showerror("Error", "Deposit must be greater than zero"); return
        if not self._verify_pin("Enter PIN for Deposit", self.data[self.current_user].get("pin")): return
            
        self.data[self.current_user]["balance"] += amount
        save_data(self.data, DATA_FILE)
        log_transaction(self.current_acc_no, "Deposit", amount, "Success")
        base_message = f"Deposit Successful! Amount: {self._format_currency(amount)}"
        self._handle_transaction_result("Success", base_message)
        self.show_dashboard()

    def show_withdraw_page(self):
        self._create_transaction_page("Withdraw Funds", ["Amount to Withdraw:"], self.withdraw, "primary")

    def withdraw(self, entries):
        try: amount = int(entries["Amount to Withdraw:"].get())
        except ValueError: messagebox.showerror("Error", "Enter a valid integer amount."); return
        user_data = self.data[self.current_user]
        current_balance = user_data.get("balance", 0)
        
        if amount <= 0: messagebox.showerror("Failed", "Withdrawal must be positive."); return
        if not self._verify_pin("Enter PIN for Withdrawal", user_data.get("pin")): return
        if amount > current_balance: messagebox.showerror("Failed", "Amount exceeds balance."); return
        if current_balance - amount < MINIMUM_BALANCE: 
            messagebox.showerror("Failed", f"Minimum balance {self._format_currency(MINIMUM_BALANCE)} required."); return

        user_data["balance"] -= amount
        save_data(self.data, DATA_FILE)
        log_transaction(self.current_acc_no, "Withdrawal", amount * -1, "Success")
        base_message = f"Withdrawal Successful! Amount: {self._format_currency(amount)}"
        self._handle_transaction_result("Success", base_message)
        self.show_dashboard()
        
    def show_send_money_page(self):
        self._create_transaction_page(
            "Send Funds (Push)", 
            ["Recipient Account No:", "Amount to Send:"], 
            self.send_money, 
            "info"
        )

    def send_money(self, entries):
        target_acc_no = entries["Recipient Account No:"].get()
        try: amount = int(entries["Amount to Send:"].get())
        except ValueError: messagebox.showerror("Error", "Enter a valid integer amount."); return

        target_user = next((u for u, d in self.data.items() if d.get("account_no") == target_acc_no), None)
        user_data = self.data[self.current_user]
        current_balance = user_data.get("balance", 0)

        if amount <= 0: messagebox.showerror("Error", "Amount must be positive."); return
        if not target_user: messagebox.showerror("Error", "Recipient Account not found."); return
        if target_user == self.current_user: messagebox.showerror("Error", "Cannot send to self."); return
        if not self._verify_pin("Enter PIN to Authorize Send", user_data.get("pin")): return
        if amount > current_balance: messagebox.showerror("Failed", "Amount exceeds your balance."); return
        if current_balance - amount < MINIMUM_BALANCE: 
            messagebox.showerror("Failed", f"Maintain minimum balance of {self._format_currency(MINIMUM_BALANCE)}."); return

        self.data[target_user]["balance"] += amount
        user_data["balance"] -= amount
        save_data(self.data, DATA_FILE)
        
        log_transaction(self.current_acc_no, "Send", amount * -1, "Success", target_acc_no)
        log_transaction(target_acc_no, "Receive (Send)", amount, "Success", self.current_acc_no)
        
        base_message = f"Sent {self._format_currency(amount)} to {target_user} (Acc No: {target_acc_no})."
        self._handle_transaction_result("Success", base_message)
        self.show_dashboard()

    
    
    def show_request_money_page(self):
        """Shows the page for *creating* a money request."""
        self._create_transaction_page(
            "Request Funds (Pull)", 
            ["Source Account No:", "Amount to Request:"], 
            self.create_money_request, 
            "warning"
        )

    def create_money_request(self, entries):
        """Creates a pending request. Does NOT transfer money or ask for PIN."""
        source_acc_no = entries["Source Account No:"].get()
        try: amount = int(entries["Amount to Request:"].get())
        except ValueError: messagebox.showerror("Error", "Enter a valid integer amount."); return

        source_user_item = next(((u, d) for u, d in self.data.items() if d.get("account_no") == source_acc_no), None)

        if not source_user_item:
            messagebox.showerror("Error", "Source Account not found."); return
            
        source_user, source_data = source_user_item

        if amount <= 0: messagebox.showerror("Error", "Amount must be positive."); return
        if source_user == self.current_user: messagebox.showerror("Error", "Cannot request from self."); return

        all_requests = load_data(REQUESTS_FILE)
        if not isinstance(all_requests, dict):
            all_requests = {}
        
        new_req_id = generate_request_id(all_requests)
        
        new_request = {
            "request_id": new_req_id,
            "requester_acc_no": self.current_acc_no,
            "requester_username": self.current_user,
            "source_acc_no": source_acc_no,
            "source_username": source_user,
            "amount": amount,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending" 
        }
        
        all_requests[new_req_id] = new_request
        save_data(all_requests, REQUESTS_FILE)
        
        messagebox.showinfo("Request Sent", f"Your request for {self._format_currency(amount)} has been sent to {source_user}. They will be notified when they log in.")
        self.show_dashboard()
        

    # Page and Functions for  Approving Requests

    def show_pending_requests_page(self):
        """Displays all pending requests for the current user."""
        frame = self.setup_frame("Pending Money Requests", back_command=self.show_dashboard)
        
        self.all_requests = load_data(REQUESTS_FILE)
        if not isinstance(self.all_requests, dict): self.all_requests = {}
        
        self.pending_list = [
            req for req in self.all_requests.values() 
            if req.get('source_acc_no') == self.current_acc_no and req.get('status') == 'pending'
        ]
        
        if not self.pending_list:
            ttk.Label(frame, text="You have no pending requests.", font=("Arial", 14)).grid(
                row=2, column=0, columnspan=2, pady=50, sticky="n"
            )
            return

        table_frame = ttk.Frame(frame)
        table_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("#1", "#2", "#3")
        self.requests_tree = Treeview(
            table_frame, columns=columns, show="headings", height=15, bootstyle="table" 
        )

        self.requests_tree.heading("#1", text="Date", anchor=tk.W)
        self.requests_tree.heading("#2", text="From", anchor=tk.W)
        self.requests_tree.heading("#3", text="Amount", anchor=tk.E)
        self.requests_tree.column("#1", width=150, anchor=tk.W)
        self.requests_tree.column("#2", width=150, anchor=tk.W)
        self.requests_tree.column("#3", width=120, anchor=tk.E)

        for req in self.pending_list:
            self.requests_tree.insert(
                "", tk.END, iid=req.get('request_id', 'N/A'),
                values=(
                    req.get('timestamp', 'N/A').split(' ')[0], 
                    req.get('requester_username', 'N/A'), 
                    self._format_currency(req.get('amount', 0))
                )
            )

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.requests_tree.yview)
        self.requests_tree.configure(yscrollcommand=vsb.set)
        self.requests_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Approve Selected", bootstyle="success", command=self.approve_request).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="Deny Selected", bootstyle="danger", command=self.deny_request).pack(side=tk.LEFT, padx=20)

    def approve_request(self):
        """Handles the logic for approving a selected money request."""
        try:
            selected_id = self.requests_tree.selection()[0]
        except IndexError:
            messagebox.showerror("Error", "Please select a request to approve.")
            return

        request = self.all_requests.get(selected_id)
        if not request:
            messagebox.showerror("Error", "Could not find the selected request. It may be outdated."); return
            
        amount = request.get('amount', 0)
        
        user_data = self.data[self.current_user]
        current_balance = user_data.get("balance", 0)
        
        if amount > current_balance:
            messagebox.showerror("Failed", "You do not have sufficient funds to approve this request."); return
        if current_balance - amount < MINIMUM_BALANCE: 
            messagebox.showerror("Failed", f"This transaction would bring you below the minimum balance of {self._format_currency(MINIMUM_BALANCE)}."); return
        
        # Verify the CURRENT user's PIN
        if not self._verify_pin(f"Enter YOUR PIN to send {self._format_currency(amount)}", user_data.get("pin")):
            return

        requester_user = next((u for u, d in self.data.items() if d.get('account_no') == request.get('requester_acc_no')), None)
        
        if not requester_user:
            messagebox.showerror("Error", "Could not find the requester's account. Cancelling transaction."); return
            
        # All checks passed, process the transaction
        self.data[self.current_user]["balance"] -= amount
        self.data[requester_user]["balance"] += amount
        save_data(self.data, DATA_FILE)
        
        request['status'] = 'approved'
        save_data(self.all_requests, REQUESTS_FILE)
        
        log_transaction(self.current_acc_no, "Send (Request)", amount * -1, "Success", request.get('requester_acc_no'))
        log_transaction(request.get('requester_acc_no'), "Receive (Request)", amount, "Success", self.current_acc_no)
        
        messagebox.showinfo("Success", "Request approved and money sent!")
        self.show_pending_requests_page() 

    def deny_request(self):
        """Handles the logic for denying a selected money request."""
        try:
            selected_id = self.requests_tree.selection()[0]
        except IndexError:
            messagebox.showerror("Error", "Please select a request to deny.")
            return
            
        request = self.all_requests.get(selected_id)
        if not request:
            messagebox.showerror("Error", "Could not find the selected request."); return
            
        request['status'] = 'denied'
        save_data(self.all_requests, REQUESTS_FILE)
        
        messagebox.showinfo("Request Denied", "The money request has been successfully denied.")
        self.show_pending_requests_page() 


if __name__ == "__main__":
    root = ttk.Window(themename="darkly") 
    app = BankApp(root)
    root.mainloop()
