
import re
import time
import string
import json
from numpy.random import randint
from random import choice 
from MySQLdb import _mysql , _exceptions

import helper_modules.flash_errors as fe
import helper_modules.flash_success as fs
import helper_modules.flash_warn as fw
import helper_modules.cookie_helper as hc
import helper_modules.mail_helper as mt
from helper_modules.operations import *


with open("configs.json") as configs :
    params = json.load(configs)
    
mysql_passwd = params["mysql_password"]
db_user = params["mysql_user"]


class User():
    
    """
    
    The main class to log in user...

    : Flask login uses the object of this class to log in user by saving it in session and in `rememberToken` if `rememnber` = True while logging.
    : Flask login saves the information returned by the object function `get_id()` which returns a tuple containing `userid` at zeroth index and `secret_pass` at first index.
    
        :: `userid` --> unique id for every user which is 8-digit long and user can access it and can log into the account using it also..
        :: `secret_pass` --> A secret password that is 60 digit long and is randomly generated.. Uses of `secert_pass` ---->

            .. Provide double layer security while loading user thorugh `user_loader`(60-digit long i.e. not easy to guess)
            .. Used to relogin the saved user. User can relogin using `userid` and `secret_pass` only i.e stored in cookies.. (If user allows to save login details then only...) 
    
    
    : Attributes of `User` class objects --->
        .. name
        .. email
        .. id 
        .. secret_pass
        .. is_authenticated ----> Returns True if user is logged in and False if user dosen't
        .. is_active ----> Returns True if user is logged in and False if user dosen't
        .. is_anonymus ----> Returns False if the user is logged in and True if the user is not logged in.
        .. error ----> If any error occurs like `SOMEWENTWRONG` , `SERVERCONTACTERROR` , it get stored in error attribute. 
    : To access attributes ---> Use flask_login.current_user.attributename
    : An example to access attribute --
        current_user.is_authenticated
        
        
    : Useful Functions of the `User` class objects --->
        .. get_id() --> Returns tuple containing userid and secret password.
        .. get_email() --> Returns user email.
        .. get_name() --> Returns user name.
    : The most useful function is `get_id` which is also used by `user_loader` of `flask_login`
    
    """
    
    
    
    def __init__(self , flash_error =  False , **auth_details):
        
        
        """
        . Function makes the user object by assigning all the attributes and functions according to the details passed in constructor        
        
        : flash_eroor --> If any error encounters then the message should be flashed or not... (Default value = False i.e do not have to flash any message)
        
        : auth_details --> All authetication details to passed in this variable ...
        : An example of above variable .
            User(userid = "123" , secret_pass = "xyz")
                  
        : Morover the constructor is mainly focused on taking authentication details and analysing them to make the user object...
        : If the user object is not made then user.id and others are None and if any error occurs while making user object then it gets store in user.error and also user.is_anonymous = True.  
        : If user creation suceessfull then attributes are assigned...
        
        """
        
        # Removing the extra keys --->

        for key , value in auth_details.items():
            if not value:
                auth_details.pop(key)
                
                
        """Setting all the values to None i.e. creating an anonymous user first..."""
            
        self.name = None
        self.email = None
        self.id = None
        self.secret_pass = None
        self.is_authenticated = False
        self.is_active = False
        self.is_anonymous = True
        self.error = None
    
    
    
        """Analysing authentication details and creating a user object.."""
    
        if ("user_id" in auth_details) and ("secret_pass" in auth_details):
        
            """
            --> Login user with the help of `userid` and `secret_pass` ...
                .. Used by `user_loader` of flask_login And `log_saved_user`
                    ... log_saved_user --> If user wants to relogin into the account provided the account login details are saved while previous logout... 
            """
            
            self.make_from_idnsecpass(auth_details["user_id"] ,auth_details["secret_pass"] , flash_error)           
                   
            
        
        elif ("user_email" in auth_details) and ("password" in auth_details) and ("bcrypt" in auth_details):
            
            """
            --> Login user with the help of `user_email` and `password` ...
            """
            
            self.make_from_emailnpass(auth_details["user_email"] , auth_details["password"] , auth_details["bcrypt"] , flash_error)
    
    
        
    def set_user_details(self ,user_name  , user_email , userid , secret_pass ):
        
        """
        Used to set the user object attributes after matching the auth details... 
        
        """
    
        self.name = user_name
        self.email = user_email
        self.id = userid
        self.secret_pass = secret_pass
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.error = None
    
    
    
    def make_from_idnsecpass(self , user_id , secret_pass , flash_error):
        
        """
        
        """
        
        user_account = get_user_account_by_id(user_id)
        
        if not user_account:
            if flash_error :
                fe.no_acc_found()
            return
        
        if user_account == SERVERPROBLEM:
            if flash_error :
                fe.server_contact_error()
            self.error = SERVERPROBLEM
            return
            
        
        user_name , user_email , db_secret_pass = user_account
        
        if secret_pass != db_secret_pass:
            if flash_error :
                fe.no_acc_found()
            self.error = LOGGEDOUT
            return
        
        self.set_user_details(user_name, user_email, user_id , secret_pass)
        return self      
        
    def make_from_emailnpass(self ,user_email ,  form_password , bcrypt , flash_error = True):
        user_account = get_user_account(user_email)
        
        if not user_account:
            if flash_error:
                fe.no_acc_found()
            return
        
        if user_account == SERVERPROBLEM:
            if flash_error :
                fe.server_contact_error()
            self.error = SERVERPROBLEM
            return

        
        user_id , user_name , secret_pass , db_password = user_account
        
        if not bcrypt.check_password_hash(db_password,  form_password):
            if flash_error:
                fe.incorrect_password()
            return
        
        self.set_user_details(user_name, user_email, user_id , secret_pass)
        return self    
    
      
    
    @staticmethod
    def load_user(user_auth_details):
        
        """
        
        Function to load user with the help of user id and secret_pass
        
        : user_auth_details --> string containing userid and secret password..
            ... Example(user_auth_details) - "123&xyz" 
        
        """
        
        
        try:
            userid , secret_pass = user_auth_details.split("&")
            user =  User(user_id = userid , secret_pass = secret_pass)
            
            if user.is_anonymous:
                if user.error == LOGGEDOUT:
                    fw.logged_out()
                return
            return user
            
        except Exception:
            return     
        
        
        
        
    def get_id(self):
        if self.id:
            return f"{self.id}&{self.secret_pass}"  # Passes as the user_auth_details in load_user
        return
    
    def get_email(self):
        return self.email
    
    def get_name(self):
        return self.name
    
    def __str__(self):
        return f"Id : {self.id} ,  Name : {self.name} , Email : {self.email}"





