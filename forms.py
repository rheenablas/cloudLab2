from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, FloatField, SelectField
from wtforms.validators import NumberRange, Optional

class QueryForm(FlaskForm):
    age = IntegerField("Age: ", validators=[Optional(strip_whitespace=True)])
    #rate = FloatField("Rate: ", validators=[Optional(strip_whitespace=True)])
    year = IntegerField("Year: ", validators=[Optional(strip_whitespace=True)])
    gender = SelectField('Gender: ', choices = [('', ''), ("Male", "Male"), ("Female", "Female")])
    stat_code = SelectField("Statistic Code: ", choices = [('', ''), ("VSA49C01", "VSA49C01"), ("VSA49C02", "VSA49C02")])
    submit = SubmitField("Query")



