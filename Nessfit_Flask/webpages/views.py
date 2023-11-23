from flask import Blueprint,render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Log, Exercise
from datetime import datetime
from sqlalchemy.exc import IntegrityError

views = Blueprint('views',__name__)

#FOR BMI 
def der_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 24.9:
        return 'Normal Weight'
    elif 24.9 <= bmi < 29.9:
        return 'Overweight'
    else:
        return 'Obese'
    
#START OF THE CODE
@views.route('/')
def home():
    return render_template('home.html',user=current_user)

#-----------BMI-------------------------------------------------------------------------------------------------    
@views.route('/bmi-calculator',methods=['POST','GET'])
def calculate():
    bmi =''
    category = ''
    a = ''
    g = ''
    if request.method == 'POST' and 'weight' in request.form and 'height' in request.form and 'age' in request.form and 'gender' in request.form:
        w = float(request.form.get('weight'))
        h = float(request.form.get('height'))
        a = int(request.form.get('age'))
        g = request.form.get('gender')
        bmi = round(w/((h/100)**2),2)
        category = der_category(bmi)
        #return redirect(url_for('views.index'))
    return render_template('bmi_calcu.html',bmi=bmi,category=category,a=a,g=g)

#-----------INDEX-------------------------------------------------------------------------------------------------   
@views.route('/index')
@login_required
def index():
    logs = Log.query.filter_by(user_id=current_user.id).order_by(Log.date.desc()).all() # gets the logs of the current logged-in user and the exercise data
    log_dates = [] # this dictionary will contain the exericse data and put below the following code ⤵️

    for log in logs:
        exercise_names = []
        for exercise in log.exercises:
            exercise_names.append({
                'name': exercise.name,
                'reps': exercise.reps,
                'sets': exercise.sets,
                'rest': exercise.rest
            })

        log_dates.append({
            'log_date': log,
            'exercises': exercise_names
        })

    return render_template("index.html", log_dates=log_dates) # This code retrieves the data in the database and presents it in the html file


#-----------CREATE LOGS-------------------------------------------------------------------------------------------------   
@views.route('/create_logs', methods=['POST']) # POST is a HTTP request method used to submit data to be processed
def logs():
    date = request.form.get('date') # retrieves the value of the date parameter from the POST request
    
    if not date:
        flash('Please enter a valid date.', category='error') # error handler / flash the message 
        return redirect(url_for('views.index'))

    try:
        log = Log(date=datetime.strptime(date, '%Y-%m-%d'), user_id=current_user.id) # try is same with if statement 
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('views.index'))  # Redirect to the index on success
    except ValueError:
        flash('Please enter a valid date in the format YYYY-MM-DD.', category='error')
        return redirect(url_for('views.index'))  # Redirect to the index on error
    except IntegrityError:
        db.session.rollback()
        flash('Log entry for this date already exists.', category='error')
        return redirect(url_for('views.index'))  # Redirect to the index on error

#-----------VIEW-------------------------------------------------------------------------------------------------   
@views.route('/view/<int:log_id>')
@login_required
def view(log_id):
    log = Log.query.get_or_404(log_id)
    exercises = Exercise.query.all()
    return render_template('view.html', exercises=exercises, log=log)



#-----------SHOW ADD-------------------------------------------------------------------------------------------------   
@views.route('/add')
@login_required
def add():
    exercises = Exercise.query.all()
    return render_template('add.html', exercises=exercises, exercise=None)



#-----------ADD TO POST-------------------------------------------------------------------------------------------------   
@views.route('/add', methods=['POST'])
def add_post():
    exercise_name = request.form.get('exercise_name').strip()  # Remove leading/trailing spaces
    standardized_name = exercise_name.upper()  # or .lower() for lowercase

    reps = request.form.get('reps') # request forms get is a get method that gets the data input by the user
    sets = request.form.get('sets')
    rest = request.form.get('rest')
    exercise_id = request.form.get('exercise-id') # exercise-id is a callable variable in the add.html

    if exercise_id:
        exercise = Exercise.query.get_or_404(exercise_id) # if statement that handles the error and the commit which saves the get data in the database
        exercise.name = standardized_name
        exercise.reps = reps
        exercise.sets = sets
        exercise.rest = rest
    else:
        existing_exercise = Exercise.query.filter_by(name=standardized_name).first()
        if existing_exercise:
            flash('Exercise with this name already exists!', category='error')
            return redirect(url_for('views.add'))  # Redirect back to the form

        new_exercise = Exercise(   # new exercise, stnadard way of naming a new data in the models
            name=standardized_name,
            reps=reps,
            sets=sets,
            rest=rest,
            log_id=current_user.id
        )

        try:
            db.session.add(new_exercise) # this adds the new data in the database
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # Rollback to prevent changes
            flash('Exercise with this name already exists!', category='error')

    return redirect(url_for('views.add'))

#-----------DELETE-------------------------------------------------------------------------------------------------   
@views.route('/delete/<int:exercise_id>') # a delete method for exercises
def delete(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id) # calls the exercise_id which is in the database
    db.session.delete(exercise) # deletes the exercise
    db.session.commit()
    return redirect(url_for('views.add'))

#-----------EDIT-------------------------------------------------------------------------------------------------   
@views.route('/edit/<int:exercise_id>')# a edit method for exercises
def edit(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)# calls the exercise_id in the database
    exercises = Exercise.query.all()# this is handled in the edit.html which you can change the name, reps, sets, and rest
    return render_template('edit.html',exercise=exercise,exercises=exercises)

#-----------ADD TO LOG-------------------------------------------------------------------------------------------------   
@views.route('/add_to_log/<int:log_id>', methods=['POST']) 
def add_to_log(log_id):
    # Fetching the log belonging to the current user
    user_log = current_user.logs.filter_by(id=log_id).first_or_404()
    
    selected_exercise = request.form.get('exercise-select')
    exercise = Exercise.query.get(int(selected_exercise)) 

    if exercise in user_log.exercises:
        flash('This exercise is already associated with this log!', category='error')
    else:
        user_log.exercises.append(exercise)
        db.session.commit()
        flash('Exercise added successfully to the log!', category='success')

    return redirect(url_for('views.view', log_id=log_id))

 
@views.route('/update/<int:exercise_id>',methods=['POST'])
def update(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    # Fetch data from the form submission
    exercise.name = request.form.get('exercise_name')
    exercise.reps = request.form.get('reps')
    exercise.sets = request.form.get('sets')
    exercise.rest = request.form.get('rest')
    # Update the exercise in the database
    db.session.commit()
    flash('Exercise updated successfully!', category='success')
    return redirect(url_for('views.index'))

#-----------REMOVE-------------------------------------------------------------------------------------------------   
@views.route('/remove_log/<int:log_id>') # removes logs, this is the same code for the delete 
def remove_log(log_id):
    log = Log.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return redirect(url_for('views.index'))

