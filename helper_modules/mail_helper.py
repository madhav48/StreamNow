"""


Module for creating mail templates ----
And sending emails....
And other helper functions ---

"""


import helper_modules.flash_errors as fe
from globalvars import Configs , Flask_Functions


params = Configs.params
mail =  Flask_Functions.mail

domain_name = params["domain_name"]
secure_link = domain_name + "/user-accounts/secure-account"





"""Helpers -----------------------------------"""


def ast(length):
    
    s  = ""
    for i in range(length):
        s = s + "*"
    return s


def ast_email(email):
    
    """
    Function used to generate asterisked email....
    
        --> Example --
        
            member@company.org - m****r@c*****y.org
    
    """
    
    email_parts = email.split("@")
    domain_details = email_parts[1].split(".")
    return_email= email_parts[0][0] + ast(len(email_parts[0][1:-1])) + email_parts[0][-1] + "@" + domain_details[0][0] + ast(len(domain_details[0][1:-1])) + domain_details[0][-1] + "." + domain_details[1]

    return return_email



"""Helpers -----------------------------------"""






"""Templates --------------------------------------------"""


def otp_verifcation(user_name ,  otp):
    return (f"Otp Verification for {user_name}!" , f"Hey {user_name}! Your Email Verification One Time Password is {otp}<br>The otp is valid for only 5 minutes.Don't share this with anyone.<br>Thanks, StreamNow - Your Music Buddy")



def change_pass_mail(user_name , token , id):
    
    reset_link = domain_name + f"/forgot-password/change-password?token={token}&id={id}"
    
    return (f"Password Change for {user_name}!" , f"Hey {user_name}!<br>To reset your account password click at the link given below.<br><a href = {reset_link}>Reset Password</a><br>(The link is valid for only 5 minutes)<br>Thanks, StreamNow - Your Music Buddy")



def acc_created(user_name):
    
    return ("Registration Successfull!" ,  f"Congratulations {user_name}!!!\nYou are successfully registered with StreamNow - Your Music Buddy.\nEnjoy the feel of music!")



def new_login(user_name):
        
    return ("New Login Detected!" ,  f"Hey {user_name}! We have seen a new login into your account! If it was not you then please secure your account now by clicking the below link.<br><a href = {secure_link}>Secure Your Account</a><br>Thanks, StreamNow - Your Music Buddy")


def pass_changed(user_name):
    
    return ("Password changed!" ,  f"Hey {user_name}! Your account password has been changed! If it was not you then please secure your account now by clicking the below link.<br><a href = {secure_link}>Secure Your Account</a><br>Thanks, StreamNow - Your Music Buddy")

"""Templates ----------------------------------------------------"""





"""

Mail Functions ---------------------------------------------------------------


"""


def send_mail(recipients , subject , html , flash = False):
    
    """
    
    --> Returns True/False
        ... True on successfull send of email
        ... False on unsuccess ..
    
    
        Function is used to send email to the user..
    
    :Main function...
    
        Other mail functions are built using lambda and this helper function..
    
    """ 
    
    
    try:
        mail.send_message(subject = subject,
        recipients= recipients,
        sender= params["verify-email-id"],
        html = html
        )
        return True

    except AssertionError:
        
        if flash:
            fe.mail_send_prblm()
        return False
    

# To send signup otp----
send_verify_mail = lambda email , otp , user_name , flash = True : send_mail([email] , *otp_verifcation(user_name , otp) , flash)


#  To send password change link...
send_change_pass_mail = lambda email ,  user_name, token , id , flash = True : send_mail([email] , *change_pass_mail(user_name , token , id) , flash)
   
    
# To send account creation success mail...
send_account_create_success_email = lambda email , user_name: send_mail([email] , *acc_created(user_name))     


# To send new device logged in information --- 
send_new_login_detect = lambda email , user_name: send_mail([email] , *new_login(user_name))     


# To send password changed mail ---
send_pass_changed_mail = lambda email , user_name: send_mail([email] , *pass_changed(user_name))




"""

Mail Functions ---------------------------------------------------------------


"""



