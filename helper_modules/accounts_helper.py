from globalvars import * 

import re
import string
import time
from numpy.random import randint
from random import choice


import helper_modules.flash_errors as fe
import helper_modules.flash_success as fs
import helper_modules.flash_warn as fw
import helper_modules.operations as operations
import helper_modules.mail_helper as mail_helper


# Flask_Functions ---
bcrypt = Flask_Functions.bcrypt



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
                   
            
        
        elif ("user_email" in auth_details) and ("password" in auth_details):
            
            """
            --> Login user with the help of `user_email` and `password` ...
            """
            
            self.make_from_emailnpass(auth_details["user_email"] , auth_details["password"] , flash_error)
    
    
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
                
        user_account = get_account_by_userid(user_id)
        
        if not user_account:
            if flash_error :
                fe.no_acc_found()
            return
        
        if user_account == operations.SERVERPROBLEM:
            if flash_error :
                fe.server_contact_error()
            self.error = operations.SERVERPROBLEM
            return
            
        
        user_name , user_email , db_secret_pass = user_account
        
        if secret_pass != db_secret_pass:
            if flash_error :
                fe.no_acc_found()
            self.error = operations.LOGGEDOUT
            return
        
        self.set_user_details(user_name, user_email, user_id , secret_pass)
        return self      
    
        
    def make_from_emailnpass(self , user_email ,  form_password , flash_error = True):
    
        user_account = get_user_account(user_email)
        
        if not user_account:
            if flash_error:
                fe.no_acc_found()
            return
        
        if user_account == operations.SERVERPROBLEM:
            if flash_error :
                fe.server_contact_error()
            self.error = operations.SERVERPROBLEM
            return

        
        user_id , user_name , secret_pass , db_password = user_account
        
        print(db_password)
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
                if user.error == operations.LOGGEDOUT:
                    fw.logged_out()
                return
            return user
            
        except Exception:
            return
        
        
    @staticmethod
    def create_user_object(*args , **kwargs):
        
        """
        Function returns the User class object according to the given parameters...
        
        """
        
        return User(*args , **kwargs)
        
                    



def get_user_account(user_email):
    
    """
    
    Function used to get user account with the help of email...
    
    Returns None (if no account exists) or a tuple containing (userid , user_name , secret_pass , password) or serverproblem ...
    
    """
    
    try:
    
        db = Database.mysql_sn_users_db
        cursor = db.cursor()
        
        cursor.execute(f"""SELECT `userid` , `user_name` , `secret_pass` , `password` FROM users WHERE user_email = '{user_email}' """)

        user_account = cursor.fetchone()
        cursor.close()
        return user_account

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM
    

def get_account_by_userid(userid):
    
    
    """
    
    Function used to get user account with the help of email...
    
    Returns None (if no account exists) or a tuple containing (user_name , user_email , secret_pass) or serverproblem ...
    
    """
    
    
    try:
    
        db = Database.mysql_sn_users_db
        cursor = db.cursor()
        
        cursor.execute(f"""SELECT `user_name`, `user_email` , `secret_pass` FROM users WHERE userid = '{userid}' """)
  
        user_account = cursor.fetchone()
        cursor.close()
        
        return user_account

    except Exception:
        return operations.SERVERPROBLEM



def get_request_values(*args):
    
    """Function returns all the values stored in the html form ..."""
    
    return_values = []

    for item in args :
        return_values.append(Storage.request.form.get(item))
    return return_values



def validate_password(password):
    
    """Function validates the password by checking its format and returns bool value..."""
    
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


def get_hashed_password(password):
    
    """Function returns the hashed password to store in the databse..."""    
    return bcrypt.generate_password_hash(password.encode("utf-8") , 10)


def check_account_exist(**kwargs):
    
    """
    
    Function used to get user account existance with any crendtial ...
    
    Returns False (if no account) or True (if account) or serverproblem
    
    """
    
    user_account_exist = False
    
    try:
     
        db = Database.mysql_sn_users_db
        cursor = db.cursor() 
        
        for key , value in kwargs.items() :  
            
            if user_account_exist:
                break
                  
            cursor.execute(f"""SELECT `user_name` FROM users WHERE {key} = '{value}' """)
            user_account = cursor.fetchone()
            
            if user_account:
                user_account_exist = True
        
        cursor.close()        
        return user_account_exist
            

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM


def signup_req_email(slug):
    
    """  
    Function used to get user signup request email ...
    
    Returns None (if no Request) or email (if Request) or serverproblem
    
    """

    
    try:
        
        
        db = Database.mysql_sn_users_db
        cursor = db.cursor() 
                        
        cursor.execute(f"""SELECT `user_email` FROM new_acc_req WHERE slug = '{slug}' """)
        user_req_email = cursor.fetchone()
        
        cursor.close()
        
        if user_req_email :
            return user_req_email[0]
        return False

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM


def get_signup_req(slug):
        
    """
    
    Function is used to get the signup request from the database...
    
    --> Format - (user_email , user_name , password , otp)
    
    """    
    
    try:

        db = Database.mysql_sn_users_db
        cursor = db.cursor() 
                     
        cursor.execute(f"""SELECT `user_email` ,  `user_name`  , `password` , `otp` , `time` FROM new_acc_req WHERE slug = '{slug}' """)
        
        user_req = cursor.fetchone()
        cursor.close()
        
        return user_req

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM
    


def del_signup_req(db= None , cursor = None , **kwargs):
    
    """
    
    Function is used to delete the signup request from the database...
    
    
    """    
    
    def delete_entry(cursor , db , key , value):
        cursor.execute(f"""DELETE FROM `new_acc_req` WHERE `new_acc_req`.`{key}` = '{value}'""")
        db.commit()
    
    try:
        
        if not cursor:
            db = Database.mysql_sn_users_db
            cursor = db.cursor() 
            
            for key , value in kwargs.items():
                delete_entry(cursor , db , key , value)
                cursor.close()
            return
        
        else:       
            for key , value in kwargs.items():    
                delete_entry(cursor , db , key , value) 
            return 

    except AssertionError:
        return 
    


def signup_user_request():
    
    """
    
    --> Returns a tuple with operation variable (success or fail) at 0th index and email and username on 1st and 2nd index respectively (if failed) or email and slug on 1st and 2nd index respectively (if success)...
    
    
    Helper function which is used to add the user signup request to the datbase...
    
        :It get all the values from the form and the check the email if any account exists or not and then validate password and after that finally generates slug and otp and returns...
    
    """
    
    name, email  , password = get_request_values('name'  , 'email' , 'password')
        
    if None in (name , email , password):
        fe.some_went_wrong()
        return (operations.SOMEWENTWRONG , "" , "")

    
    account = check_account_exist(user_email = email)
    
    if account :
        if account != operations.SERVERPROBLEM:
            fe.already_acc_exists()
        return (operations.OP_FAIL , name , email)
    
    
    if not validate_password :
        fe.pswd_format_nt_crct()
        return (operations.OP_FAIL , name , email)
    
    hashed_password = get_hashed_password(password)    
        
    slug = generate_slug(name , email , hashed_password)       
    
    if not slug:
        return (operations.OP_FAIL , name , email)
    
    return (operations.OP_SUCCESS , email , slug)       



def generate_slug(user_name , user_email , password):
    
    """
    --> Returns True (on success) or None (on Fail)....
    
    Function generates otp and slug and then send the otp to the user email and then if sent successfully then store all the user details including otp and a slug into the database... 
    
    """
    
    
    
    otp = randint(111111,999999)
       
    verify_mail = mail_helper.send_verify_mail(user_email, otp , user_name)

    if not verify_mail:
        return None
    
    try:

        db = Database.mysql_sn_users_db
        cursor = db.cursor() 
        
        # Generating slug ----
        while True:
            
            slug = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(15))
            
            cursor.execute(f"""SELECT `sno`  FROM `new_acc_req` WHERE slug = '{slug}' """)
            user_req = cursor.fetchone()
            
            if not user_req:
                break
            
        # Deleting the old entry if exists...
        del_signup_req(db = db , cursor = cursor , user_email = user_email)
                
        cursor.execute(f"""INSERT INTO `new_acc_req` (`user_name`, `user_email`, `password`, `slug` , `otp`) VALUES ('{user_name}', '{user_email}', "{password.decode()}", '{slug}' , '{otp}' );""")
        db.commit()
        
        cursor.close()
        return slug       

    except AssertionError:
        fe.server_contact_error()
        return None





