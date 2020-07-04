from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime
import os

# load in the variables in the .env file into our operating system environment
load_dotenv()

app = Flask(__name__)

# connect to mongo
MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)

# define my db_name
DB_NAME = "expenseTracker"

# read in the SESSION_KEY variable from the operating system environment
SESSION_KEY = os.environ.get('SESSION_KEY')

# set the session key
app.secret_key = SESSION_KEY

# START WRITING YOUR CODE


@app.route('/')
def home():
    expenses = client[DB_NAME].expense.find()
    return render_template('home.template.html', expenses=expenses)


@app.route('/expense/create')
def show_create_form():
    return render_template('create_expense.template.html')


@app.route('/expense/create', methods=["POST"])
def process_create_expense():
    expense_name = request.form.get('expense-name')
    expense_date = request.form.get('expense-date')
    expense_type = request.form.get('expense-type')

    client[DB_NAME].expense.insert_one({
        'expense_name': expense_name,
        'expense_date': datetime.strptime(expense_date, '%Y-%m-%d'),
        'expense_type': expense_type,
        'reconciled': False

    })

    flash(f"New expense '{expense_name}' create successfully ")
    return redirect(url_for('home'))


@app.route('/expenses/check', methods=['PATCH'])
def check_expense():
    expense_id = request.json.get('expense_id')
    print(expense_id)
    expense = client[DB_NAME].expense.find_one({
        "_id": ObjectId(expense_id)
    })
    print(expense)

    client[DB_NAME].expense.update_one({
        "_id": ObjectId(expense_id)
    }, {
        '$set': {
            'reconciled': not expense['reconciled']
        }
    })

    return {
        "Status": "OK"
    }


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
