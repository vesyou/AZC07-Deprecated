import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Obtain user_id of current session, select all from portfolio for current user
    user = session["user_id"]
    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", user)
    cursor = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    money = cursor[0]['cash']

    # Loop through portfolio and add new fields for name, current price and total using the lookup function
    total_value = 0
    for row in portfolio:
        row['name'] = lookup(row['symbol'])['name']
        row['price'] = lookup(row['symbol'])['price']
        row['total'] = row['price'] * row['shares']
        total_value = total_value + row['total']

    # Format to usd before passing to template
    total_value = usd(total_value + money)
    money = usd(money)
    return render_template("index.html", portfolio=portfolio, money=money, total_value=total_value)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Obtain user input
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Lookup symbol and return apology if symbol does not exist
        RESULT = lookup(request.form.get("symbol"))
        if not RESULT:
            return apology("lookup is unsuccessful, symbol may not exist", 403)

        # Return apology if shares input not a positive integer (https://note.nkmk.me/en/python-check-int-float/)
        if not shares.isnumeric() or int(shares) <= 0:
            return apology("number of shares must be a positive integer", 403)

        # Return apology if user does not have enough money, obtained user_id from session (Referenced provided code from CS50: session["user_id"] = rows[0]["id"])
        cursor = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        money = float(cursor[0]['cash'])

        total_cost = float(RESULT["price"] * int(shares))
        if money < total_cost:
            return apology("not enough money to purchase", 403)

        # CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER, symbol TEXT NOT NULL, shares INTEGER, price NUMERIC(14,2), purchase_date DATETIME, FOREIGN KEY (user_id) REFERENCES users(id));
        # Record the number of shares bought, at what price, when, and the unique ID of the user in 'users' table. Each transaction also has its own unique ID.
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, purchase_date) VALUES (?, ?, ?, ?, ?)", session["user_id"], RESULT["symbol"], shares, RESULT["price"], datetime.now() )

        # CREATE TABLE portfolio (user_id INTEGER NOT NULL, symbol TEXT NOT NULL, shares INTEGER, FOREIGN KEY (user_id) REFERENCES users(id));
        # Check if there is already a entry for this user, and for this symbol
        existing = db.execute("SELECT shares FROM portfolio WHERE user_id = ? AND symbol = ?", session["user_id"], RESULT["symbol"])
        # if user already owns shares with the same symbol, add amount of shares. Else add new entry.
        if existing:
            db.execute("UPDATE portfolio SET shares = shares + ? WHERE user_id = ? AND symbol = ?", shares, session["user_id"], RESULT["symbol"])
        else:
            db.execute("INSERT INTO portfolio (user_id, symbol, shares) VALUES (?, ?, ?)", session["user_id"], RESULT["symbol"], shares)

        # Deduct amount from users table
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, session["user_id"])

        # Obtain price and format in USD for flash message
        total_cost = usd(total_cost)
        price = usd(RESULT["price"])

        # Flash message confirming purchase (https://stackoverflow.com/questions/71153840/how-to-flash-message-with-variables-in-flask)
        flash("Successfully purchased {} shares of {} at {} per share for a total of {}.".format(shares, symbol, price, total_cost), "success")

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

        # Obtain user_id of current session, select all from portfolio for current user
    user = session["user_id"]
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", user)

    # Loop through portfolio and add new fields for name, current price and total using the lookup function
    for row in transactions:
        if row['purchase_date']:
            row['buy_sell'] = "Purchase"
        else:
            row['buy_sell'] = "Sale"

    return render_template("history.html", transactions=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        RESULT = lookup(request.form.get("symbol"))

        # Check if lookup is successful
        if not RESULT:
            return apology("lookup is unsuccessful, symbol may not exist", 403)

        return render_template("quoted.html", result=RESULT)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Check if user submitted form via POST
    if request.method == "POST":

        # Check if username present
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            return apology("username already exists", 403)

        # Check if password present
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Check if password confirmation present and same as password
        elif not request.form.get("confirmation") or (request.form.get("confirmation") != request.form.get("password")):
            return apology("confirmation must be same as password", 403)

        # Hash the password and define username
        password = request.form.get("confirmation")
        hash = generate_password_hash(password)
        username = request.form.get("username")

        # Insert new user, with username and hashed password
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        # Flask success message and return to login page
        flash("Successful registration! Login below")
        return render_template("login.html")

    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        # Obtain user input
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Lookup symbol and return apology if symbol does not exist
        RESULT = lookup(request.form.get("symbol"))
        if not RESULT:
            return apology("lookup is unsuccessful, symbol may not exist", 403)

        # Return apology if shares input not a positive integer (https://note.nkmk.me/en/python-check-int-float/)
        if not shares.isnumeric() or int(shares) <= 0:
            return apology("number of shares must be a positive integer", 403)

        # Iterate over each row in the owned_shares dictionary to check if symbol matches, if so, also check if they own the number of shares they are intending to sell
        owned_shares = db.execute("SELECT symbol, shares FROM portfolio WHERE user_id = ?", session["user_id"])
        user_has_shares = False
        for share in owned_shares:
            if symbol == share['symbol']:
                user_has_shares = True
                if int(shares) > share['shares']:
                    return apology("user does not appear to have enough shares", 403)
                break

        if not user_has_shares:
            return apology("unable to find stock in user's portfolio", 403)

        # Record the symbol, number of shares sold, at what price, the user's ID, and date of sale
        # Had to add column 'sale_date': ALTER TABLE transactions ADD COLUMN sale_date DATETIME;
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, sale_date) VALUES (?, ?, ?, ?, ?)", session["user_id"], symbol, shares, RESULT["price"], datetime.now() )

        # Remove number of shares from portfolio
        db.execute("UPDATE portfolio SET shares = shares - ? WHERE user_id = ? AND symbol = ?", shares, session["user_id"], symbol)

        # If all shares have been sold, remove entry
        db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol = ? AND shares = 0", session["user_id"], symbol)

        # Calculate total price the shares sold for, and increase user's money accordingly
        total_price = float(RESULT["price"] * int(shares))
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_price, session["user_id"])

        # Obtain price and format in USD for flash message
        total_price = usd(total_price)
        price = usd(RESULT["price"])

        # Flask success message and return to login page (https://stackoverflow.com/questions/71153840/how-to-flash-message-with-variables-in-flask)
        flash("Successfully sold {} shares of {} at {} per share for a total of {}.".format(shares, symbol, price, total_price), "success")
        return redirect("/")
    else:
        user = session["user_id"]
        symbols = db.execute("SELECT symbol FROM portfolio WHERE user_id = ?", user)
        return render_template("sell.html", symbols=symbols)

@app.route("/settings")
def settings():
    """Extra personal touch settings"""


    return render_template("settings.html")