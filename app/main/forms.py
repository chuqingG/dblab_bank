from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Regexp, Optional, Email
from wtforms.fields.html5 import DateField
from ..models import Branch, Employee, Client, Loan


class BranchSearchForm(FlaskForm):
    name = StringField("支行名")
    city = StringField("所在城市")
    submit = SubmitField("搜索")


class BranchEditForm(FlaskForm):
    name = StringField("支行名", validators=[InputRequired()])
    city = StringField("所在城市", validators=[InputRequired()])
    asset = FloatField("资产", validators=[InputRequired(), NumberRange(min=0., message='资产必须大于0')])
    submit = SubmitField("提交")


class EmployeeSearchForm(FlaskForm):
    id = StringField("身份证号", validators=[
        Optional(),
        Regexp(r'^([1-9]\d{5}[12]\d{3}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d{3}[0-9xX])$', 0,
               "身份证号不合法")
    ])
    name = StringField("姓名")
    branch_name = SelectField('所在支行')
    phone = StringField("手机号")
    address = StringField("联系地址")
    submit = SubmitField("搜索")

    def __init__(self, *args, **kwargs):
        super(EmployeeSearchForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [('', '')]
        self.branch_name.choices.extend([(branch.name, branch.name)
                                         for branch in Branch.query.all()])


class EmployeeEditForm(FlaskForm):
    id = StringField("身份证号", validators=[
        InputRequired(),
        Regexp(r'^([1-9]\d{5}[12]\d{3}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d{3}[0-9xX])$', 0,
               "身份证号不合法")
    ])
    name = StringField("姓名", validators=[InputRequired()])
    branch_name = SelectField('所在支行')
    phone = StringField("手机号")
    address = StringField("联系地址")
    enroll_date = DateField("入职日期", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(EmployeeEditForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [(branch.name, branch.name)
                                    for branch in Branch.query.all()]


class ClientSearchForm(FlaskForm):
    id = StringField("身份证号", validators=[
        Optional(),
        Regexp(r'^([1-9]\d{5}[12]\d{3}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d{3}[0-9xX])$', 0,
               "身份证号不合法")
    ])
    name = StringField("姓名")
    phone = StringField("手机号")
    address = StringField("联系地址")
    contact_name = StringField("联系人姓名")
    submit = SubmitField("搜索")


class ClientEditForm(FlaskForm):
    id = StringField("身份证号", validators=[
        InputRequired(),
        Regexp(r'^([1-9]\d{5}[12]\d{3}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d{3}[0-9xX])$', 0,
               "身份证号不合法")
    ])
    name = StringField("姓名", validators=[InputRequired()])
    phone = StringField("手机号", validators=[InputRequired()])
    address = StringField("联系地址", validators=[InputRequired()])
    contact_name = StringField("联系人姓名", validators=[InputRequired()])
    contact_phone = StringField("联系人手机号")
    contact_email = StringField("联系人邮箱", validators=[Optional(), Email()])
    contact_relation = StringField("联系人与客户关系")
    submit = SubmitField("提交")


class SavingAccountSearchForm(FlaskForm):
    id = StringField("账号编号", validators=[])
    clients = SelectMultipleField("所属客户", validators=[])
    branch_name = SelectField('开户支行')
    employee_id = SelectField('负责员工')
    submit = SubmitField("搜索")

    def __init__(self, *args, **kwargs):
        super(SavingAccountSearchForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [('', '')]
        self.branch_name.choices.extend([(branch.name, branch.name)
                                         for branch in Branch.query.all()])
        self.clients.choices = [(client.id, client.name + ', ' + client.id)
                                for client in Client.query.all()]
        self.employee_id.choices = [('', '')]
        self.employee_id.choices.extend([(employee.id, employee.name + ', ' + employee.id)
                                         for employee in Employee.query.all()])


class SavingAccountEditForm(FlaskForm):
    id = StringField("账号编号", validators=[InputRequired()])
    branch_name = SelectField('开户支行', validators=[InputRequired()])
    employee_id = SelectField('负责员工', validators=[InputRequired()])
    balance = FloatField("余额", validators=[InputRequired(), NumberRange(min=0., message="余额必须大于0")])
    interest_rate = StringField("利率", validators=[InputRequired()])
    currency_type = StringField("货币类型", validators=[InputRequired()])
    clients = SelectMultipleField("所属客户", validators=[InputRequired()])
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(SavingAccountEditForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [(branch.name, branch.name)
                                    for branch in Branch.query.all()]
        self.clients.choices = [(client.id, client.name + ', ' + client.id)
                                for client in Client.query.all()]
        self.employee_id.choices = [(employee.id, employee.name + ', ' + employee.id)
                                    for employee in Employee.query.all()]


class CheckAccountSearchForm(FlaskForm):
    id = StringField("账号编号", validators=[])
    clients = SelectMultipleField("所属客户", validators=[])
    branch_name = SelectField('开户支行')
    employee_id = SelectField('负责员工')
    submit = SubmitField("搜索")

    def __init__(self, *args, **kwargs):
        super(CheckAccountSearchForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [('', '')]
        self.branch_name.choices.extend([(branch.name, branch.name)
                                         for branch in Branch.query.all()])
        self.clients.choices = [(client.id, client.name + ', ' + client.id)
                                for client in Client.query.all()]
        self.employee_id.choices = [('', '')]
        self.employee_id.choices.extend([(employee.id, employee.name + ', ' + employee.id)
                                         for employee in Employee.query.all()])


class CheckAccountEditForm(FlaskForm):
    id = StringField("账号编号", validators=[InputRequired()])
    branch_name = SelectField('开户支行', validators=[InputRequired()])
    employee_id = SelectField('负责员工', validators=[InputRequired()])
    balance = FloatField("余额", validators=[InputRequired(), NumberRange(min=0., message="余额必须大于0")])
    over_draft = FloatField("透支额", validators=[InputRequired(), NumberRange(min=0., message="透支额必须大于0")])
    clients = SelectMultipleField("所属客户", validators=[InputRequired()])
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(CheckAccountEditForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [(branch.name, branch.name)
                                    for branch in Branch.query.all()]
        self.clients.choices = [(client.id, client.name + ', ' + client.id)
                                for client in Client.query.all()]
        self.employee_id.choices = [(employee.id, employee.name + ', ' + employee.id)
                                    for employee in Employee.query.all()]


class LoanEditForm(FlaskForm):
    id = StringField("贷款编号", validators=[InputRequired()])
    branch_name = SelectField('贷款支行', validators=[InputRequired()])
    employee_id = SelectField('负责员工', validators=[InputRequired()])
    amount = FloatField("贷款金额", validators=[InputRequired(), NumberRange(min=0., message="贷款金额必须大于0")])
    clients = SelectMultipleField("所属客户", validators=[InputRequired()])
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(LoanEditForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [(branch.name, branch.name)
                                    for branch in Branch.query.all()]
        self.clients.choices = [(client.id, client.name + ', ' + client.id)
                                for client in Client.query.all()]
        self.employee_id.choices = [(employee.id, employee.name + ', ' + employee.id)
                                    for employee in Employee.query.all()]


class LoanSearchForm(FlaskForm):
    id = StringField("贷款编号", validators=[])
    clients = SelectMultipleField("所属客户", validators=[])
    branch_name = SelectField('贷款支行')
    employee_id = SelectField('负责员工')
    submit = SubmitField("搜索")

    def __init__(self, *args, **kwargs):
        super(LoanSearchForm, self).__init__(*args, **kwargs)
        self.branch_name.choices = [('', '')]
        self.branch_name.choices.extend([(branch.name, branch.name)
                                         for branch in Branch.query.all()])
        self.clients.choices = [(client.id, client.name + ', ' + client.id)
                                for client in Client.query.all()]
        self.employee_id.choices = [('', '')]
        self.employee_id.choices.extend([(employee.id, employee.name + ', ' + employee.id)
                                         for employee in Employee.query.all()])


class LoanLogEditForm(FlaskForm):
    id = StringField("贷款发放编号", validators=[InputRequired()])
    loan_id = SelectField('贷款编号', validators=[InputRequired()])
    amount = FloatField("发放金额", validators=[InputRequired(), NumberRange(min=0., message="发放金额必须大于0")])
    submit = SubmitField("提交")

    def __init__(self, *args, **kwargs):
        super(LoanLogEditForm, self).__init__(*args, **kwargs)
        self.loan_id.choices = [(loan.id, loan.id)
                                for loan in Loan.query.all()]