"""

Informative Functions ---------------------------------------------------------------


"""


def get_request_values(request , *args):

    return_values = []
    
    for item in args :
        return_values.append(request.form.get(item))
    
    return return_values

def validate_password(password):
    
    if (len(password)<8):
        return
    
    elif not re.search("[a-z]", password):
        return 
    
    elif not re.search("[A-Z]", password):
        return
    
    elif not re.search("[0-9]", password):
        return
        
    else:
        return True

def get_hashed_password(password , bcrypt):
    return bcrypt.generate_password_hash(password , 10).decode('utf-8')

def get_user_name(user_email):
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        db.query(f"""SELECT `user_name` FROM users WHERE user_email = '{user_email}' """)
        user_account = db.store_result().fetch_row(maxrows = 0)
        
        
        if user_account:
            user_account = user_account[-1]
            return user_account[0].decode() 
        return user_account

    except Exception:
        return SERVERPROBLEM
    
def get_user_account(user_email):
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        db.query(f"""SELECT `userid` , `user_name` , `secret_pass` , `password` FROM users WHERE user_email = '{user_email}' """)
        user_account = db.store_result().fetch_row(maxrows = 0)
        
        
        if user_account:
            user_account = user_account[-1]
            return user_account[0].decode() , user_account[1].decode() , user_account[2].decode() , user_account[3].decode()
        return user_account

    except Exception:
        return SERVERPROBLEM
    
