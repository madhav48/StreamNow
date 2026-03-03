"""

STREAMNOW  

. CREATED BY MADHAV AGRAWAL
. STARTED ON 18TH MARCH , 2022 AT 12:00 AM (HOLI FESTIVAL)



. STREAMNOW - YOUR MUSIC BUDDY
. MUSIC STREAMING APPLICATION 
. PYTHON SERVER BASED APPLICATION BUILT USING FLASK FRAMEWORK...


"""

from flask import Flask , redirect , render_template , request , jsonify , session , url_for , abort , make_response
import json

from matplotlib.style import use

with open("configs.json") as configs :
    params = json.load(configs)

app = Flask(__name__)
app.config['SECRET_KEY'] = params["SECRET_KEY"]                     # For Flask session....



import globalvars as glv

glv.Configs.params = params
glv.Storage.request = request
glv.Storage.session = session

glv.make_response.update(make_response)
glv.url_for.update(url_for)
glv.redirect.update(redirect)
glv.render_template.update(render_template)
glv.abort.update(abort)



from flask_login import LoginManager , current_user , login_user , login_required , logout_user

login_manager = LoginManager()
login_manager.init_app(app)

glv.Storage.current_user = current_user
glv.login_required.update(login_required)


from flask_bcrypt import Bcrypt
from flask_mail import Mail

bcrypt = Bcrypt(app)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params["verify-email-id"],
    MAIL_PASSWORD = params["verify-email-password"]
)
mail = Mail(app)

glv.Flask_Functions.bcrypt = bcrypt
glv.Flask_Functions.mail = mail


from flask_sqlalchemy import SQLAlchemy
import MySQLdb

app.config['SQLALCHEMY_DATABASE_URI'] = params["local_host"]
SQLALCHEMY_BINDS = {
    'sn_users':        params["local_host_sn_users"],
}
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
sn_users_sql_alchemy_db = SQLAlchemy(app)


sn_users_mysql_db = MySQLdb.connect(db = "sn_users" , user = params["mysql_user"] , passwd = params["mysql_password"])

glv.Database.sqlalchemy_sn_users_db = sn_users_sql_alchemy_db
glv.Database.mysql_sn_users_db = sn_users_mysql_db




import helper_modules.url_helper as url_helper

glv.is_safe_url.update(url_helper.is_safe_url)
glv.quoted_url.update(url_helper.quoted_url)
glv.unquoted_url.update(url_helper.unquoted_url)
glv.redirect_response.update(url_helper.redirect_response)
glv.render_response.update(url_helper.render_response)
glv.redirect_to_next.update(url_helper.redirect_to_next)
app.jinja_env.globals.update(quoted_url = glv.quoted_url)



import helper_modules.cookie_helper as cookie_helper

glv.is_cookie_storable.update(cookie_helper.is_cookie_storable)
glv.delete_cookies.update(cookie_helper.delete_cookies)
glv.set_cookies.update(cookie_helper.set_cookies)
glv.delete_session.update(cookie_helper.delete_session)


import helper_modules.mail_helper as mt

import helper_modules.flash_errors as fe
import helper_modules.flash_success as fs
import helper_modules.flash_warn as fw

from helper_modules.operations import *

import user_auths

# glv.create_user_object.update(user_auths.User.create_user_object)

# import user_account as ua



@app.route("/flash-sto" , methods = ["POST"])
def flash_sto() :
    fe.sess_time_out()
    return OP_SUCCESS




# Login - helper functions -----


@login_manager.user_loader
def load_user(user_auth_details):
    # user_auth_details --- userid&secret_password        
    return user_auths.load_user(user_auth_details)

    
@login_manager.unauthorized_handler
def unauthorized():
    return user_auths._unauthorized()


# Login - helper functions -----





# Webpages Functions---------------------


@app.route("/")
def index():
    
    # return jsonify(request.args.get("next"))
    # request.set_cookie("hii" , value = "hello")
    # return url_for("index" , next = "yhuyby ybybbbb")
    # return jsonify(bool(is_cookie_storable()))
    # return  abort(404)
    # return render_template("index.html" , request = glv.request_object)
    return render_template("index.html" , request = glv.Storage.request.cookies)
    # return render_template("index.html" , request = (request))
    
    # resp = make_response(render_template("index.html"))
    # resp.set_cookie('somecookiename', 'I am cookie' , secure = True)
    # return resp 


@app.route("/signup" , methods = ["POST" , "GET"])
def signup():
    return user_auths._signup()

        
@app.route("/signup/otp-verification/<string:slug>" , methods = ["GET" , "POST"])
def signup_otp_verification(slug):
    return user_auths._signup_otp_verification(slug)
    
            
@app.route("/signup/otp-verification/resend/<string:slug>" , methods = ["POST"])
def resend_signup_otp_verification(slug):
    return user_auths._resend_signup_otp_verification(slug) 
           
     
@app.route("/login" , methods = ["GET" , "POST"])
def login():  
    return user_auths._login(login_user)
    
    
@app.route("/logout")
@login_required
def logout():
    return user_auths._logout(logout_user)
    


@app.route("/forgot-password" , methods = ["POST" , "GET"])
def forgot_password():
    return user_auths._forgot_password()
    
    

@app.route("/forgot-password/change-password" , methods = ["POST" , "GET"])
def change_password():
    if request.method == "POST":
        
        red_resp = redirect_response("change_password")         
        next_red_resp = redirect_response("login")
        
        ch_user_password = ua.try_change_password(request , bcrypt , red_resp , next_red_resp , mail)
        if ch_user_password :          
            return next_red_resp
    
        return red_resp
    return "hllo"



@app.route("/exp - page / hujnjn")
@login_required
def exp_page():
    return render_template("exp-page.html")


@app.route("/exp-page/hii")
@login_required
def exp_2page():
    return render_template("exp-page.html")

if __name__ == "__main__":
    Flask.run(app , debug = True)