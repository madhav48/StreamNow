# # # import hashlib
# # # string="pythonpool.ffffffbiuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuusfnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnfffffffcom"
# # # encoded=string.encode()
# # # result = hashlib.sha256(encoded).hexdigest()
# # # print(result)
# # # print(encoded)

# # # string2 = string
# # # encoded = string2.encode()
# # # result2 = hashlib.sha256(encoded).hexdigest()
# # # print(result2)
# # # # print(result == result2)


# # # import time

# # # print(time.mktime(time.strptime("2022:03:19 22:49:19" , '%Y:%m:%d %H:%M:%S')))
# # # print(time.time())

# # # print("a" or "h")

# # # var = "%252Fexp%2520-%2520page%2520%252F%2520hujnjn"
# # # from urllib.parse import quote_plus , unquote , quote
# # # print(quote(unquote(var) ,safe = ""))
# # # print(unquote('/El%20Ni%C3%B1o/') )
# # # print(unquote(var))
# # # print(unquote(unquote(var)))
# # # from requests.utils import quote


# # # print(quote(var , safe = ""))

# # # from flask import Flask , url_for

# # # app = Flask(__name__)


# # # @app.route("/")
# # # def index():
# # #     return url_for("index" , net = "uu ytgvv")
# # print(bool(""))






            
# #     try:
    
# #         db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
# #         db.query(f"""SELECT `user_email` , `user_name` FROM users WHERE userid = '{userid}' AND secret_pass = '{secret_pass}' """)
# #         user_account = db.store_result().fetch_row(maxrows = 0)
        
# #         if not user_account:
# #             fe.no_acc_found()
# #             return
        
# #         user_account = user_account[0]
# #         user_email , user_name =  user_account[0].decode() , user_account[1].decode()
        
# #         user = User(user_name , user_email , userid , secret_pass)
# #         fs.login_success()  
# #         return user

# #     except Exception:
# #         fe.server_contact_error()
# #         return SERVERPROBLEM












# # class a ():
# #     def __init__(self):
# #         self = None
    
    
# # b = a()
# # print(b)











# # # app.run()
















































# def send_forgot_password_otp(request , params , mail , session):
    
#     email = request.args.get("email")
    
#     if not email :
#         return SOMEWENTWRONG    
    
#     user_account = get_user_account(email)
    
#     if user_account:
    
#         if user_account == SERVERPROBLEM:
#             print(1)
#             return SERVERPROBLEM
                     
#         slug = generate_and_send_forgot_pass_otp(email , params , mail)
#         print(2,slug)
        
#         if slug not in (SERVERPROBLEM , MAIL_PROBLEM):    
#             """Excecutes when otp is generated , sent and stored successfully..."""
                    
#             session["forgot-pass-otp-email"] = email
#             return slug
#         return slug
    
#     return NOACCFOUND
    
    
# def generate_and_send_forgot_pass_otp(email , params , mail):
    
#     otp = randint(111111,999999)            
#     otp_mail = send_forgot_otp_mail(email , params , otp , mail)
    
#     if not otp_mail:
#         return MAIL_PROBLEM
    
    
#     try:

#         db = _mysql.connect(db = "sn_users" , user = db_user , passwd = mysql_passwd)
        
#         try:
#             # Delete the old request (if any).....
#             db.query(f"""DELETE FROM `forget_pass` WHERE `forget_pass`.`user_email` = '{email}'""")
#         except Exception: 
#             pass
        
#         # Creating a unique slug:
#         while True :

#             slug = ''.join(choice(string.ascii_lowercase  + string.digits + string.ascii_uppercase) for x in range(60))
            
#             db.query(f"""SELECT `user_email`  FROM `forget_pass` WHERE slug = '{slug}' """)   # 60-Char long..
#             user_request = db.store_result().fetch_row(maxrows = 0)
            
#             if not user_request:
#                 break
        
        
#         # Final - Main Step -----
#         db.query(f"""INSERT INTO `forget_pass` (`user_email`, `slug`, `otp`) VALUES ('{email}', '{slug}', "{otp}");""")
        
#         return slug 
    
#     except AssertionError:
#         return SERVERPROBLEM
        
        



def a (*args):
    print("gii")
    
a()