def get_user_account_by_id(id):
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        db.query(f"""SELECT `user_name`, `user_email` , `secret_pass` FROM users WHERE userid = '{id}' """)
        user_account = db.store_result().fetch_row(maxrows = 0)
        
        if user_account:
            user_account = user_account[-1]
            return user_account[0].decode() , user_account[1].decode() , user_account[2].decode()
        return user_account

    except Exception:
        return SERVERPROBLEM
    
def get_user_account_password(user_email):
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        db.query(f"""SELECT cast(`password` as CHAR) from `users` WHERE user_email = '{user_email}' """)
        user_account_passwd = db.store_result().fetch_row(maxrows = 0)
        
        if user_account_passwd:
            return user_account_passwd[0][0].decode()
        fe.no_acc_found() 
        return user_account_passwd

    except Exception:
        fe.server_contact_error()
        return None

def get_email_from_req(slug):
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
                
        db.query(f"""SELECT `user_email` FROM new_acc_req WHERE slug = '{slug}' """)
        user_req_email = db.store_result().fetch_row(maxrows = 0)
        
        if user_req_email :
            return user_req_email[-1][0].decode()
        return 

    except AssertionError:
        fe.server_contact_error()
        return None

def get_req_otp(slug):
        
    try:

        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
                
        db.query(f"""SELECT `user_email` , `otp` , `user_name` FROM new_acc_req WHERE slug = '{slug}' """)
        user_req_email_n_otp = db.store_result().fetch_row(maxrows = 0)
        
        if user_req_email_n_otp != ():
            user_req_email_n_otp = user_req_email_n_otp[-1]
            return user_req_email_n_otp[0].decode() , user_req_email_n_otp[1].decode(), user_req_email_n_otp[2].decode()
        return 

    except AssertionError:
        fe.server_contact_error()
        return None
    

"""

Informative Functions ---------------------------------------------------------------


"""



def delete_saved_user_info(request , *resp):
    
    """Funcion deletes the cookies which have any information for logging in user..""" 
    
    for response in resp :   
        hc.delete_cookies(request , response , "saved-log-in-details"  , "saved-email")    
    
    return





def signup_request(bcrypt, session , mail , request , red_resp):
    
    name, email  , password = get_request_values(request , 'name'  , 'email' , 'password')
    
    delete_saved_user_info(request , red_resp)
    
    if None in (name , email , password):
        fe.some_went_wrong()
        return

    
    account = get_user_account(email)
    
    if account :
        if account != SERVERPROBLEM:
            fe.already_acc_exists()
        values = {"name": name,
                "email" : email}
        
        session["user-signup-details"] = values
        return 
    
        
    slug = add_new_acc_req(name , email , password , bcrypt, session, mail)       
    
    if not slug:
        return 
    
    return slug          
    

def add_new_acc_req(user_name , user_email , password , bcrypt , session , mail):
    
    values = {"name":user_name,
        "email" : user_email}
        
    if not validate_password :
        fe.pswd_format_nt_crct()
        session["user-signup-details"] = values 
        return None

    
    hashed_password = get_hashed_password(password , bcrypt)
    otp = randint(111111,999999)
    
    
    verify_mail = mt.send_verify_mail(user_email, otp , user_name , mail)
    if not verify_mail:
        session["user-signup-details"] = values 
        return None
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
    
        # Generating slug ----
        while True:
            
            slug = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(15))
            
            db.query(f"""SELECT `sno`  FROM `new_acc_req` WHERE slug = '{slug}' """)
            user_req = db.store_result().fetch_row(maxrows = 0)
            
            if not user_req:
                break
            
        # Deleting the old entry if exists...
        try:
            db.query(f"""DELETE FROM `new_acc_req` WHERE `new_acc_req`.`user_email` = '{user_email}'""")
        except Exception:
            pass
                
        db.query(f"""INSERT INTO `new_acc_req` (`user_name`, `user_email`, `password`, `slug` , `otp`) VALUES ('{user_name}', '{user_email}', "{hashed_password}", '{slug}' , '{otp}' );""")
        
        session["user-signup-details-email"] = user_email 
        
        return slug       

    except AssertionError:
        
        fe.server_contact_error()
        session["user-signup-details"] = values 
        return None


