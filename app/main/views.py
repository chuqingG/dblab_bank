from flask import render_template, redirect, url_for, make_response, request, current_app, flash
from .forms import BranchSearchForm, BranchEditForm, EmployeeEditForm, EmployeeSearchForm, ClientEditForm, \
    ClientSearchForm, SavingAccountEditForm, SavingAccountSearchForm, CheckAccountEditForm, CheckAccountSearchForm, LoanEditForm, LoanSearchForm, LoanLogEditForm
from . import main
from .. import db
from ..models import Branch, Employee, Client, SavingAccount, ClientSaving, SavingConstraint, CheckAccount, ClientCheck, CheckConstraint, HasLoan, Loan, LoanLog, BranchRecords
from sqlalchemy import extract
import datetime
import time


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/branch', methods=['GET', 'POST'])
def branch():
    form = BranchSearchForm()
    if form.validate_on_submit():
        resp = make_response(redirect(url_for('.branch')))
        resp.set_cookie('search_branch_name', form.name.data, max_age=10*60)
        resp.set_cookie('search_branch_city', form.city.data, max_age=10*60)
        return resp
    query = Branch.query
    search_branch_name = request.cookies.get('search_branch_name', '')
    search_branch_city = request.cookies.get('search_branch_city', '')
    if search_branch_name != '':
        query = query.filter(Branch.name.like('%' + search_branch_name + '%'))
        form.name.data = search_branch_name
    if search_branch_city != '':
        query = query.filter(Branch.city.like('%' + search_branch_city + '%'))
        form.city.data = search_branch_city

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    branches = pagination.items

    return render_template('branch.html', form=form, branches=branches, pagination=pagination)


@main.route('/branch_all')
def branch_show_all():
    resp = make_response(redirect(url_for('.branch')))
    resp.set_cookie('search_branch_name', '', max_age=10*60)
    resp.set_cookie('search_branch_city', '', max_age=10*60)
    return resp


@main.route('/branch_edit/<string:branch_name>', methods=['GET', 'POST'])
def branch_edit(branch_name):
    form = BranchEditForm()
    if form.validate_on_submit():
        if branch_name == 'create':
            if Branch.query.filter_by(name=form.name.data).first():
                flash('该支行名已经存在')
                return render_template('branch_edit.html', form=form)
            branch = Branch(
                name=form.name.data,
                city=form.city.data,
                asset=form.asset.data
            )
            db.session.add(branch)
            db.session.commit()
            flash('已添加新支行')
            return redirect(url_for('.branch_edit', branch_name=branch.name))
        else:
            branch = Branch.query.filter_by(name=branch_name).first_or_404()
            if branch.name != form.name.data:
                if Branch.query.filter_by(name=form.name.data).first():
                    flash("该支行名已经存在")
                    return render_template('branch_edit.html', form=form)
            branch.name = form.name.data
            branch.city = form.city.data
            branch.asset = form.asset.data
            db.session.add(branch)
            db.session.commit()
            flash('该支行信息已更新')
            return redirect(url_for('.branch_edit', branch_name=branch.name))

    if branch_name != 'create':
        branch = Branch.query.filter_by(name=branch_name).first_or_404()
        form.name.data = branch.name
        form.city.data = branch.city
        form.asset.data = branch.asset

    return render_template('branch_edit.html', form=form)


@main.route('/branch_delete/<string:id>')
def branch_delete(id):
    branch = Branch.query.filter_by(name=id).first_or_404()
    if branch.loans.first():
        flash('该支行仍有贷款，无法删除')
        return redirect(url_for('.branch_show_all'))
    if branch.saving_accounts.first():
        flash('该支行仍有储蓄账户，无法删除')
        return redirect(url_for('.branch_show_all'))
    if branch.check_accounts.first():
        flash('该支行仍有支票账户，无法删除')
        return redirect(url_for('.branch_show_all'))
    if branch.employees.first():
        flash('该支行仍有员工，无法删除')
        return redirect(url_for('.branch_show_all'))
    db.session.delete(branch)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.branch_show_all'))


