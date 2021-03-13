import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FormField, BooleanField, FieldList, FileField
from wtforms.fields.html5 import IntegerRangeField, DateField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l

from WebAppOptimizer.app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class BodyForm(FlaskForm):
    config = requests.get('http://0.0.0.0:4996/api/27/getInfo').json()['data']
    # ['PONTLAB_1', 'PONTLAB_2', 'PV_1', "PV_2", "WIND_1", "WIND_2", 'BESS_1', 'BESS_2', 'LOAD_1', 'LOAD_2','LOAD_3', 'LOAD_4', "CONF_1", "CONF_2","CONF_3", "CONF_4","CONF_5", "CONF_6", "CONF_7" ]

    i = 0
    for c in config:
        #if c['name'] == 'PONTLAB_1' or c['name'] == 'PONTLAB_2' or c['name'] ==  'BESS_1' or c['name'] == 'BESS_2' or c['name'] == 'LOAD_4':
        #    continue
        vars()[c['name']] = IntegerRangeField(_prefix=i, label=c['name'], default=0, description=c['description'])
        vars()[str(c['id'])] = StringField(default=c['description'])
        i += 1


class ConfigurationForm(FlaskForm):
    body = FormField(BodyForm)
    confname = StringField(_l('Configuration Name'))
    date = DateField(_l('Enter Date'), validators=[DataRequired()])
    remember_conf = BooleanField(_l('Save Configuration'))
    submit = SubmitField(_l('Submit'))


class GetFromLibraResultForm(FlaskForm):
    profile_id = StringField('Id')
    profile_name = StringField('Name')
    profile_description = StringField('Description')
    profile = StringField('Profiles')


class GetFromLibraForm(FlaskForm):
    submit = SubmitField(_l('Get Baselines'))
    textarea = TextAreaField(_l(''), render_kw={'class': 'form-control', 'rows': 5})
    table_title = StringField('Date')
    rows = FieldList(FormField(GetFromLibraResultForm))

class AggregatedOptimizationResultForm(FlaskForm):
    single = StringField('Single PODs')
    mixed = StringField('Mixed PODs')
    local_time = StringField('Time for Local Optimizations (s)')
    aggr_time = StringField('Time for Aggregated Optimizations (s)')
    tot_time = StringField('Total Optimization Time (s)')

class LocalOptimizationResultForm(FlaskForm):
    configuration = StringField('Configuration')
    composition = StringField('Composition')
    min_time = StringField('Time for minimization(s)')
    max_time = StringField('Time for maximization(s)')


class OptimizationForm(FlaskForm):
    submit1 = SubmitField(_l('Run Local Optimization'))
    image = FileField(u'Image File')
    submit2 = SubmitField(_l('Aggregate'))
    textarea = TextAreaField(_l(''), render_kw={'class': 'form-control', 'rows': 5})
    table_title = StringField('Date')
    local_rows = FieldList(FormField(LocalOptimizationResultForm))
    aggr_rows = FieldList(FormField(AggregatedOptimizationResultForm))