def check_signup_otp(slug , session , request , mail , next_red_resp):
    
    req_otp = get_req_otp(slug)
        
    if not req_otp:
        fe.sess_time_out()        
        
        return
    
    email  , db_otp , user_name = req_otp
    
    if (not email) or ("user-otp-email" not in session) or (email != session["user-otp-email"]):
        fe.sess_time_out()        
        return
    
    form_otp = get_request_values(request , 'otp')[-1]
    
    if form_otp == str(db_otp) :
        new_acc = create_new_account(email, mail)
        
        hc.delete_session(session , "user-otp-email")
        
        if not new_acc :
            
            hc.delete_session(session , "user-otp-email")
            return
        
        
        """# Deleting if any saved info exists ---"""
        delete_saved_user_info(request , next_red_resp)               
        hc.delete_session(session , "log-in-details")
        
        hc.set_cookies(request , next_red_resp,("saved-email" , email , 15*24*60*60 ))
        return OP_SUCCESS
            
    else:
        fe.otp_not_crct()
        session["user-signup-details-email"] = email
        hc.delete_session(session , "user-otp-email")

        return OTP_ERROR



def create_new_account(user_email, mail):
    
    account = get_user_account(user_email)
    
    if account:
        if account != SERVERPROBLEM:
            fe.already_acc_exists()
        return None
      
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
                
        db.query(f"""SELECT `user_name` , `password` , `time`  FROM new_acc_req WHERE user_email = '{user_email}' """)
        user_details = db.store_result().fetch_row(maxrows = 0)[-1]    
        user_name , password , req_ent_time = user_details[0].decode() , user_details[1].decode() , user_details[2].decode()
        
        # Checking the 5-min time limit :
        req_time = time.mktime(time.strptime(req_ent_time , '%Y-%m-%d %H:%M:%S'))        
        if req_time + 300 <= time.time() :
            fe.sess_time_out()
            return None
        
        
        # Creating a unique userid:
        while True :

            userid = randint(11111111,99999999) # 8-digit id
            
            db.query(f"""SELECT `sno`  FROM `users` WHERE userid = '{userid}' """)
            user_account = db.store_result().fetch_row(maxrows = 0)
            
            if not user_account:
                break              
            
        # Creating a secret_password (for login) ....   
    
        secret_pass = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(60))                              #60-char long secret_pass
        
        
        
        # Final - Main Step -----
        db.query(f"""INSERT INTO `users` (`user_name`, `user_email`, `password`, `userid`, `secret_pass`, `data`) VALUES ('{user_name}', '{user_email}', "{password}",  "{userid}", "{secret_pass}", '');""")
        
        
        # Delete the request.....
        try:
            db.query(f"""DELETE FROM `new_acc_req` WHERE `new_acc_req`.`user_email` = '{user_email}'""")
        except Exception:
            pass
        
        # Sending confirmation email...
        mt.send_account_create_success_email(user_email , user_name , mail)
        
        fs.acc_create_success()
        return True

    except AssertionError:
        fe.server_contact_error()
        return None



"""


Login Functions -------------------------------------------------------------


"""