@main.route('/employee', methods=['GET', 'POST'])
def employee():
    form = EmployeeSearchForm()
    if form.validate_on_submit():
        resp = make_response(redirect(url_for('.employee')))
        resp.set_cookie('search_employee_id', form.id.data, max_age=10*60)
        resp.set_cookie('search_employee_name', form.name.data, max_age=10*60)
        resp.set_cookie('search_employee_branch_name',
                        form.branch_name.data, max_age=10*60)
        resp.set_cookie('search_employee_phone',
                        form.phone.data, max_age=10*60)
        resp.set_cookie('search_employee_address',
                        form.address.data, max_age=10*60)
        return resp

    query = Employee.query

    search_employee_id = request.cookies.get('search_employee_id', '')
    search_employee_name = request.cookies.get('search_employee_name', '')
    search_employee_branch_name = request.cookies.get(
        'search_employee_branch_name', '')
    search_employee_phone = request.cookies.get('search_employee_phone', '')
    search_employee_address = request.cookies.get(
        'search_employee_address', '')

    if search_employee_id != '':
        query = query.filter_by(id=search_employee_id)
        form.id.data = search_employee_id
    if search_employee_name != '':
        query = query.filter(Employee.name.like(
            '%' + search_employee_name + '%'))
        form.name.data = search_employee_name
    if search_employee_branch_name != '':
        query = query.filter_by(branch_name=search_employee_branch_name)
        form.branch_name.data = search_employee_branch_name
    if search_employee_phone != '':
        query = query.filter_by(phone=search_employee_phone)
        form.phone.data = search_employee_phone
    if search_employee_address != '':
        query = query.filter(Employee.address.like(
            '%' + search_employee_address + '%'))
        form.address.data = search_employee_address

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    employees = pagination.items

    return render_template('employee.html', form=form, employees=employees, pagination=pagination)


@main.route('/employee_edit/<string:employee_id>', methods=['GET', 'POST'])
def employee_edit(employee_id):
    form = EmployeeEditForm()
    if form.validate_on_submit():
        if employee_id == 'create':
            if Employee.query.filter_by(id=form.id.data).first():
                flash('该身份证号已经存在')
                return render_template('employee_edit.html', form=form)
            employee = Employee(
                id=form.id.data,
                name=form.name.data,
                branch_name=form.branch_name.data,
                phone=form.phone.data,
                address=form.address.data,
                enroll_date=form.enroll_date.data
            )
            db.session.add(employee)
            db.session.commit()
            flash('已添加员工')
            return redirect(url_for('.employee_edit', employee_id=employee.id))
        else:
            employee = Employee.query.filter_by(id=employee_id).first_or_404()
            if employee.id != form.id.data:
                if Employee.query.filter_by(id=form.id.data).first():
                    flash("该身份证号已经存在")
                    return render_template('employee_edit.html', form=form)
            employee.id = form.id.data
            employee.name = form.name.data
            employee.branch_name = form.branch_name.data
            employee.phone = form.phone.data
            employee.address = form.address.data
            employee.enroll_date = form.enroll_date.data
            db.session.add(employee)
            db.session.commit()
            flash('该员工信息已更新')
            return redirect(url_for('.employee_edit', employee_id=employee.id))

    if employee_id != 'create':
        employee = Employee.query.filter_by(id=employee_id).first_or_404()
        form.id.data = employee.id
        form.name.data = employee.name
        form.branch_name.data = employee.branch_name
        form.phone.data = employee.phone
        form.address.data = employee.address
        form.enroll_date.data = employee.enroll_date

    return render_template('employee_edit.html', form=form)


@main.route('/employee_all')
def employee_show_all():
    resp = make_response(redirect(url_for('.employee')))
    resp.set_cookie('search_employee_id', '', max_age=10*60)
    resp.set_cookie('search_employee_name', '', max_age=10*60)
    resp.set_cookie('search_employee_branch_name', '', max_age=10*60)
    resp.set_cookie('search_employee_phone', '', max_age=10*60)
    resp.set_cookie('search_employee_address', '', max_age=10*60)
    return resp


@main.route('/employee_delete/<string:id>')
def employee_delete(id):
    employee = Employee.query.filter_by(id=id).first_or_404()
    if employee.loans_managed.first():
        flash('该员工仍管理贷款，无法删除')
        return redirect(url_for('.employee_show_all'))
    if employee.saving_accounts_managed.first():
        flash('该员工仍管理某储蓄账户，无法删除')
        return redirect(url_for('.employee_show_all'))
    if employee.check_accounts_managed.first():
        flash('该员工仍管理某支票账户，无法删除')
        return redirect(url_for('.employee_show_all'))
    db.session.delete(employee)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.employee_show_all'))


