from flask import Flask, render_template, request, redirect, url_for, flash , session
from models import db, User, Reservation, ParkingLot, ParkingSpot
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # use non-interactive backend
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='env')  
from datetime import datetime
import pytz

india = pytz.timezone('Asia/Kolkata')


app=Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db.init_app(app)


# --------------------------------WELCOME PAGE-----------------------------------
@app.route("/")
def welcome():
    return render_template("welcome.html")


# ---------------------------USER/ADMIN LOGIN PAGE-------------------------------
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["pwd"]

        user = User.query.filter_by(email=email).first()
        if user and user.password == pwd:
            if user.role == 1:
                return redirect(url_for('admin_dashboard',user_id=user.id))
            else:
                return redirect(url_for('user_dashboard',user_id=user.id))
        else:
            flash('Incorrect Email or Password')
            return render_template("login.html")

    return render_template('login.html')


# -------------------------REGISTRATION PAGE------------------------------------
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullname'].strip()
        email = request.form['email'].strip()
        password = request.form['pwd'].strip() 
        address = request.form['address'].strip() 
        pin_code = request.form['pin_code'].strip() 



        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            flash("User already Exist")
            return render_template('register.html')
        
        new_u = User(
            full_name=full_name,
            email=email,
            password=password,  
            address=address,         
            pin_code=pin_code,
            role=0
        )  
        db.session.add(new_u)
        db.session.commit()

        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template('register.html')


# -------------------------------USER DASHBOARD---------------------------
@app.route('/user_dashboard/<int:user_id>')
def user_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_time.desc()).limit(7).all()
    
    for lot in lots:
        lot.available_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count() 

    return render_template('user_dashboard.html', user=user, lots=[], reservations=reservations)


# ----------------------------------SEARCH ROUTE-----------------------------
@app.route('/search_by_city/<int:user_id>', methods=['POST'])
def search_by_city(user_id):
    city = request.form['city']
    user = User.query.get(user_id)
    lots = ParkingLot.query.filter_by(city=city).all()
    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_time.desc()).limit(7).all()

    for lot in lots:
        lot.available_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()

    return render_template('user_dashboard.html', user=user, lots=lots, reservations=reservations, city_selected=city)


# -------------------------------SPOT BOOKING--------------------------------
@app.route('/book/<int:lot_id>/user/<int:user_id>', methods=['GET', 'POST'])
def book_spot(lot_id, user_id):
    lot = ParkingLot.query.get(lot_id)
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')

        if not spot:
            return redirect(url_for('user_dashboard', user_id=user_id))

        res = Reservation(
            user_id=user_id,
            spot_id=spot.id,
            vehicle_number = vehicle_number,
            parking_time=datetime.now(india),  
            cost_per_unit_time=lot.price
        )

        spot.status = 'O'
        db.session.add_all([res])
        db.session.commit()

        return redirect(url_for('user_dashboard', user_id=user_id))

    return render_template("book.html", lot=lot, spot=spot, user_id=user_id)


# -------------------------------RELEASING SPOT--------------------------------
@app.route('/release/<int:res_id>', methods=['GET', 'POST'])
def release_spot(res_id):
    reservation = Reservation.query.get_or_404(res_id)
    now = datetime.now(india)
    
    if request.method == "POST":
        reservation.leaving_time = now
        reservation.spot.status = 'A'
        db.session.commit()
        return redirect(url_for("user_dashboard", user_id=reservation.user_id))
    
    start = reservation.parking_time
    if start.tzinfo is None:
        start = india.localize(start)

    diff = now - start
    total_hrs = diff.total_seconds() / 3600
    total_cost = round(total_hrs * reservation.cost_per_unit_time, 2)
    

    return render_template("release.html", res=reservation, current_time=now, total_cost=total_cost)


# -------------------------------CURRENT USER SUMMARY---------------------------
@app.route("/summary/<int:user_id>")
def summary(user_id):
    user = User.query.get_or_404(user_id)
    reservations = Reservation.query.filter_by(user_id=user.id).all()

    used = {}
    for r in reservations:
        lot_name = r.spot.lot.prime_location_name
        used[lot_name] = used.get(lot_name, 0) + 1

    df = pd.DataFrame(list(used.items()), columns=["Lot", "Count"])
    plt.figure(facecolor='#e6ccff')
    plt.bar(df['Lot'], df['Count'], color="#e9a617f9")
    plt.xlabel('Parking Lots')
    plt.ylabel('Usage Count')
    plt.title('Lot Usage Summary')

    # Saving image
    chart_path = os.path.join('static', 'summary_chart.png')
    plt.savefig(chart_path)
    plt.close()

    return render_template("user_summary.html", user=user)


