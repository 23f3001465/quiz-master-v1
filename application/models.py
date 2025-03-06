from .database import db #check for the file in existing folder n not root folder
#if i write appln.database then it will assume appln is one more folder jjwhere 
# class User(db.Model):
#     id= db.Column(db.Integer(),primary_key = True)
#     username= db.Column(db.String(),unique= True, nullable=False)
#     email= db.Column(db.String(),unique= True, nullable=False)
#     password= db.Column(db.String(), nullable=False)
#     type= db.Column(db.String(), default = 'general')
#     details= db.relationship("Info", backref= "creator")

# class Info (db.Model):
#     id= db.Column(db.Integer(),primary_key = True)
#     atr_name= db.Column(db.String(), nullable=False)
#     atr_value= db.Column(db.String(), nullable=False)
#     c_name= db.Column(db.String(), nullable=False)
#     user_id= db.Column(db.Integer(),db.ForeignKey("user.id"),nullable = False)



