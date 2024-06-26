from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, fields, marshal_with

from json import dumps
from httplib2 import Http
from custom_error import DataError, LogicError
from model import Secondary_Tag, Subject_Tag, Table_likes, Ticket, User, Priority, db

class Ticket_api(Resource):
    '''API code for Ticket Manager'''

    ticket_output = {
        "ticket_id": fields.Integer,
        "title": fields.String,
        "description": fields.String,
        "subject_name": fields.String(attribute=lambda x: Subject_Tag.query.filter_by(subject_id=x.subject_id).first().subject_name),
        "sec_name": fields.String(attribute=lambda x: Secondary_Tag.query.filter_by(sec_tag_id=x.sec_id).first().sec_tag_name),
        "isFAQ": fields.Boolean,
        "ticket_status": fields.String,
        "likes": fields.Integer(attribute=lambda x: len(x.likes))
    }

    @jwt_required()
    @marshal_with(ticket_output)
    def get(self, subject_name: str):

        # extracts all the query parameters from the endpoint and converts it into a dictionary
        params = request.args.to_dict()
        keyword = ""
        limit = 0
        # using the params dictionary we add keys and values to the filter_dict dictionary
        # and initialize the values
        obj = Subject_Tag.query.filter_by(subject_name=subject_name).first()
        filter_dict = {'subject_id': obj.subject_id}
        if obj is None:
            raise LogicError(status_code=404, error_code="TICKET006",
                             error_msg="invalid subject")
        for key in params.keys():
            if key == 'FAQ':
                if params[key].lower() == 'true':
                    filter_dict['isFAQ'] = bool(1)
                else:
                    filter_dict['isFAQ'] = bool(0)
            elif key == 'limit':
                limit = int(params[key])
            elif key == 'ResolvedStatus':
                if params[key].lower() == 'false':
                    filter_dict['ticket_status'] = 'unresolved'
                else:
                    filter_dict['ticket_status'] = 'resolved'
            elif key == 'TagName':
                filter_dict['sec_id'] = Secondary_Tag.query.filter_by(
                    sec_tag_name=params[key]).first().sec_tag_id
            elif key == 'search':
                keyword = params[key]

        # Used Inner join for two queries
        if limit > 0:
            subq = Ticket.query.filter_by(
                **filter_dict).limit(limit).subquery()
            que = Ticket.query.filter(Ticket.title.contains(keyword))\
                .join(subq, Ticket.ticket_id == subq.c.ticket_id).all()
        else:
            subq = Ticket.query.filter_by(**filter_dict).subquery()
            que = Ticket.query.filter(Ticket.title.contains(keyword))\
                .join(subq, Ticket.ticket_id == subq.c.ticket_id).all()
        return que, 200

    @jwt_required()
    @marshal_with(ticket_output)
    def put(self, ticket_id: int):
        '''Modifies the ticket details'''
        ticket_obj = Ticket.query.filter_by(ticket_id=ticket_id).first()
        if not ticket_obj:
            return DataError(status_code=404)

        form = request.get_json()

        # Checking action from form data
        if form.get("action") is None or form.get("user_id") is None:
            raise LogicError(status_code=400, error_code="TICKET001",
                             error_msg="Either user_id or action type is missing")

        user_id = form.get("user_id")

        user = User.query.filter_by(user_id=user_id).first()
        # Changes in database based on action variable from form
        if form.get("action") == 'faq' or form.get("action") == 'notfaq':
            if user.role == 'student':
                raise LogicError(status_code=400, error_code="TICKET005",
                                 error_msg="A student cannot mark/unmark the ticket as FAQ")
            if form.get("action") == 'faq':
                if ticket_obj.ticket_status == "resolved":
                    ticket_obj.isFAQ = True
                elif ticket_obj.ticket_status == "unresolved":
                    raise LogicError(status_code=400, error_code="TICKET002",
                                     error_msg="Ticket need to be resolved before marking as FAQ")
            elif form.get("action") == 'notfaq':
                ticket_obj.isFAQ = False

        elif form.get("action") == 'like':
            for like in ticket_obj.likes:
                if like.user_id == user_id:
                    db.session.delete(like)
                    break
            else:
                obj = Table_likes(
                    ticket_id=ticket_obj.ticket_id, user_id=user_id)
                db.session.add(obj)

        elif form.get("action") == 'set_priority':  # Handling priority update
            if user.role == 'admin':
                priority = form.get("priority")
                if priority not in ['Low', 'High']:
                    raise LogicError(status_code=400, error_code="TICKET007",
                                     error_msg="Priority should be 'Low' or 'High'")
                priority_entry = Priority.query.filter_by(ticket_id=ticket_id, user_id=user_id).first()
                if not priority_entry:
                    priority_entry = Priority(ticket_id=ticket_id, user_id=user_id, priority=priority)
                    db.session.add(priority_entry)
                else:
                    priority_entry.priority = priority

        db.session.commit()
        return ticket_obj, 200

        
    @jwt_required()
    @marshal_with(ticket_output)
    def post(self, subject_name: str):
        '''Creates a new ticket for a subject'''

        subject_obj = Subject_Tag.query.filter_by(
            subject_name=subject_name).first()
        if subject_obj is None:
            raise DataError(status_code=404)

        # Getting form data
        form = request.get_json()
        title = form.get("title")
        desc = form.get("description")
        sec = form.get("secondary_tag")
        priority = form.get("priority")  # New addition

        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        user_id = user.user_id
        form_data = [title, desc, sec, user_id, priority]  # Updated form_data

        # Checking if all the form data is filled up
        if None in form_data:
            raise LogicError(status_code=400, error_code="TICKET003",
                            error_msg="Some data required for creating ticket is missing")

        tickets = Ticket.query.filter_by(
            subject_id=subject_obj.subject_id).all()

        # Checking for duplicate titles
        for ticket in tickets:
            if ticket.title.lower() == title.lower():
                raise DataError(status_code=409)

        # Checking if secondary tag is present in Secondary Tag class
        sec_obj = Secondary_Tag.query.filter_by(sec_tag_name=sec).first()
        if sec_obj is None:
            raise LogicError(status_code=400, error_code="TICKET004",
                            error_msg="Secondary tag entered is not available")

        # Creating ticket obj and committing to database
        ticket_obj = Ticket(user_id=user_id, title=title,
                            description=desc, subject_id=subject_obj.subject_id,
                            sec_id=sec_obj.sec_tag_id)

        db.session.add(ticket_obj)
        tid = Ticket.query.filter_by(title=title).first().ticket_id
        t_title = Ticket.query.filter_by(title=title).first().title
        t_desc = Ticket.query.filter_by(title=title).first().description
        t_sub = Ticket.query.filter_by(title=title).first().subject_id

        # Handling priority entry
        if priority:
            priority_entry = Priority(ticket_id=tid, user_id=user_id, priority=priority)
            db.session.add(priority_entry)

        db.session.commit()

        if priority == 'High':
            try:
                """Google Chat incoming webhook quickstart."""
                url = "https://chat.googleapis.com/v1/spaces/AAAAezKpJMw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=ksyvz2gwBbjKzzOqBeDR0phzYx-xAoJ9vokPMKa1xS4"
                app_message = {"text": "Ticket with title: " + t_title + " and subject: " + str(t_sub) + " has been created with high priority. Description: " + t_desc}
                print(app_message)
                message_headers = {"Content-Type": "application/json; charset=UTF-8"}
                http_obj = Http()
                response = http_obj.request(
                uri=url,
                method="POST",
                headers=message_headers,
                body=dumps(app_message))
                print('Reminder sent successfully')
            except Exception as e:
                print('Error sending reminder:', str(e))
                

        return ticket_obj, 201