# ------------------------------Admin Dashboard--------------------------------
@app.route("/admin_dashboard")
def admin_dashboard():
    admin = User.query.filter_by(role=1).first()
    lots = ParkingLot.query.all()
    city_map = {}

    for lot in lots:
        lot.occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        lot.spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        city_map.setdefault(lot.city, []).append(lot)

    return render_template("admin_dashboard.html", admin=admin, city_map=city_map)


# ------------------------------USER DETAILS----------------------------
@app.route('/user_details')
def user_details():
    admin = User.query.filter_by(role=1).first() 
    users = User.query.filter(User.role != 1).all()
    return render_template('user_details.html', users=users, admin=admin)


# --------------------------------SEARCH ---------------------------------
@app.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    admin = User.query.filter_by(role=1).first()
    results = {}
    stype = term = ""

    if request.method == 'POST':
        stype = request.form['search_by']
        term = request.form['search_term'].strip()

        if stype == 'user_id' and term.isdigit():
            results = Reservation.query.filter_by(user_id=int(term)).all()

        elif stype == 'lot_name':
            matched_lots = ParkingLot.query.filter(
                ParkingLot.prime_location_name.ilike(f"%{term}%")
            ).all()

            for lot in matched_lots:
                lot.occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
                lot.spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
                results.setdefault(lot.city, []).append(lot)  

    return render_template('admin_search.html',admin=admin,results=results,stype=stype,term=term)


# -------------------------------ADMIN SUMMARY---------------------------------
@app.route('/admin_summary')
def admin_summary():
    admin = User.query.filter_by(role=1).first()

    #Pie Chart
    pie_data={}
    reservations = Reservation.query.all()

    for r in reservations:
        if r.leaving_time:
            lot = r.spot.lot.prime_location_name
            duration = (r.leaving_time - r.parking_time).total_seconds() / 3600
            revenue = duration  * r.cost_per_unit_time 
            pie_data[lot] = pie_data.get(lot, 0) + revenue
    df = pd.DataFrame(list(pie_data.items()), columns=["Lot", "Revenue"])
    
    plt.figure(figsize=(16,14), facecolor="#e6ccff")
    plt.pie(df["Revenue"], labels=df["Lot"], autopct='%0.2f%%',  textprops={'fontsize': 25})
    plt.savefig('static/pie_chart.png')
    plt.close()

    # Bar chart
    lots = ParkingLot.query.all()
    av, oc = 0, 0

    for lot in lots:
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').first()
        if occupied:
            oc += 1
        else:
            av += 1
            
    plt.figure(figsize=(16,14),facecolor="#e6ccff")
    plt.bar(['Occupied Lots', 'Available Lots'], [oc, av], color=['red', 'green'])
    plt.ylabel("Number of Lots",fontsize=25)
    plt.title("Empty vs Occupied Parking Lots", fontsize=28)
    plt.xticks(fontsize=23)  
    plt.yticks(fontsize=23)
    plt.savefig('static/bar_chart.png')
    plt.close()

    return render_template('admin_summary.html',pie_chart='pie_chart.png',bar_chart='bar_chart.png', admin=admin)


# --------------------------------Edit Profile--------------------------------
@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form['fullname'].strip()
        user.email = request.form['email'].strip()
        user.address = request.form['address'].strip()
        user.pin_code = request.form['pin_code'].strip()
        pwd = request.form['pwd'].strip()
        confirm = request.form['confirm_pwd'].strip()
        if pwd:
            if pwd == confirm:
                user.password = pwd
            else:
                flash("Passwords do not match.")
                return render_template("edit_profile.html", user=user)
        db.session.commit()
        if user.role == 1:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard',user_id=user.id))
        
    return render_template('edit_profile.html', user=user)


# -----------------------GENERATE SPOT NAMES FUNCTION-----------------------
def generate_spot_name(lot, start=1, end=None):
    prefix = lot.prime_location_name[0].upper()
    end = end or lot.max_number_of_spots
    for i in range(start, end + 1):
        spot = ParkingSpot(
            lot_id=lot.id,
            spot_name=f"{prefix}{i}",
            status='A'
        )
        db.session.add(spot)