@main.route('/client', methods=['GET', 'POST'])
def client():
    form = ClientSearchForm()
    if form.validate_on_submit():
        resp = make_response(redirect(url_for('.client')))
        resp.set_cookie('search_client_id', form.id.data, max_age=10*60)
        resp.set_cookie('search_client_name', form.name.data, max_age=10*60)
        resp.set_cookie('search_client_phone', form.phone.data, max_age=10*60)
        resp.set_cookie('search_client_address',
                        form.address.data, max_age=10*60)
        resp.set_cookie('search_client_contact_name',
                        form.contact_name.data, max_age=10*60)
        return resp

    query = Client.query

    search_client_id = request.cookies.get('search_client_id', '')
    search_client_name = request.cookies.get('search_client_name', '')
    search_client_phone = request.cookies.get('search_client_phone', '')
    search_client_address = request.cookies.get('search_client_address', '')
    search_client_contact_name = request.cookies.get(
        'search_client_contact_name', '')

    if search_client_id != '':
        query = query.filter_by(id=search_client_id)
        form.id.data = search_client_id
    if search_client_name != '':
        query = query.filter(Client.name.like('%' + search_client_name + '%'))
        form.name.data = search_client_name
    if search_client_phone != '':
        query = query.filter_by(phone=search_client_phone)
        form.phone.data = search_client_phone
    if search_client_address != '':
        query = query.filter(Client.address.like(
            '%' + search_client_address + '%'))
        form.address.data = search_client_address
    if search_client_contact_name != '':
        query = query.filter(Client.contact_name.like(
            '%' + search_client_contact_name + '%'))
        form.contact_name.data = search_client_contact_name

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    clients = pagination.items

    return render_template('client.html', form=form, clients=clients, pagination=pagination)


@main.route('/client_edit/<string:client_id>', methods=['GET', 'POST'])
def client_edit(client_id):
    form = ClientEditForm()
    if form.validate_on_submit():
        if client_id == 'create':
            if Client.query.filter_by(id=form.id.data).first():
                flash('该身份证号已经存在')
                return render_template('client_edit.html', form=form)
            client = Client(
                id=form.id.data,
                name=form.name.data,
                phone=form.phone.data,
                address=form.address.data,
                contact_name=form.contact_name.data,
            )
            if form.contact_phone.data != '':
                client.contact_phone = form.contact_phone.data
            if form.contact_email.data != '':
                client.contact_email = form.contact_email.data
            if form.contact_relation.data != '':
                client.contact_relation = form.contact_relation.data
            db.session.add(client)
            db.session.commit()
            flash('已添加客户')
            return redirect(url_for('.client_edit', client_id=client.id))
        else:
            client = Client.query.filter_by(id=client_id).first_or_404()
            if client.id != form.id.data:
                if Client.query.filter_by(id=form.id.data).first():
                    flash("该身份证号已经存在")
                    return render_template('client_edit.html', form=form)
            client.id = form.id.data
            client.name = form.name.data
            client.phone = form.phone.data
            client.address = form.address.data
            client.contact_name = form.contact_name.data
            if form.contact_phone.data != '':
                client.contact_phone = form.contact_phone.data
            if form.contact_email.data != '':
                client.contact_email = form.contact_email.data
            if form.contact_relation.data != '':
                client.contact_relation = form.contact_relation.data
            db.session.add(client)
            db.session.commit()
            flash('该客户信息已更新')
            return redirect(url_for('.client_edit', client_id=client.id))

    if client_id != 'create':
        client = Client.query.filter_by(id=client_id).first_or_404()
        form.id.data = client.id
        form.name.data = client.name
        form.phone.data = client.phone
        form.address.data = client.address
        form.contact_name.data = client.contact_name
        form.contact_phone.data = client.contact_phone
        form.contact_email.data = client.contact_email
        form.contact_relation = client.contact_relation

    return render_template('client_edit.html', form=form)


@main.route('/client_all')
def client_show_all():
    resp = make_response(redirect(url_for('.client')))
    resp.set_cookie('search_client_id', '', max_age=10*60)
    resp.set_cookie('search_client_name', '', max_age=10*60)
    resp.set_cookie('search_client_phone', '', max_age=10*60)
    resp.set_cookie('search_client_address', '', max_age=10*60)
    resp.set_cookie('search_client_contact_name', '', max_age=10*60)
    return resp
    return render_template('client_edit.html', form=form)


@main.route('/client_delete/<string:id>')
def client_delete(id):
    client = Client.query.filter_by(id=id).first_or_404()
    if client.loans.first():
        flash('该客户仍有贷款，无法删除')
        return redirect(url_for('.client_show_all'))
    if client.saving_accounts.first():
        flash('该客户仍有储蓄账户，无法删除')
        return redirect(url_for('.client_show_all'))
    if client.check_accounts.first():
        flash('该客户仍有支票账户，无法删除')
        return redirect(url_for('.client_show_all'))
    db.session.delete(client)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.client_show_all'))


