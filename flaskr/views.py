from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from .db import get_db

bp = Blueprint('views', __name__)

@bp.route('/dashboard')
def dashboard():
    db=get_db()
    credit=db.execute(
          ' SELECT sum(MaintenanceFee)'
          ' FROM income'
        ).fetchone()
    debit=db.execute(
           ' SELECT sum(fee)'
           ' FROM expenses'
        ).fetchone()
    residents=db.execute(
           ' SELECT count(Name)'
           ' FROM income'
        ).fetchone()

    list = []

    list.append(credit[0])
    list.append(debit[0])

    return render_template('dashboard.html',list=list,residents=residents)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, Name,Block,UnitNo,MaintenanceFee,Due'
        ' FROM income p'
         
    ).fetchall()
    return render_template('index.html', posts=posts)

@bp.route('/paid')    
def paid():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, Name,Block,UnitNo,MaintenanceFee,Due'
        ' FROM income p '
        ' WHERE Due=0'
         
    ).fetchall()
    return render_template('paid.html', posts=posts)

@bp.route('/unpaid')     
def unpaid():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, Name,Block,UnitNo,MaintenanceFee,Due'
        ' FROM income p'
        ' WHERE Due>0'
         
    ).fetchall()
    return render_template('unpaid.html', posts=posts)       

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        Name = request.form['Name']
        Block = request.form['Block']
        UnitNo = request.form['UnitNo']
        MaintenanceFee = request.form['MaintenanceFee']
        Due = request.form['Due']
        error = None

        if not Name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO income (Name,Block,UnitNo,MaintenanceFee,Due)'
                ' VALUES (?, ?, ?, ?, ?)',
                (Name,Block,UnitNo,MaintenanceFee,Due)
                
            )
            db.commit()
            return redirect(url_for('views.index'))

    return render_template('create.html')    


@bp.route('/payment/<int:income_id>', methods=('GET', 'POST'))
def payment(income_id):

    db = get_db()
    query = "SELECT Due from income p where p.id = {}".format(income_id) 
    row = db.execute(query).fetchone()
    due = row[0]
    

    if request.method == 'POST':
        amount = int(request.form['amount'])
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO Payment (income_id,amount)'
                ' VALUES (?, ?)',
                (income_id, amount)
            )
            db.commit()

            due = due - amount

            db.execute(
                'UPDATE income SET due = ? '
                ' WHERE id = ?',
                ( due, income_id)
            )
            db.commit()
            
                

            return redirect(url_for('views.index'))
    
    return render_template('addpayment.html', due=due)  

@bp.route('/history/<int:income_id>')
def history(income_id):
    db=get_db()
    posts=db.execute(
            'SELECT p.id,amount,Pdate'
            ' FROM payment p'
            ' WHERE p.income_id={}'.format(income_id)
        ).fetchall()
    return render_template('history.html', posts=posts)


@bp.route('/vendor')
def vendor():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, Vname,cause,phone,fee'
        ' FROM expenses p'
         
    ).fetchall()
    return render_template('vendor.html', posts=posts)


@bp.route('/vcreate', methods=('GET', 'POST'))
def vcreate():
    if request.method == 'POST':
        Vname = request.form['Vname']
        cause = request.form['cause']
        phone = request.form['phone']
        fee = request.form['fee']
        error = None

        if not Vname:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO expenses (Vname,cause,phone,fee)'
                ' VALUES (?, ?, ?, ?)',
                (Vname,cause,phone,fee)
                
            )
            db.commit()
            return redirect(url_for('views.vendor'))

    return render_template('vcreate.html')    


@bp.route('/salary/<int:expense_id>', methods=('GET', 'POST'))
def salary(expense_id):

    db = get_db()
    query = "SELECT fee from expenses p where p.id = {}".format(expense_id) 
    row = db.execute(query).fetchone()
    due = row[0]
    

    if request.method == 'POST':
        amount = int(request.form['amount'])
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO salary (expense_id,amount)'
                ' VALUES (?, ?)',
                (expense_id, amount)
            )
            db.commit()

            due = due + amount

            db.execute(
                'UPDATE expenses SET fee = ? ,ispaid=0'
                ' WHERE id = ?',
                ( due, expense_id)
            )
            db.commit()
            
                

            return redirect(url_for('views.vendor'))
    
    return render_template('addpayment.html', due=due)  

@bp.route('/vhistory/<int:expense_id>')
def vhistory(expense_id):
    db=get_db()
    posts=db.execute(
            'SELECT p.id,amount,Pdate'
            ' FROM salary p'
            ' WHERE p.expense_id={}'.format(expense_id)
        ).fetchall()
    return render_template('history.html', posts=posts)


@bp.route('/vpaid')    
def vpaid():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, Vname,cause,phone,fee'
        ' FROM expenses p'
        ' WHERE ispaid=1'
         
    ).fetchall()
    return render_template('vpaid.html', posts=posts)

@bp.route('/vunpaid')     
def vunpaid():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, Vname,cause,phone,fee'
        ' FROM expenses p'
        ' WHERE ispaid=0 '
         
    ).fetchall()
    return render_template('vunpaid.html', posts=posts)

@bp.route('/paynow/<int:expense_id>')
def paynow(expense_id):
    db=get_db()
    posts=db.execute(
        'UPDATE expenses set ispaid=1'
        ' WHERE id={}'.format(expense_id)
        )
    db.commit()
    return redirect(url_for('views.vendor'))

@bp.route('/visitors')
def visitors():
    db=get_db()
    posts=db.execute(
        ' SELECT p.id, visname,category,phoneno,unitno,datein'
        ' FROM visitor p'
    ).fetchall()
    return render_template('visitors.html',posts=posts)

@bp.route('/visitoradd', methods=('GET', 'POST'))
def addvisitor():
    if request.method == 'POST':
        visname = request.form['visname']
        category = request.form['category']
        phoneno = request.form['phoneno']
        unitno = request.form['unitno']
        error = None

        if not visname:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO visitor (visname,category,phoneno,unitno)'
                ' VALUES (?, ?, ?, ?)',
                (visname,category,phoneno,unitno)
                
            )
            db.commit()
            return redirect(url_for('views.visitors'))

    return render_template('addvisitor.html')    

@bp.route('/visitormanage',methods=('GET','POST'))
def manage():
    if request.method == 'POST':
        startdate = request.form['startdate']
        enddate = request.form['enddate']
        error = None

        if not startdate:
            error = 'Date is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            posts=db.execute(
                ' SELECT p.id, visname,category,phoneno,unitno,datein'
                ' FROM visitor p'
                ' WHERE p.datein BETWEEN (?) AND (?)',
                (startdate,enddate)
                
            ).fetchall()
            return render_template('report.html',posts=posts,startdate=startdate,enddate=enddate)

    return render_template('manage.html')
    

