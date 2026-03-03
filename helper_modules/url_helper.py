"""

    Module to handle urls...

"""

from urllib.parse import unquote, urlparse, urljoin , quote_plus
from globalvars import make_response , render_template , url_for , redirect , Storage


""" Functions --------------------- """


def is_safe_url(target):
    ref_url = urlparse(Storage.request.host_url)
    test_url = urlparse(urljoin(Storage.request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def quoted_url(string):
    return quote_plus(unquote(string))    # Function replaces escape sequence with %xx ...


def unquoted_url(string):
    try:
        return unquote(string)    # Function replaces %xx with escape sequence ...
    except Exception:
        return None




def redirect_response(target_page , **kwargs):
    
    """Function to create redirect url with correct parameters like next..."""
    
    next_url = Storage.request.args.get("next")
    resp = make_response(redirect(url_for(target_page , **kwargs)))
    if next_url :
        resp = make_response(redirect(url_for("login" , next = unquoted_url(next_url) , **kwargs)))
        
    return resp


def render_response(html_template , **kwargs):
    
    """Function to create response of render template..."""
    
    resp = make_response(render_template(html_template , **kwargs))
    return resp    


def redirect_to_next(target_page):
    
    """Function redirects the user to the next page in next parameter of url or to the target_page (set as default redirect)..."""
    
    """If any error occurs then returns abort(400)..."""
    
    next_url = Storage.request.args.get("next")    
    
    if not is_safe_url(next_url):
        return None
    
    try: 
        return make_response(redirect(unquoted_url(next_url) or url_for(target_page)))
    except Exception:
        return None
    
    