@main.route('/saving_account_edit/<string:account_id>', methods=['GET', 'POST'])
def saving_account_edit(account_id):
    form = SavingAccountEditForm()
    if form.validate_on_submit():
        if account_id == 'create':
            if SavingAccount.query.filter_by(id=form.id.data).first():
                flash('该账户编号已存在')
                return render_template('saving_account_edit.html', form=form)
            saving_account = SavingAccount(
                id=form.id.data,
                branch_name=form.branch_name.data,
                employee_id=form.employee_id.data,
                balance=form.balance.data,
                interest_rate=form.interest_rate.data,
                currency_type=form.currency_type.data
            )
            db.session.add(saving_account)
            for c_id in form.clients.data:
                client = Client.query.filter_by(id=c_id).first_or_404()
                client_saving = ClientSaving(client=client, saving_account=saving_account)
                db.session.add(client_saving)
                if SavingConstraint.query.filter_by(client_id=client.id, branch_name=saving_account.branch_name).first():
                    db.session.rollback()
                    flash('每个客户只允许在一个支行建立一个储蓄账户')
                    return render_template('saving_account_edit.html', form=form)
                saving_constraint = SavingConstraint(
                    client_id=client.id,
                    branch_name=saving_account.branch_name,
                    saving_id=saving_account.id
                )
                db.session.add(saving_constraint)
            # S
            branchreords = BranchRecords(
                id=int(time.time()),
                branch_name=form.branch_name.data,
                OpType="存款",
                OpMoney=form.balance.data
            )
            db.session.add(branchreords)
            # E
            db.session.commit()
            flash('已添加储蓄账户')
            return redirect(url_for('.saving_account_edit', account_id=saving_account.id))
        else:
            saving_account = SavingAccount.query.filter_by(id=account_id).first_or_404()
            if saving_account.id != form.id.data:
                if SavingAccount.query.filter_by(id=form.id.data).first():
                    flash('该账户编号已存在')
                    return render_template('saving_account_edit.html', form=form)

            # S
            delta = form.balance.data - saving_account.balance
            branch_records = BranchRecords(
                id=int(time.time()),
                branch_name=form.branch_name.data,
                OpMoney=abs(delta)
            )
            if delta >= 0:
                branch_records.OpType = '存款'
            else:
                branch_records.OpType = '取款'

            db.session.add(branch_records)
            # E

            orig_account_id = saving_account.id
            saving_account.id = form.id.data
            saving_account.branch_name = form.branch_name.data
            saving_account.employee_id = form.employee_id.data
            saving_account.balance = form.balance.data
            saving_account.interest_rate = form.interest_rate.data
            saving_account.currency_type = form.currency_type.data
            db.session.add(saving_account)

            ClientSaving.query.filter_by(saving_id=orig_account_id).delete()
            SavingConstraint.query.filter_by(saving_id=orig_account_id).delete()
            db.session.commit()

            for c_id in form.clients.data:
                client = Client.query.filter_by(id=c_id).first_or_404()
                client_saving = ClientSaving(client=client, saving_account=saving_account)
                db.session.add(client_saving)
                if SavingConstraint.query.filter_by(client_id=client.id, branch_name=saving_account.branch_name).first():
                    db.session.rollback()
                    flash('每个客户只允许在一个支行建立一个储蓄账户')
                    return render_template('saving_account_edit.html', form=form)
                saving_constraint = SavingConstraint(
                    client_id=client.id,
                    branch_name=saving_account.branch_name,
                    saving_id=saving_account.id
                )
                db.session.add(saving_constraint)

            db.session.commit()
            flash('该储蓄账户信息已更新')
            return redirect(url_for('.saving_account_edit', account_id=saving_account.id))

    if account_id != 'create':
        saving_account = SavingAccount.query.filter_by(id=account_id).first_or_404()
        clients = [c.client.id for c in saving_account.clients.all()]
        form.id.data = saving_account.id
        form.branch_name.data = saving_account.branch_name
        form.employee_id.data = saving_account.employee_id
        form.balance.data = saving_account.balance
        form.interest_rate.data = saving_account.interest_rate
        form.currency_type.data = saving_account.currency_type
        form.clients.data = clients

    return render_template('saving_account_edit.html', form=form)



@main.route('/saving_account', methods=['GET', 'POST'])
def saving_account():
    form = SavingAccountSearchForm()
    if form.validate_on_submit():
        resp = make_response(redirect(url_for('.saving_account')))
        resp.set_cookie('search_sa_id', form.id.data, max_age=10*60)
        resp.set_cookie('search_sa_branch_name', form.branch_name.data, max_age=10*60)
        resp.set_cookie('search_sa_employee_id', form.employee_id.data, max_age=10*60)
        resp.set_cookie('search_sa_clients', ','.join(form.clients.data), max_age=10*60)
        return resp

    query = SavingAccount.query

    search_sa_id = request.cookies.get('search_sa_id', '')
    search_sa_branch_name = request.cookies.get('search_sa_branch_name', '')
    search_sa_employee_id = request.cookies.get('search_sa_employee_id', '')
    search_sa_clients = request.cookies.get('search_sa_clients', '')
    if search_sa_clients != '':
        search_sa_clients = search_sa_clients.split(',')
    else:
        search_sa_clients = []

    if search_sa_id != '':
        query = query.filter_by(id=search_sa_id)
        form.id.data = search_sa_id
    if search_sa_branch_name != '':
        query = query.filter_by(branch_name=search_sa_branch_name)
        form.branch_name.data = search_sa_branch_name
    if search_sa_employee_id != '':
        query = query.filter_by(employee_id=search_sa_employee_id)
        form.employee_id.data = search_sa_employee_id
    if search_sa_clients != []:
        for c_id in search_sa_clients:
            query = query.filter(SavingAccount.clients.any(client_id=c_id))
        form.clients.data = search_sa_clients

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    saving_accounts = pagination.items

    return render_template('saving_account.html', form=form, saving_accounts=saving_accounts, pagination=pagination)