def get_saved_users(request):
 
    """
    
    --> returns None (If there is no user saved) or tuple of (True , `user_name` , `user_email`) [Details of the saved user..] 
        ... The True is used to tell jinja templating to show an extra option of looging into the saved account..
    
    Used to get the saved user account to show on the login page if saved during logout so we can relogin them...
        ... request.cookies are used to get informatiion about the saved_details
            And then details are verified through `User` class...
            And approprivate values are returned..
    
    """ 
 
      
    if ("saved-log-in-details" in request.cookies):
        saved_log_in_details = request.cookies.get("saved-log-in-details")
    
        try:
            userid , secret_pass = saved_log_in_details.split("&")
            user = User(user_id = userid , secret_pass = secret_pass )
            
            if not user.is_anonymous: 
                return True , user.name , user.id , user.email
 
            else:
                return
        
        except AssertionError:
                return                 
                



def log_user(user , login_user , request , next_red_resp , remember = True):
    
    """
    
    --> returns userid 
    The final most function to log in the user...
    
    login user and flash message and delete the previous saved cookies... and returns userid
    
    """
    
    login_user(user , remember = bool(remember))
    fs.login_success()    
    
    delete_saved_user_info(request , next_red_resp)
    return user.get_id()


    
def try_login_user(request ,  same_red_resp , next_red_resp, login_user , bcrypt , session , mail):
    
    
    """
    
    --> return None if user is not logged in due to any reason or userid if user logged in... 
    
    Function helps to login the user by checking various parameters.. and then flashes messages according to the errors occured.. 
    
    
    # Checks for the values step by step  and if the values are found then try to login the user with the help of those values..
    
    Values Finding prefferenece..
    
        1. saved_userid --> Helps to login the saved user (User svaed while logout)....
        2. Email And Password - Normal login using email and password...    
    
    
    # Parameters taken ...

        ... request -> Used to get login details
        ... same_red_resp --> Response of same (login) page if the user is not logged in due to any issue occured in between. Used to store or delete cookies...
        ... next_red_resp --> Response of next page to which the user is being redirected after successfull login. Used to store or delete cookies.. 
        ... login_user --> flask_login.login_user . Used to login user..
        ... bcrypt --> flask_bcrypt.bcrypt , pasword encrypter. Used to match the password..
        ... session --> Store or delete login details..
        
        
    """
       
    
    """
    # If user saved login details --->
    # """
    
    saved_userid = get_request_values(request, "saved-userid")[-1]
    
    if saved_userid:
        
        if "saved-log-in-details" in request.cookies:
            saved_user = get_login_saved_user(saved_userid= saved_userid , request = request)
            
            if saved_user in (None , SERVERPROBLEM , SOMEWENTWRONG):
                
                """User object does not exists."""
                
                if not saved_user:
                    hc.delete_cookies(request , same_red_resp , "saved-log-in-details")
                return
                        
            return log_user(saved_user , login_user , request , next_red_resp)

        else:
            return
    
    else:
        
        """If user tried to login into another account then delete all the saved account info 0even if the login is not successfull..."""
        hc.delete_cookies(request , same_red_resp , "saved-log-in-details")
        
        
        
    """
    
    Logging user with the help of user email and password...
    
    """
    
    user_email , form_password , remember = get_request_values(request , "email" , "password" , "remember")
        
    if None not in (user_email , form_password):
        
        user = get_login_user_using_email_n_pass(user_email , form_password , remember , session , bcrypt)
        if user:
            """If user object made successfully..."""
            
            mt.send_new_login_detect(user.email , user.name, mail)
            return log_user(user , login_user , request , next_red_resp , remember= remember)
        return
    return


    
