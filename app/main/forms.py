class NameForm(FlaskForm):  # 定义表单
    name = StringField('what is your name?', validators=[Required()])
    submit = SubmitField('Submit')
 