@main.route('/saving_account_all')
def saving_account_show_all():
    resp = make_response(redirect(url_for('.saving_account')))
    resp.set_cookie('search_sa_id', '', max_age=10*60)
    resp.set_cookie('search_sa_branch_name', '', max_age=10*60)
    resp.set_cookie('search_sa_employee_id', '', max_age=10*60)
    resp.set_cookie('search_sa_clients', '', max_age=10*60)
    return resp


@main.route('/saving_account_delete/<string:account_id>')
def saving_account_delete(account_id):
    saving_account = SavingAccount.query.filter_by(id=account_id).first_or_404()
    ClientSaving.query.filter_by(saving_id=saving_account.id).delete()
    SavingConstraint.query.filter_by(saving_id=saving_account.id).delete()
    db.session.delete(saving_account)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.saving_account_show_all'))


@main.route('/check_account_edit/<string:account_id>', methods=['GET', 'POST'])
def check_account_edit(account_id):
    form = CheckAccountEditForm()
    if form.validate_on_submit():
        if account_id == 'create':
            if CheckAccount.query.filter_by(id=form.id.data).first():
                flash('该账户编号已存在')
                return render_template('check_account_edit.html', form=form)
            check_account = CheckAccount(
                id=form.id.data,
                branch_name=form.branch_name.data,
                employee_id=form.employee_id.data,
                balance=form.balance.data,
                over_draft=form.over_draft.data
            )
            db.session.add(check_account)
            for c_id in form.clients.data:
                client = Client.query.filter_by(id=c_id).first_or_404()
                client_check = ClientCheck(client=client, check_account=check_account)
                db.session.add(client_check)
                if CheckConstraint.query.filter_by(client_id=client.id, branch_name=check_account.branch_name).first():
                    db.session.rollback()
                    flash('每个客户只允许在一个支行建立一个支票账户')
                    return render_template('check_account_edit.html', form=form)
                check_constraint = CheckConstraint(
                    client_id=client.id,
                    branch_name=check_account.branch_name,
                    check_id=check_account.id
                )
                db.session.add(check_constraint)
            db.session.commit()
            flash('已添加支票账户')
            return redirect(url_for('.check_account_edit', account_id=check_account.id))
        else:
            check_account = CheckAccount.query.filter_by(id=account_id).first_or_404()
            if check_account.id != form.id.data:
                if CheckAccount.query.filter_by(id=form.id.data).first():
                    flash('该账户编号已存在')
                    return render_template('check_account_edit.html', form=form)
            orig_account_id = check_account.id
            check_account.id = form.id.data
            check_account.branch_name = form.branch_name.data
            check_account.employee_id = form.employee_id.data
            check_account.balance = form.balance.data
            check_account.over_draft = form.over_draft.data

            db.session.add(check_account)

            ClientCheck.query.filter_by(check_id=orig_account_id).delete()
            CheckConstraint.query.filter_by(check_id=orig_account_id).delete()
            db.session.commit()

            for c_id in form.clients.data:
                client = Client.query.filter_by(id=c_id).first_or_404()
                client_check = ClientCheck(client=client, check_account=check_account)
                db.session.add(client_check)
                if CheckConstraint.query.filter_by(client_id=client.id, branch_name=check_account.branch_name).first():
                    db.session.rollback()
                    flash('每个客户只允许在一个支行建立一个支票账户')
                    return render_template('check_account_edit.html', form=form)
                check_constraint = CheckConstraint(
                    client_id=client.id,
                    branch_name=check_account.branch_name,
                    check_id=check_account.id
                )
                db.session.add(check_constraint)

            db.session.commit()
            flash('该支票账户信息已更新')
            return redirect(url_for('.check_account_edit', account_id=check_account.id))

    if account_id != 'create':
        check_account = CheckAccount.query.filter_by(id=account_id).first_or_404()
        clients = [c.client.id for c in check_account.clients.all()]
        form.id.data = check_account.id
        form.branch_name.data = check_account.branch_name
        form.employee_id.data = check_account.employee_id
        form.balance.data = check_account.balance
        form.over_draft.data = check_account.over_draft
        form.clients.data = clients

    return render_template('check_account_edit.html', form=form)