# -------------------------------Add Lot---------------------------------
@app.route("/add_lot", methods=["GET", "POST"])
def add_lot():
    city = request.args.get("city") 
    admin = User.query.filter_by(role=1).first()
    
    if request.method == "POST":
        lot = ParkingLot(
            prime_location_name=request.form["location"].strip().title(),
            address=request.form["address"].strip().title(),
            pin_code=request.form["code"].strip(),
            city=request.form["city"].strip(),
            price=int(request.form["price"]),
            max_number_of_spots=int(request.form["spot_no"])
        )
        db.session.add(lot)
        db.session.flush()

        generate_spot_name(lot)

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template("add_lot.html", city=city, user=admin)


# -----------------------------EDIT LOT--------------------------------
@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    admin = User.query.filter_by(role=1).first()
    lot = ParkingLot.query.get_or_404(lot_id)
    old = lot.max_number_of_spots
    occ = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()

    if request.method == 'POST':
        new = int(request.form['spot_no'])
        if new < old and occ > 0:
            flash(f"Cannot reduce spots — {occ} occupied.", "error")
            return redirect(url_for('edit_lot', lot_id=lot.id))

        lot.prime_location_name = request.form['location'].strip().title()
        lot.address = request.form['address'].strip().title()
        lot.pin_code = request.form['code'].strip()
        lot.city = request.form['city'].strip()
        lot.price = request.form['price']
        lot.max_number_of_spots = new

        db.session.flush()

        # spot naes
        if new > old:
            generate_spot_name(lot, start=old + 1, end=new)
        elif new < old:
            extra = ParkingSpot.query.filter_by(lot_id=lot.id,).order_by(ParkingSpot.id.desc()).limit(old - new).all()
            for s in extra:
                db.session.delete(s)

        db.session.commit()
        return redirect(url_for('admin_dashboard', user_id=admin.id))

    return render_template('edit_lot.html', lot=lot, user=admin)


# ---------------------------------DELETE LOT-------------------------
@app.route("/delete_lot/<int:lot_id>", methods=["POST"])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    occupied_spots = [s for s in lot.spots if s.status == 'O']
    if occupied_spots:
        flash("Cannot delete lot. Some spots are still occupied.")
    else:
        for spot in lot.spots:
            db.session.delete(spot)
        db.session.delete(lot)
        db.session.commit()
        flash("Lot deleted successfully.")
    
    return redirect(url_for('admin_dashboard'))  
  

# -------------------------------VIEW SPOT-------------------------------------
@app.route('/view_spot/<int:spot_id>')
def view_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    return render_template('view_spot.html', spot=spot)


# --------------------------------DELETE SPOT-------------------------------
@app.route('/delete_spot/<int:spot_id>', methods=['POST'])
def delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)

    Reservation.query.filter_by(spot_id=spot.id).delete()

    lot = ParkingLot.query.get(spot.lot_id)
    lot.max_number_of_spots -= 1

    db.session.delete(spot)
    db.session.commit()

    flash("Spot deleted ")

    return redirect(url_for('admin_dashboard',lot_id=spot.lot_id))


# ------------------------------OCCUPIED SPOT DETAILS-----------------------
@app.route("/occupied_spot/<int:spot_id>")
def occupied_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    res = Reservation.query.filter_by(spot_id=spot.id, leaving_time=None).first()
    user = User.query.get(res.user_id)

    start = res.parking_time
    if start.tzinfo is None:
        start = india.localize(start)

    now = datetime.now(india)
    diff = now - start
    total_hrs = diff.total_seconds() / 3600
    total_cost = round(total_hrs * res.cost_per_unit_time, 2)
    
    return render_template("o_spot.html", spot=spot, res=res, user=user, total_cost=total_cost)



def create_auto_admin():
    if_exists = User.query.filter_by(role=1).first()
    if not if_exists:
        admin = User(email='admin@app.com',
            password='9999',
            full_name="Admin",
            address="None",
            pin_code=99999,
            role=1)
        db.session.add(admin)
        db.session.commit()
        print("Admin created!")
    else:
        print("Admin already exists.") 


if __name__ == "__main__":
    with app.app_context(): 
        db.create_all()
        lots = ParkingLot.query.all()
        db.session.commit()
        create_auto_admin()
    app.run(debug=False)