def get_login_saved_user(saved_userid, request):
    
    """
    --> returns None / SOMEWENTWRONG / SERVERPROBLEM if any eroor occurs or `User` class object if successfully made..     
    
    Function helps to log in the user which is saved in the cookies.. when user allowed us to save while logout..
    
        Takes saved user id and request as argument..
            Get all the details from cookies and the try getting user id and secret password by splitting and then matching the user id prsent in log in forms and cookies and the try to make user object using `User` class..
            
            If any eroor occrrs while creating user then function returns None (Problem in saved cookies or secret_pass not matching..) / SOMEWENTWRONG (user ids are different in forms and cookies..) / SERVERPROBLEM (Server Issue)
    
        Example - get_login_saved_user(123 , request)
        
    """
    
    try:
        saved_log_in_details = request.cookies.get("saved-log-in-details")
        userid , secret_pass = saved_log_in_details.split("&")
        
        if userid == saved_userid:
            user = User(flash_error=True  , user_id = userid , secret_pass = secret_pass)
                       
            if not user.get_id():
                if user.error != SERVERPROBLEM:
                    
                    """Exceute when the user object can't be made because of wrong user id or secret password""" 
                    return
                
                return SERVERPROBLEM
                
            else:
                
                """Execute when the user object is successfully made..."""
                return user
            
        fe.some_went_wrong()
        return SOMEWENTWRONG        
                        
    except Exception:
        return 
    
    
def get_login_user_using_email_n_pass(user_email , form_password , remember , session , bcrypt):
    
    """
    
    --> returns None if user object is not made (due to incorrect authentication details) or `User` class object if object is made...
    
    Function helps to log on user with the help of the email and password provided..
    
    """
            
    remember_check = "unchecked"
    if remember:
        remember_check = "checked"

    user = User(flash_error= True , user_email= user_email , password = form_password , bcrypt= bcrypt)
    
    if not user.get_id():
        if user.error != SERVERPROBLEM:
            
            """Exceute when the user object can't be made because of wrong email or incorrect password""" 
            return
        
        session["log-in-details"] = {
                        "email" : user_email,
                        "remember_check" : remember_check
                            }    
        return
        
    else:
        
        """Execute when the user object is successfully made..."""
        return user



"""


Login Functions -------------------------------------------------------------


"""






"""


Forgot Password Functions -------------------------------------------------------------


"""



def send_change_password_link(request, mail):
    
    
    """
    
    --> Returns `Success...` if the link is sent successfully to the email else return the problem occured like --->
        ..SERVERPROBLEM
        ..MAIL_PROBLEM
        ..SOMEWENTWRONG
        
        
    Function to generate an password changing link and sending it to the user email so that the user can change the password of the account by accessing it from the registered email...
    
        At first generates the token and id and stores it in the database with email after confirming the valid email thorgh the function   `get_user_name` and `generate_pass_link`..
        
        After this the function tries to send the mail and then returns the values as mentioned above...

    """
        
    email = request.args.get("email")
    
    if not email :
        return SOMEWENTWRONG    
    
    user_name = get_user_name(email)
    
    if user_name:
        
        if user_name == SERVERPROBLEM:
            return SERVERPROBLEM
                     
        ch_pass_details = generate_pass_link(email)
        
        if ch_pass_details == SERVERPROBLEM:
            return ch_pass_details
        
        else:
                
            """Excecutes when token and id are generated and stored successfully..."""
                    
            token , id = ch_pass_details

            link_mail = mt.send_change_pass_mail(mail , email, user_name , token , id)
            
            if not link_mail:
                return MAIL_PROBLEM

            return "Success..."
    
    return NOACCFOUND
    




