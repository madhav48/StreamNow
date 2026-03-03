from flask import flash

def flash_login_req():
    return flash (("warn","Please log in to access this page."))

def enable_cookie():
    return flash (("warn","Please enable the cookies!"))


def logged_out():
    return flash (("warn","You are logged out of the account! Please relogin!"))