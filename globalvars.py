"""
    
    Module to declare all global variables , functions etc...
    
"""


class Storage:
    
    request = None
    session = None
    current_user = None


class Flask_Functions:
    
    mail = None 
    bcrypt = None


class Configs: 
       
    params = {} 


class Database:
      
    sqlalchemy_sn_users_db = None
    mysql_sn_users_db = None


class GlobalVariables:
    
    def __init__(self , *args):
                
        if args:
            self.value = args[0]
        else:
            self.value = None

    def update(self , *args):
        
        if args:
            self.value = args[0]           
        return
    

class GlobalFunctions:
    
    def __init__(self , *args):
 
        if args:
            self.call = args[0]        
        else:
            self.call =  self.default_call
            
    
    def __call__(self , *args , **kwargs):
        return self.call(*args , **kwargs)
  
              
    def default_call(self):
        return None
        
    def update(self , *args):
        
        if args:
            self.call = args[0]           
        return   

# Login Functions ----

login_required = GlobalFunctions()


# Response Functions ----

make_response = GlobalFunctions()
url_for = GlobalFunctions()
redirect = GlobalFunctions()
render_template = GlobalFunctions()
abort = GlobalFunctions()


# Url functions -----

is_safe_url = GlobalFunctions()
quoted_url = GlobalFunctions()
unquoted_url = GlobalFunctions()
redirect_response = GlobalFunctions()
render_response = GlobalFunctions()
redirect_to_next = GlobalFunctions()


# Cookies Funcions ---

is_cookie_storable = GlobalFunctions()
delete_cookies = GlobalFunctions()
set_cookies = GlobalFunctions()
delete_session = GlobalFunctions()

