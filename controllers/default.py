# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])

def getEditDisplay(row):
    database = db().select(db.info.ALL)
   # my_email = database[row.id].user_email
   # print my_email
    edit_button = ''
    print row.id
    if database[row.id - 1].user_email == auth.user.email:
        edit_button =A('Edit', _class='button btn btn-default', _href=URL("default", "edit", args=[row.id]))

    return edit_button

@auth.requires_login()
def index():
    q = db.info
    export_classes = dict(csv=False, json=False, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    links = [lambda row: getEditDisplay(row)]
    selectable = lambda ids: delete(ids)
    form = SQLFORM.grid(
        q,
        editable=False,
        links=links,
        create=True,
        selectable=selectable,
        user_signature=False,
        deletable=False,
        fields=[db.info.user_email, db.info.skills, db.info.available_times,
                ],
        details=True,
        exportclasses=export_classes
    )
    # my_extra_element = TR(LABEL("Don't view"),
    #                       INPUT(_name='Unviewable', value=False, _type='checkbox'))
    # form[1].insert(0, my_extra_element)
    # row = db().select(db.info.ALL)
    # if 'edit' in request.args:
    #     if auth.user.email == row[0].user_email:
    #         response.flash = T("emails are the same")
    return dict(form=form)

@auth.requires_login()
def delete(ids):
    row = db().select(db.info.ALL)
    if row[0].user_email == auth.user.email:
        to_delete = db(db.info.id.belongs(ids))
        to_delete.delete()



@auth.requires_login()
def edit():
    if request.args(0) is None:
        form = SQLFORM(db.info)
    else:
        # A checklist is specified.  We need to check that it exists, and that the user is the author.
        # We use .first() to get either the first element or None, rather than an iterator.
        q = ((db.info.user_email == auth.user.email) &
             (db.info.id == request.args(0)))
        cl = db(q).select().first()
        if cl is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'index'))
        # Always write invariants in your code.
        # Here, the invariant is that the checklist is known to exist.
        form = SQLFORM(db.info, record=cl, deletable=True, readonly=False)

    # Adds some buttons.  Yes, this is essentially glorified GOTO logic.
    button_list = []

    button_list.append(A('Cancel', _class='btn btn-warning',
                          _href=URL('default', 'index')))

    if form.process().accepted:
        # At this point, the record has already been inserted.
        session.flash = T('Checklist edited.')
        redirect(URL('default', 'index'))
    elif form.errors:
        session.flash = T('Please enter correct values.')
    return dict(form=form, button_list=button_list)

def submit():
    t_id = db(db.info.user_email == auth.user.email).update(
        skills = request.vars.skills,
        available_times = request.vars.available_times
    )
    t = db.info(request.vars.info_id)
    return response.json(dict(info=t))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    if request.args(0) == 'profile':
        db.auth_user.first_name.writable = db.auth_user.last_name.writable = db.auth_user.email.writable = False
        for field in auth.settings.extra_fields['auth_user']:
            field.readable = True
            field.writable = False
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