def check_signup_otp(slug):
    
    
    """
    
    --> Function returns user_email or opeartions.Problem instance....

        : user_email - If user account is created successfully...
        : serverproblem - For db problem
        : sess_time_out - No request found
        : otp_erorr _ For incorrect otp
        : op_fail - Any other error...
        
    
    : Function gets the user signup request through the slug prrovided
    :: And then check for the account existance by that email 
    ::: And if not found then gets otp from the form and then match the form otp and otp stored in the database 
    :::: And if the otps are matched then check for the 5 min time limit
    ::::: And then creates the account by storing all the informations in the databse
    :::::: And finally it send the user the confimation mail and flashes it...
    
    
    """
    
    signup_req = get_signup_req(slug)
        
    if not signup_req:
        fe.sess_time_out()        
        return operations.OP_FAIL
    
    elif signup_req == operations.SERVERPROBLEM: 
        return operations.SERVERPROBLEM
    
    
    user_email , user_name , password , db_otp , req_time = signup_req   
    
    if not user_email:
        del_signup_req(slug = slug)
        fe.sess_time_out()        
        return operations.OP_FAIL
    
    account = check_account_exist(user_email = user_email)
    
    if account:
        
        if account != operations.SERVERPROBLEM:
            fe.already_acc_exists()
            return operations.SERVERPROBLEM
        
        return operations.OP_FAIL
    
    form_otp = get_request_values(Storage.request , 'otp')[-1]
    
    if form_otp == str(db_otp) :
        
        # Checking the 5-min time limit :           
        req_time = time.mktime(req_time.timetuple())        
        if req_time + 300 <= time.time() :
            fe.sess_time_out()
            return operations.SESS_TIME_OUT
     
        
        new_acc = create_new_account(user_email , user_name , password)
                
        if not new_acc :            
            return operations.OP_FAIL
                
        elif new_acc == operations.SERVERPROBLEM :            
            return operations.SERVERPROBLEM
        
        
        # Sending confirmation email...
        mail_helper.send_account_create_success_email(user_email , user_name)
        
        fs.acc_create_success()
        return user_email
        
    else:
        fe.otp_not_crct()
        return  operations.OTP_ERROR
    
    

def create_new_account(user_email, user_name , password):
         
    """
    --> Returns True or Server Error...
    
    Function used to create an user account ...
    
        : At first, creates a uniques user id...
        : Second secret pass
        : And at last stores them all in the databse of users...
        : And then delete the signup request from database and returns True at last...
    
    """
    
    
    
    try:
        
      
        db = Database.mysql_sn_users_db
        cursor = db.cursor() 
        
        # Creating a unique userid:
        while True :

            userid = randint(11111111,99999999) # 8-digit id
            
            cursor.execute(f"""SELECT `sno`  FROM `users` WHERE userid = '{userid}' """)
            user_account = cursor.fetchone()
            
            if not user_account:
                break              
            
        
        # Creating a secret_password (for login) ....
        # 60-char long secret_pass   
        
        secret_pass = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(60))          
    
        
        
        # Final - Main Step -----
        cursor.execute(f"""INSERT INTO `users` (`user_name`, `user_email`, `password`, `userid`, `secret_pass`, `data`) VALUES ('{user_name}', '{user_email}', "{password.decode()}",  "{userid}", "{secret_pass}", '');""")
        
        db.commit()        
        
        # Delete the request.....
        del_signup_req(db = db , cursor = cursor , user_email = user_email)
        cursor.close()
        
        return True

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM



def resend_signup_otp(slug):
    
    signup_req = get_signup_req(slug)
        
    if not signup_req:
        return operations.OP_FAIL
    
    elif signup_req == operations.SERVERPROBLEM: 
        return operations.SERVERPROBLEM

    
    user_email , user_name , password , db_otp , req_time = signup_req   
        
    if not user_email:
        del_signup_req(slug = slug)
        return operations.OP_FAIL

    resend_mail = mail_helper.send_verify_mail(user_email , db_otp , user_name ,  flash = False)
    
    if not resend_mail:
        return operations.OP_FAIL
    
    return operations.OP_SUCCESS    



def get_saved_user():
 
    """
    
    --> returns tuple of (True , `user_name` , `user_email`) [Details of the saved user..] 
        ... The True is used to tell jinja templating to show an extra option of looging into the saved account.
    
    Used to get the saved user account to show on the login page if saved during logout so we can relogin them...
        --> Details are verified through `User` class...
            And approprivate values are returned..
    
    """       
    if "saved-log-in-details" in Storage.request.cookies :
        saved_log_in_details = Storage.request.cookies.get("saved-log-in-details")
        
        try:
            
            userid , secret_pass = saved_log_in_details.split("&")
            user = User.create_user_object(user_id = userid , secret_pass = secret_pass)
            
            if not user.is_anonymous: 
                return True , user.name , user.id , user.email

            else:
                return
        
        except AssertionError:
            return
        
    return
            
                             
                


