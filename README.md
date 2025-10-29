# Vehicle Parking App
The Vehicle Parking App is a city-based web application designed to simplify the process of locating, booking, and managing parking spots across multiple cities and helps admins manage lots and spot status efficiently. 

## VIsual Demonstration
<p align="center">
<img width="400" height="768" alt="User Dashboard" src="https://github.com/user-attachments/assets/ff6f5be1-e094-46fb-be69-3d9e06fcc854" />
<img width="400" height="768" alt="Booking" src="https://github.com/user-attachments/assets/3295936f-2d50-4e6b-99d1-ebd646b1729d" />
</p>
<p align="center">
<img width="400" height="768" alt="Admin Dashboard" src="https://github.com/user-attachments/assets/99684d8c-a099-470d-9b2b-400db60d436a" />
<img width="400" height="768" alt="Admin Summary" src="https://github.com/user-attachments/assets/fd708d92-dd95-4e6f-a5f7-bad5958a4b6b" />
</p>

## User Features
- **City-Based Search**: Search and view available lots by selecting a city
- **Book & Release Spots**: Book the first available spot and release it after use
- **Parking History**: View summarized booking history with charts
- **User Profile**: Manage personal details

## Admin Features
- **Lot Management**: Add, edit, and manage parking lots.
- **Spot Managment**: View and delete available parking spots
- **System Statistics**: View application statistics and revenue charts
- **User Data Management**: View complete user details

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Jinja2 Templates
- **Database**: SQLAlchemy (SQLite)
- **Charts**: Matplotlib

## Project Structure
```
parking_app/
├── app.py                      # Main application logic and routes
├── models/
│   └── models.py               # SQLAlchemy models
├── instance/
│   └── database.db             # Local SQLite DB 
├── static/
│   ├── style.css               # Main CSS file
│   └── images/                 # Images and generated charts
├── templates/
│   ├── add_lot.html
│   ├── admin_dashboard.html
│   ├── admin_navbar.html
│   ├── admin_summary.html
│   ├── admin_search.html
│   ├── book.html
│   ├── edit_lot.html
│   ├── edit_profile.html
│   ├── login.html
│   ├── o_spot.html
│   ├── register.html
│   ├── release.html
│   ├── user_dashboard.html
│   ├── user_summary.html
│   ├── user_details.html
│   ├── view_spot.html
│   └── welcome.html               
├── env                         # Environment Variables
├── requirements.txt            # Python dependencies
└── README.md                   # Final documentation
```

