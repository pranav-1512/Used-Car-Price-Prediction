from project import app,db
from flask import render_template, redirect, request, url_for, flash,abort
from flask_login import login_user,login_required,logout_user
from project.models import Users,Predictions
from project.forms import LoginForm, RegistrationForm
from sklearn.preprocessing import StandardScaler
from wtforms.validators import ValidationError
import pickle
from flask_login import current_user
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
model = pickle.load(open('random_forest_regression_model.pkl', 'rb'))
@app.route("/",methods=['GET', 'POST'])

def index():
    form=LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        
        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user and user.check_password(form.password.data):
            #Log in the user
            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('welcome')

            return redirect(next)

        # If user doesn't exist in the database, prompt the user to register
        elif not user:
            flash('Username does not exist. Please register.', category='error')

        # If the password is incorrect, flash an error message
        elif not user.check_password(form.password.data):
            flash('Invalid email or password.', category='error')
    return render_template('index.html', form=form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('index'))
@app.route('/welcome')
@login_required
def welcome():
    return render_template('form.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = Users(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('index'))
    if form.errors:  # only true if there were errors during validation by WTForms
        for field, error in form.errors.items():
           
            flash(f"Error for {field}: {', '.join(error)}", category='error')
            
    return render_template('register.html', form=form)
standard_to = StandardScaler()
@app.route("/predict", methods=['POST'])
def predict():
    Fuel_Type_Diesel=0
    if request.method == 'POST':
        Year = int(request.form['Year'])
        Present_Price=float(request.form['Present_Price'])
        Kms_Driven=int(request.form['Kms_Driven'])
        Kms_Driven2=np.log(Kms_Driven)
        Owner=int(request.form['Owner'])
        
        Fuel_Type_Petrol=request.form['Fuel_Type_Petrol']
        print(type(Fuel_Type_Petrol))
        if(Fuel_Type_Petrol=='Petrol'):
                Fuel_Type_Petrol=1.0
                Fuel_Type_Diesel=0.0
                print(type(Fuel_Type_Petrol))
        else:
            Fuel_Type_Petrol=0
            Fuel_Type_Diesel=1
        Year=2023-Year
        Seller_Type_Individual=request.form['Seller_Type_Individual']
        Seller_Type_Individual = 1.0 if request.form.get('Seller_Type_Individual') == 'Individual' else 0.0
        Transmission_Mannual=request.form['Transmission_Manual']
        Transmission_Mannual = 1.0 if request.form.get('Transmission_Manual') == 'Manual' else 0.0
        prediction=model.predict([[Present_Price,Kms_Driven2,Owner,Year,Fuel_Type_Diesel,Fuel_Type_Petrol,Seller_Type_Individual,Transmission_Mannual]])
        print(prediction)
        output=round(prediction[0],2)
        print(output)
        predicted_prices = []
        next_years = range(Year,Year+5)
        for year in next_years:
            print(year)
            predicted_price = model.predict([[Present_Price,Kms_Driven2,Owner,year,Fuel_Type_Diesel,Fuel_Type_Petrol,Seller_Type_Individual,Transmission_Mannual]])
            predicted_prices.append(predicted_price)

                # Convert the lists to numpy arrays
        next_years = np.array(next_years)
        Year=2023-Year
        for i in range(0,5):
            next_years[i]=Year+i
            print(next_years[i])
        print(next_years)
        predicted_prices = np.array(predicted_prices)
        print(predicted_prices)
                # Scatter plot for Next 5 Years vs Predicted Prices
        fig, ax = plt.subplots()
        ax.scatter(next_years, predicted_prices, color='blue', marker='o')
        plt.xlabel('Next 5 Years')
        plt.ylabel('Predicted Prices')
        plt.title('Car Price Prediction - Next 5 Years vs Predicted Prices')
        path = "C:/Users/prana/Downloads/Flask/Flask/Flask_Login/project/static/plot1.png"
        # path = "C:/Users/prana/OneDrive/Documents/Material/MP/Flask/Flask/Flask_Login/static/plot1.png"
        # path = "C:/Flask/Flask_Login/project/static/plot1.png"
        plt.savefig(path)
        plt.close()
        if output<0:
            return render_template('index.html',prediction_texts="Sorry you cannot sell this car")
        else:
            if current_user.is_authenticated:
                user = Users.query.filter_by(email=current_user.email).first()
                Year=2023-Year
                current_user.update_prediction(output,Year,Present_Price,Kms_Driven)
                #db.session.commit()
                predictions = Predictions.query.filter_by(user_id=user.id).all()
                db.session.commit()
                # Generate the next 5 years

                # Generate the corresponding predicted prices for the next 5 years
                # return render_template('result.html', output=output,path=path,timestamp=int(time.time()))  
    #             result_content = render_template('result.html', output=output, path=path, timestamp=int(time.time()))
    
    #             # Return the result content to the main HTML page
    #             return render_template('form.html', result_content=result_content)
                
    # result_content = render_template('result.html', output=output, path=path, timestamp=int(time.time()))
    
    # # Return the result content to the main HTML page
    return render_template('form.html',result_content=prediction)
    # return render_template('result.html', prediction=output, predictions=predictions)  
@app.route('/history', methods=['GET'])
def history():
    if current_user.is_authenticated:
        user = Users.query.filter_by(email=current_user.email).first()
        predictions = Predictions.query.filter_by(user_id=user.id).all()
        show_table = True
    return render_template('display.html', predictions=predictions, show_table=show_table)





if __name__ == '__main__':
    app.run(debug=True)