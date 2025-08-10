import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# Load Gemini API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# UTILITY: Extract Only Clean Response -
def extract_main_response(gemini_output: str) -> str:
    for line in gemini_output.splitlines():
        if line.strip().startswith(">"):
            return line.strip("> ").strip()
    return gemini_output.strip()


#  TOOL FUNCTIONS 
def check_balance(account_number: str) -> str:
    if not account_number.isdigit() or len(account_number) != 10:
        return "❌ Invalid account number. Please enter a 10-digit number."
    return f"✅ The balance for account {account_number} is PKR 25,000."

def transfer_funds(from_account: str, to_account: str, amount: float) -> str:
    if not (from_account.isdigit() and len(from_account) == 10):
        return "❌ Invalid sender account number."
    if not (to_account.isdigit() and len(to_account) == 10):
        return "❌ Invalid receiver account number."
    if amount <= 0:
        return "❌ Amount must be greater than 0."
    return f"✅ PKR {amount} transferred from {from_account} to {to_account}."

#  HANDOFF AGENTS
class BalanceAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def handle(self, account_number: str) -> str:
        response = check_balance(account_number)
        prompt = f"You are a helpful banking assistant.\nUser requested balance check.\nResponse: {response}"
        reply = self.model.generate_content(prompt)
        return extract_main_response(reply.text)

class TransferAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def handle(self, from_acc: str, to_acc: str, amount: float) -> str:
        response = transfer_funds(from_acc, to_acc, amount)
        prompt = f"You are a helpful banking assistant.\nUser requested fund transfer.\nResponse: {response}"
        reply = self.model.generate_content(prompt)
        return extract_main_response(reply.text)

#- MAIN BANK AGENT 

class BankAgent:
    def __init__(self):
        self.balance_agent = BalanceAgent()
        self.transfer_agent = TransferAgent()

    async def run(self):
        print("🏦 Welcome to Bank Assistant")
        print("What would you like to do?")
        print("1. Check Balance")
        print("2. Transfer Funds")
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            acc = input("Enter your 10-digit account number: ").strip()
            response = self.balance_agent.handle(acc)
        elif choice == "2":
            from_acc = input("Sender's 10-digit account number: ").strip()
            to_acc = input("Receiver's 10-digit account number: ").strip()
            try:
                amount = float(input("Amount to transfer (PKR): ").strip())
            except ValueError:
                print("❌ Invalid amount entered. please enter a correct amount.")
                return
            response = self.transfer_agent.handle(from_acc, to_acc, amount)
        else:
            print("❌ Invalid choice. please enter1 or 2 to proceed.")
            return

        print("\n🤖Agent Response:\n", response)

#  RUNNER

if __name__ == "__main__":
    agent = BankAgent()
    asyncio.run(agent.run())
