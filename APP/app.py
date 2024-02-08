from flask import Flask,render_template, session, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.sms_email import Send
from models import db


app = Flask(__name__)
app.secret_key = "f8fd933c-af3b-4e77-b6b9-cdb5f2dd42d3"

@app.route("/votes", methods=["GET", "POST"])
def votes():
    if session.get("voter_id"):
        return redirect(url_for("vote_route", token=session.get("token")))
    else:
        return redirect(url_for("login"))

@app.route("/vote")
def vote_route():
    candidate_group = db.get_candidates()
    voter = db.get_voter(session.get("email"), session.get("token"))
    return render_template("vote.html", voter=voter, candidate_group=candidate_group)

@app.route("/recordvote", methods=["GET", "POST"])
def recordvote():
    return request.form

@app.route("/login/", methods=["GET", "POST"])
def login():  
    if request.method == "GET": 
        if session.get("voter_id"):
            session.clear()
        token_from_get = request.args.get("token")
        session["token"] = token_from_get 
        return render_template("login.html")
    
    if request.method == "POST":
        email = request.form["email"]
        voter_passwd = request.form["password"]
        
        voter = db.get_voter(email=email,token=session.get("token"))

        if voter and check_password_hash(voter.passwordhash, voter_passwd):
            session["voter_id"] = voter.id
            session["email"] = voter.email
            return redirect(url_for("votes"))
        else:
            flash('Login failed. Check credentials or use your unique link.', 'info')
            token = session.get('token')
            return redirect(url_for("login", token=token))      
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        contact = request.form["contact"]
        passwd = generate_password_hash(request.form["password"])
        
        if (db.check_existance(contact=contact, email=email, type="Voter") == False):
            new_voter = db.register_voter(first_name=first_name,
                                          last_name=last_name,
                                          email=email,
                                          pwdhash=passwd,
                                          contact=contact)           
            flash('Succesfully Register! Go to login', 'success')
            send = Send(token=new_voter.token, first_name=new_voter.first_name)
            send.send_email(voter_email_address=new_voter.email)
            #send.send_sms(contact=new_voter.contact)
            return redirect(url_for('register'))
        flash('Registration failed. User Already Exist!', 'info')
        return redirect(url_for('register'))
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)