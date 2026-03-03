from globalvars import * 
from MySQLdb import _mysql
import re
import string
import time
import helper_modules.flash_errors as fe
import helper_modules.flash_success as fs
import helper_modules.operations as operations
from numpy.random import randint
from random import choice
import helper_modules.mail_helper as mail_helper

# Flask_Functions ---

mail = Flask_Functions.mail
bcrypt = Flask_Functions.bcrypt

# Params ---

params = Configs.params

mysql_passwd = params["mysql_password"]
db_user = params["mysql_user"]




def get_user_account(user_email):
    
    """
    
    Function used to get user account with the help of email...
    
    Returns None (if no account exists) or a tuple containing (userid , user_name , secret_pass , password) or serverproblem ...
    
    """
    
    try:
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
        db.query(f"""SELECT `userid` , `user_name` , `secret_pass` , `password` FROM users WHERE user_email = '{user_email}' """)
        user_account = db.store_result().fetch_row(maxrows = 0)
        
        
        if user_account:
            user_account = user_account[-1]
            return user_account[0].decode() , user_account[1].decode() , user_account[2].decode() , user_account[3].decode()  
        return user_account

    except AssertionError:
        fe.server_contact_error()
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
    
    return bcrypt.generate_password_hash(password , 10).decode('utf-8')


def check_account_exist(**kwargs):
    
    """
    
    Function used to get user account existance with any crendtial ...
    
    Returns False (if no account) or True (if account) or serverproblem
    
    """
    
    user_account_exist = False
    
    try:
        
        for key , value in kwargs.items() :  
            
            if user_account_exist:
                break
                  
        
            db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
            
            db.query(f"""SELECT `user_name` FROM users WHERE {key} = '{value}' """)
            user_account = db.store_result().fetch_row(maxrows = 0)
            
            
            if user_account:
                user_account_exist = True
                
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
    
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
                
        db.query(f"""SELECT `user_email` FROM new_acc_req WHERE slug = '{slug}' """)
        user_req_email = db.store_result().fetch_row(maxrows = 0)
        
        if user_req_email :
            return user_req_email[-1][0].decode()
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

        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
                
        db.query(f"""SELECT `user_email` ,  `user_name`  , `password` , `otp` , `time` FROM new_acc_req WHERE slug = '{slug}' """)
        user_req = db.store_result().fetch_row(maxrows = 0)
        
        if user_req != ():
            user_req = user_req[-1]
            return user_req[0].decode() , user_req[1].decode(), user_req[2].decode() , user_req[3].decode() , user_req[4].decode()
        return 

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM
    


def del_signup_req(user_email):
    
    """
    
    Function is used to delete the signup request from the database...
    
    
    """    
    
    try:
        
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)                
        db.query(f"""DELETE FROM `new_acc_req` WHERE `new_acc_req`.`user_email` = '{user_email}'""")
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
        except AssertionError:
            pass
                
        db.query(f"""INSERT INTO `new_acc_req` (`user_name`, `user_email`, `password`, `slug` , `otp`) VALUES ('{user_name}', '{user_email}', "{password}", '{slug}' , '{otp}' );""")
        
        return slug       

    except AssertionError:
        fe.server_contact_error()
        return None





def check_signup_otp(slug):
    
    signup_req = get_signup_req(slug)
        
    if not signup_req:
        fe.sess_time_out()        
        return operations.OP_FAIL
    
    elif signup_req == operations.SERVERPROBLEM:
    
        return operations.SERVERPROBLEM
    
    
    user_email , user_name , password , db_otp , req_time = signup_req   
    
    if not user_email:
        del_signup_req(user_email)
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
        req_time = time.mktime(time.strptime(req_time , '%Y-%m-%d %H:%M:%S'))        
        if req_time + 300 <= time.time() :
            fe.sess_time_out()
            return operations.SESS_TIME_OUT
        
        new_acc = create_new_account(user_email , user_name , password)
                
        if not new_acc :            
            return operations.OP_FAIL
                
        elif new_acc == operations.SERVERPROBLEM :            
            return operations.SERVERPROBLEM

        return user_email
        
    else:
        fe.otp_not_crct()
        return  operations.OTP_ERROR
    
    

def create_new_account(user_email, user_name , password):
         
    try:
        
        db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
                 
        # Creating a unique userid:
        while True :

            userid = randint(11111111,99999999) # 8-digit id
            
            db.query(f"""SELECT `sno`  FROM `users` WHERE userid = '{userid}' """)
            user_account = db.store_result().fetch_row(maxrows = 0)
            
            if not user_account:
                break              
            
        
        # Creating a secret_password (for login) ....
        # 60-char long secret_pass   
        
        secret_pass = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(60))          
    
        
        
        # Final - Main Step -----
        db.query(f"""INSERT INTO `users` (`user_name`, `user_email`, `password`, `userid`, `secret_pass`, `data`) VALUES ('{user_name}', '{user_email}', "{password}",  "{userid}", "{secret_pass}", '');""")
        
        
        # Delete the request.....
        try:
            db.query(f"""DELETE FROM `new_acc_req` WHERE `new_acc_req`.`user_email` = '{user_email}'""")
        except AssertionError:
            pass
        
        # Sending confirmation email...
        mail_helper.send_account_create_success_email(user_email , user_name)
        
        fs.acc_create_success()
        return True

    except AssertionError:
        fe.server_contact_error()
        return operations.SERVERPROBLEM


