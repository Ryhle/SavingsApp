import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# Load initial data
data = pd.read_excel('data.xlsx')
data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')

def save_data(data):
    data.to_excel('data.xlsx', index=False)

def show_monthly_budget(date):
    filtered = data.loc[data['Date'] == date]
    return filtered.to_dict(orient='records')

def record_expenses(date, amount, details):
    global data  # Declare data as a global variable
    amount = int(amount)  # Convert amount to integer
    new_expense = pd.DataFrame({'Date': [date], 'Amount': [-amount], 'Details': [details], 'Type': ['expense']})
    data = pd.concat([data, new_expense], axis=0, ignore_index=True)
    save_data(data)
    return {"message": "Expense recorded successfully."}


def filter_monthly_records(month):
    # Extract month from Date column
    data['Month'] = pd.to_datetime(data['Date']).dt.to_period('M')
    # Filter data by month
    monthly_data = data[(data['Month'] == month) & (data['Type'] == 'expense')]
    # Drop the Month column to avoid confusion
    monthly_data = monthly_data.drop(columns=['Month'])
    return monthly_data

def record_allowance(date, amount):
    global data  # Ensure data is accessed from the global scope
    amount = int(amount)
    new_record = pd.DataFrame({'Date': [date], 'Amount': [amount], 'Type': ['allowance']})
    data = pd.concat([data, new_record], axis=0, ignore_index=True)
    save_data(data)  # Save the updated DataFrame to data.xlsx
    print('Allowance Recorded Successfully')
    return {"message": "Allowance recorded successfully."}

def calculate_monthly_savings(month):
    global data
    print("Selected Month:", month)  # Print selected month for debugging
    # Filter expense data for the selected month
    expense_data = data[(data['Type'] == 'expense') & (data['Date'].dt.to_period('M') == month)]
    print("Expense Data:", expense_data)  # Print filtered expense data for debugging
    total_expense = expense_data['Amount'].sum()
    print("Total Expense:", total_expense)  # Print total expense for debugging

    # Filter allowance data for the selected month
    allowance_data = data[(data['Type'] == 'allowance') & (data['Date'].dt.to_period('M') == month)]
    print("Allowance Data:", allowance_data)  # Print filtered allowance data for debugging
    total_allowance = allowance_data['Amount'].sum()
    print("Total Allowance:", total_allowance)  # Print total allowance for debugging

    # Calculate savings
    savings = total_allowance + total_expense
    print("Savings:", savings)  # Print savings for debugging
    return int(savings)



###LOGIN
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'user' and password == 'password':
        return redirect(url_for('navigation'))  # Redirect to main.py route
    else:
        return render_template('login.html', message='Invalid username or password')
###
@app.route('/success')
def success():
    return redirect(url_for('main_page'))  # Redirect to main.py route
###
@app.route('/main')
def main_page():
    return render_template('index.html')

@app.route('/allowances_page')
def allowances_page():
    return render_template('allowances.html')

@app.route('/navigation')
def navigation():
    return render_template('navigation.html')

@app.route('/record_expense', methods=['POST'])
def record_expense():
    date = pd.to_datetime(request.json['date'])
    amount = request.json['amount']
    details = request.json['details']
    record_expenses(date, amount, details)
    return jsonify({"message": "Expense recorded successfully."})

@app.route('/show_monthly_records', methods=['GET', 'POST'])
def show_monthly_records():
    selected_month = None
    monthly_savings = None
    if request.method == 'POST':
        selected_month = pd.Period(request.form['selected_month'])
        # Filter data by selected month
        expenses = filter_monthly_records(selected_month)
        # Calculate monthly savings
        monthly_savings = calculate_monthly_savings(selected_month)
        return render_template('expenses.html', expenses=expenses, selected_month=selected_month, monthly_savings=monthly_savings)
    return render_template('expenses.html', expenses=None, selected_month=selected_month, monthly_savings=monthly_savings)

@app.route('/calculate_savings', methods=['POST'])
def calculate_savings():
    selected_month_str = request.json['selected_month']  # Get selected_month as string
    try:
        selected_month = pd.Period(selected_month_str)  # Convert selected_month to Period object
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    print("Received Selected Month:", selected_month)  # Print received selected month for debugging
    savings = calculate_monthly_savings(selected_month)
    return jsonify({"savings": savings})



@app.route('/record_allowance', methods=['POST'])
def record_allowance_route():
    date = pd.to_datetime(request.json['date'])
    amount = int(request.json['amount'])  # Convert to integer
    record_allowance(date, amount)
    return jsonify({"message": "Allowance recorded successfully."})

if __name__ == '__main__':
    app.run(debug=True)