def saved_user_obj(saved_userid):
 
    """
    --> returns None / SOMEWENTWRONG / SERVERPROBLEM if any eroor occurs or `User` class object if successfully made..     
    
    Function helps to log in the user which is saved in the cookies.. when user allowed us to save while logout..
    
        Takes saved user id  as argument..
            Get all the details from cookies and the try getting user id and secret password by splitting and then matching the user id prsent in log in forms and cookies and the try to make user object using `User` class..
            
            If any eroor occrrs while creating user then function returns None (Problem in saved cookies or secret_pass not matching..) / SOMEWENTWRONG (user ids are different in forms and cookies..) / SERVERPROBLEM (Server Issue)
    
        Example - saved_user_object(123)
        
    """    
          
    if "saved-log-in-details" in Storage.request.cookies :
        saved_log_in_details = Storage.request.cookies.get("saved-log-in-details")
    
        try:
            
            userid , secret_pass = saved_log_in_details.split("&")
            
            if userid == saved_userid:
                user = User(flash_error=True  , user_id = userid , secret_pass = secret_pass)
                    
                if not user.get_id():
                    if user.error != operations.SERVERPROBLEM:
                    
                        """Exceute when the user object can't be made because of wrong user id or secret password""" 
                        return (operations.WRONGSAVEDLOGDETAIL , "" , None)
                
                    return (operations.SERVERPROBLEM , "" , None)
                
                else:
                    
                    """Execute when the user object is successfully made..."""
                    fs.login_success()    
                    return (operations.OP_SUCCESS , user , True)
        
            fe.some_went_wrong()
            return (operations.WRONGSAVEDLOGDETAIL , "" , None)     
        
        except AssertionError:
                (operations.SOMEWENTWRONG , "" , None)               
            

def user_obj_by_email_and_pass(user_email , password , remember):
      
    
    """
    
    --> returns None if user object is not made (due to incorrect authentication details) or `User` class object if object is made...
    
    Function helps to log on user with the help of the email and password provided..
    
    """

    user = User(flash_error= True , user_email= user_email , password = password)
    
    if not user.get_id():
        if user.error != operations.SERVERPROBLEM:
            
            """Exceute when the user object can't be made because of wrong email or incorrect password""" 
            return (operations.WRONGLOGINDETAILS , user_email , remember)
        
        return (operations.SERVERPROBLEM , user_email , remember)
        
    else:
        
        """Execute when the user object is successfully made..."""
        
        fs.login_success()    
        mail_helper.send_new_login_detect(user.email , user.name)
        return (operations.OP_SUCCESS, user , remember)



def login_user_object():
    
    
    """
    
    --> return None if user is not logged in due to any reason or User class instacnce if user logged in... 
    
    Function helps to login the user by checking various parameters.. and then flashes messages according to the errors occured.. 
    
    
    # Checks for the values step by step  and if the values are found then try to login the user with the help of those values..
    
    Values Finding prefferenece..
    
        1. saved_userid --> Helps to login the saved user (User svaed while logout)....
        2. Email And Password - Normal login using email and password...    
       
        
    """
       
    
    """
        If user saved login details --->
    """
    
    saved_userid = get_request_values("saved-userid")[-1]
    
    if saved_userid:
        return saved_user_obj(saved_userid)
        
    
    """
    
    Logging user with the help of user email and password...
    
    """
    
    user_email , form_password , remember = get_request_values("email" , "password" , "remember")
        
    if None not in (user_email , form_password):
        return user_obj_by_email_and_pass(user_email , form_password , remember)
    
    return (operations.SOMEWENTWRONG , "" , None)




def send_change_password_link():
    
    """
    
    --> Returns `Success...` if the link is sent successfully to the email else return the problem occured like --->
        ..SERVERPROBLEM
        ..MAIL_PROBLEM
        ..SOMEWENTWRONG
        
        
    Function to generate an password changing link and sending it to the user email so that the user can change the password of the account by accessing it from the registered email...
    
        At first generates the token and id and stores it in the database with email after confirming the valid email thorgh the function   `get_user_name` and `generate_pass_link`..
        
        After this the function tries to send the mail and then returns the values as mentioned above...

    """
        
    email = Storage.request.args.get("email")
    
    if not email :
        return operations.SOMEWENTWRONG    
    
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
    





if __name__ == '__main__':
    print(get_user_account("agrawalmadhav13@gmail.com"))
    pass
    
    