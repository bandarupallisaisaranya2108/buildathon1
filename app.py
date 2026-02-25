from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2108cherry@3652'
app.config['MYSQL_DB'] = 'event_management'

mysql = MySQL(app)

# Home Page - Event Listing
@app.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    return render_template('home.html', events=events)

# Event Detail Page
@app.route('/event/<int:event_id>')
def event_detail(event_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    return render_template('event_detail.html', event=event)

# Registration Page
@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        tickets = request.form['tickets']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO registrations (event_id, name, email, phone, tickets) VALUES (%s, %s, %s, %s, %s)",
                       (event_id, name, email, phone, tickets))
        mysql.connection.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    return render_template('register.html', event=event)

# Save Registered Events
@app.route('/save_event/<int:event_id>', methods=['POST'])
def save_event(event_id):
    user_id = 1  # Placeholder for user ID (replace with actual user authentication logic)
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT IGNORE INTO saved_events (user_id, event_id) VALUES (%s, %s)", (user_id, event_id))
    mysql.connection.commit()
    flash('Event saved successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/saved_events')
def saved_events():
    user_id = 1  # Placeholder for user ID (replace with actual user authentication logic)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT events.* FROM events INNER JOIN saved_events ON events.id = saved_events.event_id WHERE saved_events.user_id = %s", (user_id,))
    events = cursor.fetchall()
    return render_template('saved_events.html', events=events)

# Search and Filter Functionality
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    category = request.args.get('category', '')
    date = request.args.get('date', '')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql_query = "SELECT * FROM events WHERE 1=1"
    params = []

    if query:
        sql_query += " AND name LIKE %s"
        params.append(f"%{query}%")
    if location:
        sql_query += " AND location LIKE %s"
        params.append(f"%{location}%")
    if category:
        sql_query += " AND category = %s"
        params.append(category)
    if date:
        sql_query += " AND date = %s"
        params.append(date)

    cursor.execute(sql_query, params)
    events = cursor.fetchall()
    return render_template('search.html', events=events, query=query, location=location, category=category, date=date)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Admin Panel
@app.route('/admin')
def admin():
    if 'loggedin' in session and session['user_role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        return render_template('admin.html', events=events)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

# Event Capacity Management
@app.route('/admin/update_capacity/<int:event_id>', methods=['POST'])
def update_capacity(event_id):
    if 'loggedin' in session and session['user_role'] == 'admin':
        capacity = request.form['capacity']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE events SET capacity = %s WHERE id = %s", (capacity, event_id))
        mysql.connection.commit()
        flash('Event capacity updated successfully.', 'success')
        return redirect(url_for('admin'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

# Event Reminders
@app.route('/send_reminders')
def send_reminders():
    if 'loggedin' in session and session['user_role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT r.email, e.name, e.date, e.time FROM registrations r JOIN events e ON r.event_id = e.id WHERE e.date = CURDATE()")
        reminders = cursor.fetchall()
        for reminder in reminders:
            # Logic to send email reminders (placeholder)
            print(f"Sending reminder to {reminder['email']} for event {reminder['name']} on {reminder['date']} at {reminder['time']}")
        flash('Reminders sent successfully.', 'success')
        return redirect(url_for('admin'))
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)