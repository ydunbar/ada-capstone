# ADA C-13 capstone project: Mentor Match  
## To start locally:  
### Set up database:  
cd into project directory  
$ . venv/bin/activate  
$ python  
$ from app import db  
$ from app.models import *  
$ db.create_all()  
$ Skill.generate_skills()  
### Run app:   
$ python run.py  
View in browser:  
http://localhost:5000/