@main.route('/check_account', methods=['GET', 'POST'])
def check_account():
    form = CheckAccountSearchForm()
    if form.validate_on_submit():
        resp = make_response(redirect(url_for('.check_account')))
        resp.set_cookie('search_ca_id', form.id.data, max_age=10*60)
        resp.set_cookie('search_ca_branch_name', form.branch_name.data, max_age=10*60)
        resp.set_cookie('search_ca_employee_id', form.employee_id.data, max_age=10*60)
        resp.set_cookie('search_ca_clients', ','.join(form.clients.data), max_age=10*60)
        return resp

    query = CheckAccount.query

    search_ca_id = request.cookies.get('search_ca_id', '')
    search_ca_branch_name = request.cookies.get('search_ca_branch_name', '')
    search_ca_employee_id = request.cookies.get('search_ca_employee_id', '')
    search_ca_clients = request.cookies.get('search_ca_clients', '')
    if search_ca_clients != '':
        search_ca_clients = search_ca_clients.split(',')
    else:
        search_ca_clients = []

    if search_ca_id != '':
        query = query.filter_by(id=search_ca_id)
        form.id.data = search_ca_id
    if search_ca_branch_name != '':
        query = query.filter_by(branch_name=search_ca_branch_name)
        form.branch_name.data = search_ca_branch_name
    if search_ca_employee_id != '':
        query = query.filter_by(employee_id=search_ca_employee_id)
        form.employee_id.data = search_ca_employee_id
    if search_ca_clients != []:
        for c_id in search_ca_clients:
            query = query.filter(CheckAccount.clients.any(client_id=c_id))
        form.clients.data = search_ca_clients

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    check_accounts = pagination.items

    return render_template('check_account.html', form=form, check_accounts=check_accounts, pagination=pagination)


@main.route('/check_account_all')
def check_account_show_all():
    resp = make_response(redirect(url_for('.check_account')))
    resp.set_cookie('search_ca_id', '', max_age=10*60)
    resp.set_cookie('search_ca_branch_name', '', max_age=10*60)
    resp.set_cookie('search_ca_employee_id', '', max_age=10*60)
    resp.set_cookie('search_ca_clients', '', max_age=10*60)
    return resp


@main.route('/check_account_delete/<string:account_id>')
def check_account_delete(account_id):
    check_account = CheckAccount.query.filter_by(id=account_id).first_or_404()
    ClientCheck.query.filter_by(check_id=check_account.id).delete()
    CheckConstraint.query.filter_by(check_id=check_account.id).delete()
    db.session.delete(check_account)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.check_account_show_all'))


@main.route('/loan_edit/<string:loan_id>', methods=['GET', 'POST'])
def loan_edit(loan_id):
    form = LoanEditForm()
    if form.validate_on_submit():
        if loan_id == 'create':
            if Loan.query.filter_by(id=form.id.data).first():
                flash('该贷款编号已存在')
                return render_template('loan_edit.html', form=form)
            loan = Loan(
                id=form.id.data,
                branch_name=form.branch_name.data,
                employee_id=form.employee_id.data,
                amount=form.amount.data
            )
            db.session.add(loan)
            for c_id in form.clients.data:
                client = Client.query.filter_by(id=c_id).first_or_404()
                client_loan = HasLoan(client=client, loan=loan)
                db.session.add(client_loan)
            db.session.commit()
            flash('已添加贷款')
            return redirect(url_for('.loan_show_all'))
        else:
            loan = Loan.query.filter_by(id=loan_id).first_or_404()
            if loan.id != form.id.data:
                if Loan.query.filter_by(id=form.id.data).first():
                    flash('该贷款编号已存在')
                    return render_template('loan_edit.html', form=form)
            orig_loan_id = loan.id
            loan.id = form.id.data
            loan.branch_name = form.branch_name.data
            loan.employee_id = form.employee_id.data
            loan.amount = form.amount.data
            db.session.add(loan)

            HasLoan.query.filter_by(loan_id=orig_loan_id).delete()
            db.session.commit()

            for c_id in form.clients.data:
                client = Client.query.filter_by(id=c_id).first_or_404()
                client_loan = HasLoan(client=client, loan=loan)
                db.session.add(client_loan)
            db.session.commit()
            flash('该贷款信息已更新')
            return redirect(url_for('.loan_show_all'))

    if loan_id != 'create':
        loan = Loan.query.filter_by(id=loan_id).first_or_404()
        clients = [c.client.id for c in loan.clients.all()]
        form.id.data = loan.id
        form.branch_name.data = loan.branch_name
        form.employee_id.data = loan.employee_id
        form.amount.data = loan.amount
        form.clients.data = clients

    return render_template('loan_edit.html', form=form)


