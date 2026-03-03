# class User(db.Model):
    
#     __bind_key__ = "sn_users"
    
#     sno = db.Column(db.Integer(), primary_key=True)
#     user_name = db.Column(db.String(30), nullable=False)
#     user_email = db.Column(db.String(320), unique=True, nullable=False)
#     password = db.Column(db.Binary(60), nullable=False)
#     data = db.Column(db.String(),  nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.user_name


# Announcements --------------
