from telnetlib import PRAGMA_HEARTBEAT
from globalvars import GlobalVariables


class Problems(GlobalVariables):
    
    def __init__(self, *args): 
        super().__init__(*args)
        
    def __repr__(self):
        return self.value
    
    def __str__(self):
        return self.value


class Success(GlobalVariables):
    
    def __init__(self, *args): 
        super().__init__(*args)
        
    def __repr__(self):
        return self.value
    
    def __str__(self):
        return self.value


# Problems -----------

MAIL_PROBLEM = Problems("Mail Problem!")
SERVERPROBLEM = Problems("Problem In Contacting")         
OP_FAIL = Problems("Operation Failed!")
SESS_TIME_OUT = Problems("Session Timed Out!")
SOMEWENTWRONG  = Problems("Something Went Wrong")
PASSINCORRECT = Problems("Password is not correct!")
NOACCFOUND = Problems("No Account Found!")
OTP_ERROR = Problems("Otp not Correct!")
LOGGEDOUT = Problems("Logged out!")
WRONGSAVEDLOGDETAIL = Problems("Wrong Login Details Saved!")
WRONGLOGINDETAILS = Problems("Wrong Login Details!")


# Success ----------------------

OP_SUCCESS = Success("Operation Success!") 