@main.route('/loan', methods=['GET', 'POST'])
def loan():
    form = LoanSearchForm()
    if form.validate_on_submit():
        resp = make_response(redirect(url_for('.loan')))
        resp.set_cookie('search_loan_id', form.id.data, max_age=10*60)
        resp.set_cookie('search_loan_branch_name', form.branch_name.data, max_age=10*60)
        resp.set_cookie('search_loan_employee_id', form.employee_id.data, max_age=10*60)
        resp.set_cookie('search_loan_clients', ','.join(form.clients.data), max_age=10*60)
        return resp

    query = Loan.query

    search_loan_id = request.cookies.get('search_loan_id', '')
    search_loan_branch_name = request.cookies.get('search_loan_branch_name', '')
    search_loan_employee_id = request.cookies.get('search_loan_employee_id', '')
    search_loan_clients = request.cookies.get('search_loan_clients', '')
    if search_loan_clients != '':
        search_loan_clients = search_loan_clients.split(',')
    else:
        search_loan_clients = []

    if search_loan_id != '':
        query = query.filter_by(id=search_loan_id)
        form.id.data = search_loan_id
    if search_loan_branch_name != '':
        query = query.filter_by(branch_name=search_loan_branch_name)
        form.branch_name.data = search_loan_branch_name
    if search_loan_employee_id != '':
        query = query.filter_by(employee_id=search_loan_employee_id)
        form.employee_id.data = search_loan_employee_id
    if search_loan_clients != []:
        for c_id in search_loan_clients:
            query = query.filter(Loan.clients.any(client_id=c_id))
        form.clients.data = search_loan_clients

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    loans = pagination.items

    return render_template('loan.html', form=form, loans=loans, pagination=pagination)


@main.route('/loan_all')
def loan_show_all():
    resp = make_response(redirect(url_for('.loan')))
    resp.set_cookie('search_loan_id', '', max_age=10*60)
    resp.set_cookie('search_loan_branch_name', '', max_age=10*60)
    resp.set_cookie('search_loan_employee_id', '', max_age=10*60)
    resp.set_cookie('search_loan_clients', '', max_age=10*60)
    return resp


@main.route('/loan_log_edit/<string:loan_log_id>', methods=['GET', 'POST'])
def loan_log_edit(loan_log_id):
    form = LoanLogEditForm()
    if request.args.get('loan_id'):
        form.loan_id.data = request.args.get('loan_id')
    if form.validate_on_submit():
        if loan_log_id == 'create':
            if LoanLog.query.filter_by(id=form.id.data).first():
                flash('该贷款支付编号已存在')
                return render_template('loan_log_edit.html', form=form)
            loan_log = LoanLog(
                id=form.id.data,
                loan_id=form.loan_id.data,
                amount=form.amount.data
            )
            ll = Loan.query.filter_by(id=form.loan_id.data).first()
            if ll.status == '已全部发放':
                flash('该贷款已经全部发放')
                return render_template('loan_log_edit.html', form=form)
            db.session.add(loan_log)
            db.session.commit()
            total_amount = sum([log.amount for log in loan_log.loan.loan_logs.all()])
            if total_amount >= loan_log.loan.amount:
                loan = loan_log.loan
                loan.status = '已全部发放'
                db.session.add(loan)
                db.session.commit()
            else:
                loan = loan_log.loan
                loan.status = '发放中'

                # S
                branchreords = BranchRecords(
                    id=int(time.time()),
                    branch_name=Loan.query.filter(Loan.id == form.loan_id.data).all()[0].branch_name,
                    OpType="放贷",
                    OpMoney=form.amount.data
                )
                db.session.add(branchreords)

                # E

                db.session.add(loan)
                db.session.commit()
            flash('已添加')
            return redirect(url_for('.loan_show_all'))
        else:
            loan_log = LoanLog.query.filter_by(id=loan_log_id).first_or_404()
            if loan.id != form.id.data:
                if LoanLog.query.filter_by(id=form.id.data).first():
                    flash('该贷款支付编号已经存在')
                    return render_template('loan_log_edit.html', form=form)
            if loan_log.loan.status == '已全部发放':
                flash('该贷款已经全部发放')
                return render_template('loan_log_edit.html', form=form)
            loan_log.id = form.id.data
            loan_log.loan_id = form.loan_id.data
            loan_log.amount = form.amount.data
            db.session.add(loan)
            db.session.commit(loan)

            total_amount = sum([log.amount for log in loan_log.loan.loan_logs.all()])
            if total_amount >= loan_log.loan.amount:
                loan = loan_log.loan
                loan.status = '已全部发放'
                db.session.add(loan)
                db.session.commit()
            else:
                # S
                branchreords = BranchRecords(
                    id=int(time.time()),
                    branch_name=Loan.query.filter(Loan.id == form.loan_id.data).all()[0].branch_name,
                    OpType="放贷",
                    OpMoney=form.amount.data
                )
                db.session.add(branchreords)
                # E
                loan = loan_log.loan
                loan.status = '发放中'
                db.session.add(loan)
                db.session.commit()
            flash('已更新贷款支付信息')
            return redirect(url_for('.loan_show_all'))


    if loan_log_id != 'create':
        loan_log = LoanLog.query.filter_by(id=loan_log_id).first_or_404()
        form.id.data = loan_log.id
        form.loan_id.data = loan_log.loan_id
        form.amount.data = loan_log.amount

    return render_template('loan_log_edit.html', form=form)


