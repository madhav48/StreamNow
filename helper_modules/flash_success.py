from flask import flash


def acc_create_success():
    return flash(("good","Account created successfully! Kindly Log In to the account. "))

def pass_ch_success():
    return flash(("good","Password Changed successfully! Kindly Log In to the account. "))

def login_success():
    return flash(("good","You are successfully logged in."))

def logged_out_success():
    return flash(("good","You are successfully logged out."))