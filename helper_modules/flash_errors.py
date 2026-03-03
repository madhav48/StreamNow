from flask import flash

def already_acc_exists(): 
    return flash(("error","Account already exists! Kindly login or use another email."))

def server_contact_error():
    return flash(("error","There is some problem in contacting to the server! Try again after some time."))

def pswd_format_nt_crct():
    return flash(("error","Password is not of correct foramt!."))
    
def otp_mail_prblm():
    return flash(("error","There was some problem in sending the otp to your Email!"))
    
def mail_send_prblm():
    return flash(("error","There was some problem in sending the Email! Try again after some time."))
    
def otp_not_crct():
    return flash(("error","Otp is not correct!"))

def sess_time_out():
    return flash(("error","Session Timed Out!"))

def req_time_out():
    return flash(("error","Request Timed Out!"))

def no_acc_found():
    return flash(("error","No account found!"))

def incorrect_password():
    return flash(("error","Password is incorrect! Please try again."))

def same_pass_error():
    return flash(("error","This is your existing password! Please enter a new one!"))

def some_went_wrong():
    return flash(("error","Something went wrong! Please try again after few moments."))