def generate_pass_link(email):
    
    
    """
    
    --> Returns a tuple of (token , id) on a successfull run oof the function.. Else returns SERVERPROBLEM if any problem occurs..
    
    Function used to generate token and id and storing them in the database.. 

        First of all it delete all the old requests associated with that email and them generates token and id(slug) respectively.. and then tries to store them in the database...
        
            .. token - A 6-digit number (not unique)
            .. id(slug) - 100-char long
            
                :Two parameters?-(id and token) 
                    ::For double security of cracking the password change link..
        
    """
    
    
    try:

        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        try:
            # Delete the old request (if any).....
            db.query(f"""DELETE FROM `forget_pass` WHERE `forget_pass`.`user_email` = '{email}'""")
        except Exception: 
            pass
        
        
        token = randint(111111,999999) 
        
        # Creating a unique slug:
        while True :
            
            
            slug = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(100))
            
            db.query(f"""SELECT `user_email`  FROM `forget_pass` WHERE slug = '{slug}' """)   # 60-Char long..
            user_request = db.store_result().fetch_row(maxrows = 0)
            
            if not user_request:
                break
        
        
        # Final - Main Step -----
        db.query(f"""INSERT INTO `forget_pass` (`user_email`, `slug`, `token`) VALUES ('{email}', '{slug}', "{token}");""")
        
        return token , slug 
    
    except Exception:
        return SERVERPROBLEM
    
    
        

def try_change_password(request ,bcrypt , red_resp , next_red_resp , mail):
    
    
    """
    
    --> Return True (on success) or None (On Fail) ...
    
    ::Function used to change the user password in the database..
    ::It also changes the secret password so that we can logout the user from other devices..
    
        It takes the request and the get password from form and then using url get reequest and proceed further accordinng to it..
            
            :Returns None with flash if any eror occurs...
            :Or if changed successfully then returns True...

    
    """
    
    delete_saved_user_info(request , red_resp , next_red_resp)
    
    token = request.args.get("token")
    id = request.args.get("id")
    
    if (not token) or (not id):
        fe.some_went_wrong()
        return
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        db.query(f"""SELECT `user_email` , `user_name` FROM `forget_pass` WHERE token = '{token}' AND `slug` = '{id}' """)
        user_request = db.store_result().fetch_row(maxrows = 0)
        
        if user_request:
            
            user_request = user_request[-1]            
            user_email , user_name = user_request[0].decode() , user_request[1].decode()   
                      
            password = get_request_values("password")[-1]
            
            ch_user_pswd = change_user_password(user_email , password , bcrypt)
            
            if ch_user_pswd:
                
                
                """Delete the request entry (if exist)..."""
                
                try:
                    db.query(f""" DELETE  FROM `forget_pass` WHERE `forget_pass`.`slug` = '{id}' """)
                except Exception:
                    pass               
                
                
                mt.send_pass_changed_mail(user_email , user_name , mail)
                fs.pass_ch_success()
                return True
            
            return             

        fe.req_time_out()
        return 
    

    except Exception:
        fe.server_contact_error()
        return
    
    
    
def change_user_password(user_email , password , bcrypt):
    
    """
    
    --> Return True (on success) or None (On Fail) ...
    
    Function used to change the user password in the database..
    
        It takes the password , checks its format and then comapre it with the old one stored in the database and then finally updates the password in the database...

            :Returns None with flash if any eror occurs...
            :Or if changed successfully then returns True...

    """
    
    if not validate_password(password):
        fe.pswd_format_nt_crct()
        return
    
    hash_password = get_hashed_password(password , bcrypt)
    
    
    """Matching the old and new passwords...."""
    
    old_pswd = get_user_account_password(user_email)
    if old_pswd:
        if bcrypt.check_password_hash(old_pswd, password):
            fe.same_pass_error()
            return            
    else:
        return
       
    """Updating Password And Secret Password..."""
    """Secret Password is changed so that we can logout the user form other devices.."""
     
     
    secret_pass = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(60))                              #60-char long secret_pass
        
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)    
        db.query(f"""UPDATE `users` SET (`password`, `secret_pass`) VALUES ('{hash_password}' , '{secret_pass}') WHERE `users`.`user_email` = '{user_email}';""")
        return True
        
    except Exception:
        fe.server_contact_error()
        return
    
    
    
"""


Forgot Password Functions -------------------------------------------------------------


"""


if __name__ == "__main__" :
    
    
    pass