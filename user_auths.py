from globalvars import *

import helper_modules.flash_errors as fe
import helper_modules.flash_warn as fw
import helper_modules.flash_success as fs
import helper_modules.operations as operations

import helper_modules.accounts_helper as  accounts_helper
from helper_modules.mail_helper import ast_email
import user_account as ua


load_user = accounts_helper.User.load_user

def login_not_required(response):

    """Function to make sure that authentication pages are accessible or not..."""
    
    def check_authentication(*args , **kwargs):
        
        if Storage.current_user.is_authenticated :
            return abort(404)    
        
        return response(*args , **kwargs)
    
    return check_authentication


def delete_saved_user_info(*resp , to_delete = ("saved-log-in-details"  , "saved-email")):
    
    """Funcion deletes the cookies which have any information for logging in user..""" 
    for response in resp :   
        delete_cookies(response , *to_delete)    
    return


@login_not_required
def _unauthorized():
    
    fw.flash_login_req()
    return redirect_response("login")


@login_not_required
def _signup():
     
    values = {"name":"",
            "email" : ""}
    
    if Storage.request.method == "POST":
        
        red_resp = redirect_response("signup")
        
        if not is_cookie_storable():
            return red_resp
        
        signup_request = accounts_helper.signup_user_request()
        
        if isinstance(signup_request[0] , operations.Success):
            
            slug = signup_request[2]
            
            signup_otp_verify_resp = redirect_response("signup_otp_verification" ,  slug = slug)
                      
            # Setting 15 second resend limit cookie And otp time limit cookie ----
            set_cookies(signup_otp_verify_resp , (f"resendWaitTime-{slug}", "15" , 15) , ("timeleft", "300", 300))

            # Deleting any login information cookie (if saved)...
            delete_saved_user_info(signup_otp_verify_resp)
            delete_session("log-in-details" , "user-signup-details")
                        
            return signup_otp_verify_resp        
        
        else:                
            values = {"name": signup_request[1],
                    "email" : signup_request[2]}
            Storage.session["user-signup-details"] = values     
            
            delete_saved_user_info(red_resp)
            return red_resp  
        
  
    if ("user-signup-details" in Storage.session) and is_cookie_storable() :
        values = Storage.session["user-signup-details"]
        delete_session("user-signup-details")
        
    return render_template("signup.html" , values = values)



@login_not_required
def _signup_otp_verification(slug):

    prev_red_resp = redirect_response("signup")
    same_red_resp = redirect_response("signup_otp_verification" ,  slug = slug)
    next_red_resp = redirect_response("login")
    
    """Deleting if any saved info exists ---"""        
    delete_saved_user_info(prev_red_resp, same_red_resp , next_red_resp)               
    
    
    if not is_cookie_storable():
        return prev_red_resp
        
    if Storage.request.method == "POST":
        
        
        user_email = accounts_helper.check_signup_otp(slug)
        
        if isinstance(user_email , operations.Problems) :
            
            if user_email in (operations.OTP_ERROR , operations.SERVERPROBLEM):
                return same_red_resp
            
            else:
                return prev_red_resp
            
        else:
            
            delete_session("log-in-details")

            set_cookies(next_red_resp,("saved-email" , user_email , 15*24*60*60 ))
            return next_red_resp
            
                
    req_email = accounts_helper.signup_req_email(slug)

    if (not req_email) or (isinstance(req_email , operations.Problems)):
        return prev_red_resp
       
    return render_response("signup-otp-verification.html" , email = ast_email(req_email) , slug = slug)
    


@login_not_required
def _resend_signup_otp_verification(slug):
       
    if not is_cookie_storable():
        return operations.OP_FAIL
    
    if f"resendWaitTime-{slug}"  in Storage.request.cookies:
        timeleft = int(Storage.request.cookies.get(f"resendWaitTime-{slug}"))
        if timeleft > 1 :
          return operations.OP_FAIL  
      
    otp_sent = accounts_helper.resend_signup_otp(slug)
    
    return otp_sent


@login_not_required
def _login(login_user):
    
    
    if Storage.request.method == "POST":
        
        red_resp = redirect_response("login")        
        next_url_resp = redirect_to_next("index")
        
        if not next_url_resp:
            return abort(400)
                
        if not is_cookie_storable():
            return red_resp
               
        
        user_object = accounts_helper.login_user_object()
        
        
        if user_object[0] != operations.SERVERPROBLEM:
            delete_saved_user_info(next_url_resp , red_resp)
        
        
        if isinstance(user_object[0] ,  operations.Problems) :   
            Storage.session["log-in-details"] = {
                        "email" : user_object[1],
                        "remember_check" : user_object[2]
                            }    
                
            return red_resp
        
        else:
            
            login_user(user_object[1] , remember = bool(user_object[2]))
            return next_url_resp

        
    values = {
        "email" : "",
        "remember_check" : "checked"
    }
    
    saved_user_dict = {"user_saved" : None, "saved_user_name" : None , "saved_user_id" : None , "saved_user_email" : None} 
          
    user_details_saved = accounts_helper.get_saved_user()
              
    if is_cookie_storable():
        
        if ("log-in-details" in Storage.session):
            values = Storage.session["log-in-details"]
            delete_session("log-in-details")
      

        # If user saved login details ----   
        elif user_details_saved :
    
            if user_details_saved :
                saved_user_dict = {"user_saved" : user_details_saved[0], "saved_user_name" : user_details_saved[1] , "saved_user_id" : user_details_saved[2] , "saved_user_email" : user_details_saved[3]} 
            

        elif ("saved-email" in Storage.request.cookies):
            values = {
                "email" : Storage.request.cookies.get("saved-email"),
                "remember_check" : "checked"            
            }
        
    login_resp = render_response("login.html" , values = values , **saved_user_dict)
        
    if not saved_user_dict.get("user_saved"): 
        delete_cookies(login_resp ,"saved-log-in-details")
    
    
    return login_resp

                     
def _logout(logout_user):
       
    if not is_cookie_storable():
        return redirect_response("login")
                   
    next_url_resp = redirect_to_next("login")
    if not next_url_resp:
        abort(400)
        
    # Ask user to save login info ----
    curr_email = Storage.current_user.email
    curr_userid = Storage.current_user.id
    
    save_login_detials = Storage.request.args.get("save-login-details")
    
    # If user wants to save login details ---
    if save_login_detials == curr_userid:
        
        details = curr_userid + "&" + Storage.current_user.secret_pass
        next_url_resp.set_cookie("saved-log-in-details", details , max_age= 15*24*60*60)
        
    else :    
        next_url_resp.set_cookie("saved-email", curr_email , max_age= 15*24*60*60)
    
    logout_user()
    fs.logged_out_success()
    
    return next_url_resp


@login_not_required
def _forgot_password():
    
    if Storage.request.method == "POST":
        return ua.send_change_password_link(request, mail)
   
    
    temp_resp = make_response(render_template("forgot-password.html"))
    ua.delete_saved_user_info(temp_resp)
    return temp_resp
 

