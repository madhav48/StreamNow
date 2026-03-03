"""

Helper Module to handle cookies...

: Create Cookies - set_cookies() 
: Delete Cookies - delete_cookies()
: Modify cookies etc...



"""


"""Cookies handlerr .........."""


from globalvars import Storage


def is_cookie_storable():
    if "acceptCookies" not in Storage.request.cookies:
        return 
    return True 


def delete_cookies(resp , *cookienames):

    """
    
    Function used to delete cookies.
    : Storage.request --> flask.Storage.request 
        .. Use - Used to check that if the cookiename exists in the browser or not.. So that if it exists then we will be able to delte it..
    : resp - The response of the page to which then user is being redirected..
    : *cookienames -- contains the cookie names which have to be deleted..
    
    
    ... Function iterates the cookie names using for loop and then check them in Storage.request if they exist or not and then set the cookies with same name and value `` and expiry 0... 
        Through which the cookie gets deleted as because of that expiry it means that the cookie should be deleted in  the past so the browser deletes it at that time.. And thats how cookies are deleted.. 
    
    """
    
    if not is_cookie_storable():
        return
    
    for cookiename in cookienames:
        if cookiename in Storage.request.cookies :
            resp.set_cookie(cookiename, "" ,  expires=0) 
    return


def set_cookies(resp , *cookies):

    """
    
    Function used to set cookies.
    : resp - The response of the page to which then user is being redirected..
    : *cookies -- tuples containing cookiename at 0th index and cookievalue at 1st and age at 2nd index respectively..
        .. An example of above parameter..
            ("cookienamexyz" , "cookievalueabc" , max_age = q*24*60*60)
    
    
    ... Function iterates the tuples using for loop and set the cookies one by one using `set_cookies` function...

    """
    
    if not is_cookie_storable():
        return

    for cookiename , cookievalue ,  cookie_age in cookies:
        resp.set_cookie(cookiename, cookievalue ,  max_age = cookie_age) 

    return


"""Cookies handlerr .........."""



# ------------------------------------------------------------------------------------------------------------------


"""Sessions handlerr .........."""

def delete_session(*items):
    
    for item in items :
        if item in Storage.session:
            Storage.session.pop(item , None)