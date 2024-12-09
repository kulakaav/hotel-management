from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)  # New field for customer name
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    advance_payment = db.Column(db.Float, nullable=False)
    total_payment = db.Column(db.Float, nullable=False)
    full_day = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Event {self.name} for {self.customer_name} on {self.date}>'

# Routes for Todo
@app.route('/')
def landing_page():
    return render_template("mainpage.html")

@app.route('/assignment/about/')
def about():
    return render_template("/assignment/about.html")


@app.route('/assignment/homepage/')
def Home_page():
      # Fetch event data from the database


    events = Event.query.all()

    # Prepare the events for the calendar (format: YYYY-MM-DD)
    booked_dates = [
        {'title': event.customer_name, 'start': event.date.strftime('%Y-%m-%d')}
        for event in events
    ]

    return render_template('assignment/homepage.html', booked_dates=booked_dates)


@app.route('/assignment/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))  # Use url_for here
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('assignment/index.html', tasks=tasks)

@app.route('/assignment/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('index'))  # Use url_for here
    except:
        return 'There was a problem deleting that task'

@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect(url_for('index'))  # Use url_for here
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('assignment/update.html', task=task)

@app.route('/assignment/events', methods=['GET', 'POST'])
def manage_events():
    if request.method == 'POST':
        # Handling new event creation logic
        event_name = request.form['event_name']
        customer_name = request.form['customer_name']
        event_date = request.form['event_date']
        advance_payment = float(request.form['advance_payment'])
        total_payment = float(request.form['total_payment'])
        full_day = 'full_day' in request.form

        new_event = Event(
            name=event_name,
            customer_name=customer_name,
            date=datetime.strptime(event_date, '%Y-%m-%d').date(),
            advance_payment=advance_payment,
            total_payment=total_payment,
            full_day=full_day
        )

        try:
            db.session.add(new_event)
            db.session.commit()
            return redirect(url_for('manage_events'))
        except Exception as e:
            print(f"Error adding event: {e}")
            return f"Error adding event: {e}"

    else:
        # Get filter and sort parameters from the request
        filter_full_day = request.args.get('filter_full_day', type=str)
        sort_date = request.args.get('sort_date', type=str)

        events_query = Event.query

        # Apply full day filter if specified
        if filter_full_day is not None:
            if filter_full_day.lower() == 'true':
                events_query = events_query.filter_by(full_day=True)
            elif filter_full_day.lower() == 'false':
                events_query = events_query.filter_by(full_day=False)

        # Apply sorting by date if specified
        if sort_date == 'asc':
            events_query = events_query.order_by(Event.date.asc())
        elif sort_date == 'desc':
            events_query = events_query.order_by(Event.date.desc())

        events = events_query.all()
        return render_template('assignment/events.html', events=events)
@app.route('/assignment/events/update/<int:id>', methods=['GET', 'POST'])
def update_event(id):
    event = Event.query.get_or_404(id)
    
    if request.method == 'POST':
        event.name = request.form['event_name']
        event.customer_name = request.form['customer_name']
        event.date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        event.advance_payment = float(request.form['advance_payment'])
        event.total_payment = float(request.form['total_payment'])
        event.full_day = 'full_day' in request.form

        try:
            db.session.commit()
            return redirect(url_for('manage_events'))
        except Exception as e:
            print(f"Error updating event: {e}")
            return f"Error updating event: {e}"

    return render_template('assignment/update_event.html', event=event)



# Delete event route
@app.route('/assignment/delete_event/<int:id>', methods=['GET', 'POST'])
def delete_event(id):
    # Find the event by ID
    event = Event.query.get(id)
    if event:
        # If the event exists, delete it
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('manage_events'))  # Redirect back to the event management page
if __name__ == "__main__":
    app.run(debug=True)
