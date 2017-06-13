from views import Login, SignIn, SignOut, index


routes = [
    ('*',   '/',        index,     'main'),
    ('*',   '/login',   Login,     'login'),
    ('*',   '/signin',  SignIn,    'signin'),
    ('*',   '/signout', SignOut,   'signout'),
]