@main.route('/loan_log/<string:loan_id>')
def loan_log(loan_id):
    query = LoanLog.query.filter_by(loan_id=loan_id)
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    loan_logs = pagination.items

    return render_template('loan_log.html', loan_logs=loan_logs, pagination=pagination, loan_id=loan_id)


@main.route('/loan_delete/<string:loan_id>')
def loan_delete(loan_id):
    loan = Loan.query.filter_by(id=loan_id).first_or_404()
    if loan.status == '发放中':
        flash('贷款正在发放中，无法删除')
        return redirect(url_for('.loan_show_all'))
    loan.clients.delete()
    loan.loan_logs.delete()
    db.session.delete(loan)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.loan_show_all'))


@main.route('/census/<string:id>')
def census(id):

    year = 0
    if request.args.get('year'):
        year = int(request.args.get('year'))

    if id == '0':
        userNums = {}
        totalMoneyIn1 = {}
        totalMoneyIn2 = {}
        totalMoneyOut1 = {}
        totalMoneyOut2 = {}

        bs = Branch.query.all()
        for b in bs:
            ls = Loan.query.filter(Loan.branch_name == b.name).all()
            temp = []
            for l in ls:
                temp += [ul.client_id for ul in HasLoan.query.filter(HasLoan.loan_id==l.id).all()]
            temp += [uda.client_id for uda in SavingConstraint.query.filter(SavingConstraint.branch_name == b.name).all()]
            temp += [uda.client_id for uda in CheckConstraint.query.filter(CheckConstraint.branch_name == b.name).all()]
            userNums[b.name] = len(set(temp))
            print(f"{b.name}: {userNums[b.name]}")
            brs = BranchRecords.query
            if year != 0:
                brs = brs.filter(extract('year', BranchRecords.OpTime) == year)
            brs = brs.filter(BranchRecords.branch_name==b.name)
            totalMoneyIn1[b.name] = sum([br.OpMoney for br in brs.filter(BranchRecords.OpType=='存款').all()])
            totalMoneyOut1[b.name] = sum([br.OpMoney for br in brs.filter(BranchRecords.OpType=='取款').all()])
            totalMoneyIn2[b.name] = sum([br.OpMoney for br in brs.filter(BranchRecords.OpType=='还款').all()])
            totalMoneyOut2[b.name] = sum([br.OpMoney for br in brs.filter(BranchRecords.OpType=='放贷').all()])
            print(f"{b.name}: {totalMoneyIn1[b.name]}")
        print("here")
        return render_template('census.html',bs=bs, uns=userNums, mi1=totalMoneyIn1, mi2=totalMoneyIn2,
                               mo1=totalMoneyOut1, mo2=totalMoneyOut2, year = '')

    else:
        #查询具体某个支行
        yearMoneyIn1 = [0] * 12
        yearMoneyIn2 = [0] * 12
        yearMoneyOut1 = [0] * 12
        yearMoneyOut2 = [0] * 12

        if year == 0:
            year = datetime.date.today().year
        b = Branch.query.get(id)
        if not b:
            flash('没有该支行的信息！')
            return redirect(url_for('census_page',id='0'))
        brs = BranchRecords.query.filter(BranchRecords.branch_name == id).filter(extract('year', BranchRecords.OpTime) == year)
        for month in range(1, 13):
            brs1 = brs.filter(extract('month', BranchRecords.OpTime) == month)
            yearMoneyIn1[month - 1] = sum([br.OpMoney for br in brs1.filter(BranchRecords.OpType=='存款').all()])
            yearMoneyOut1[month - 1] = sum([br.OpMoney for br in brs1.filter(BranchRecords.OpType == '取款').all()])
            yearMoneyIn2[month - 1] = sum([br.OpMoney for br in brs1.filter(BranchRecords.OpType == '还款').all()])
            yearMoneyOut2[month - 1] = sum([br.OpMoney for br in brs1.filter(BranchRecords.OpType == '放贷').all()])

        return render_template('census.html', uns=0, bs=b, mi1=yearMoneyIn1, mi2=yearMoneyIn2,
                               mo1=yearMoneyOut1, mo2=yearMoneyOut2, year = str(year))