# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import requests
from datetime import datetime, date


app = Flask(__name__)
app.secret_key = 'secret123'  # for flash messages

# --- Telegram Bot Config ---
BOT_TOKEN = '7383707456:AAFtBX7-tzUxWUhGmVik1CPAOsHAHQuU1IM'
CHAT_ID = '7370529147'  # Telegram user or group ID

# --- Database Init ---
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    car TEXT,
                    pickup_date TEXT,
                    drop_date TEXT
                )''')
    conn.commit()
    conn.close()

# --- Routes ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cars')
def cars():
    return render_template('cars.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# @app.route('/book')
# def book():
#     car = request.args.get('car')
#     return render_template('book.html', car=car)

@app.route('/book')
def book():
    car = request.args.get('car')
    min_date = date.today().isoformat()
    return render_template('book.html', car=car, min_date=min_date)


@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    name = request.form['name']
    phone = request.form['phone']
    car = request.form['car']
    pickup_date = request.form['pickup_date']
    drop_date = request.form['drop_date']
    # price = car_prices.get(car, "Price not available") 
    
    from datetime import datetime, date  # already added above

    pickup_obj = datetime.strptime(pickup_date, "%Y-%m-%d").date()
    drop_obj = datetime.strptime(drop_date, "%Y-%m-%d").date()
    today = date.today()

    if pickup_obj < today or drop_obj < today:
        flash("Pickup and drop dates cannot be in the past.")
        return redirect(url_for('book'))

    if drop_obj < pickup_obj:
        flash("Drop date cannot be before pickup date.")
        return redirect(url_for('book'))


  
    # Save to database
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("INSERT INTO bookings (name, phone, car, pickup_date, drop_date) VALUES (?, ?, ?, ?, ?)",
              (name, phone, car, pickup_date, drop_date))
    conn.commit()
    conn.close()
    
    car_prices = {
        "Swift": "₹1100/day",
        "Swift Dzire": "₹1700/day",
        "Old Ertiga": "₹2000/day"
    }
    price = car_prices.get(car, "Price not available")

    # Send to Telegram
    message = f"🚗 New Booking:\n\nName: {name}\nPhone: {phone}\nCar: {car}\nPickup: {pickup_date}\nDrop: {drop_date}\nPrice: {price}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)

    # Debug output
    print("Telegram Response:", response.status_code)
    print("Telegram Response Text:", response.text)

    flash("Booking submitted successfully!")
    return redirect(url_for('cars', car=car, booked='true'))

    # return redirect(url_for('cars', car=car))


# --- Run ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
