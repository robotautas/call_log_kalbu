from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from secret import api_key
import uuid
# from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:example@127.0.0.1:5432/kalbu"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class CallLog(db.Model):
    __tablename__ = "CallLog"
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    call_start_time = db.Column("CallStartTime", db.DateTime)
    call_end_time = db.Column("CallEndTime", db.DateTime)
    direction = db.Column("Direction", db.String(8))
    caller_id = db.Column("CallerID", db.String(11))
    extension = db.Column("Extension", db.String(3))
    dialed_number = db.Column("DialedNumber", db.String(11))
    destination_number = db.Column("DestinationNumber", db.String(11))
    duration = db.Column("Duration", db.Integer)
    bill_sec = db.Column("Billsec", db.Integer)
    answer_state = db.Column("AnswerState", db.String(12))
    extensions = relationship("Extension")

    def __repr__(self):
        return f"{self.id} - {self.extension}"


# Forwarded calls are stored as child objects 
class Extension(db.Model):
    __tablename__ = "Extension"
    id = db.Column(db.Integer, primary_key=True)
    call_start_time = db.Column("CallStartTime", db.DateTime)
    extension = db.Column("Extension", db.String(3))
    call_id = db.Column(UUID(as_uuid=True), db.ForeignKey("CallLog.id"))


@app.route("/", methods=["POST"])
def log_call():
    # simple api-key authorization
    auth = request.headers.get("Api-Key")
    if auth != api_key:
        return "", 401
    
    try:
        body = request.get_json()
    except Exception as e:
        return "", 400

    call = CallLog.query.filter_by(id=body["UUID"]).first()

    if len(body) == 4:
        # Call forward case
        if call:
            extension = Extension(
                call_start_time=datetime.fromtimestamp(int(body["CallStartTime"])),
                extension=body["Extension"],
            )
            call.extensions.append(extension)
            db.session.commit()
            return "", 200
        
        # Call start case
        else:
            call = CallLog(
                id=body["UUID"],
                call_start_time=datetime.fromtimestamp(int(body["CallStartTime"])),
                caller_id=body["CallerID"],
                extension=body["Extension"]
            )
            db.session.add(call)
            db.session.commit()
            return "", 200
    
    # Call end case. Call start row must exist already, otherwise responds with 400.
    elif call and len(body) == 10:
        call.call_end_time = datetime.fromtimestamp(int(body["CallEndTime"]))
        call.direction = body["Direction"]
        call.dialed_number = body["DialedNumber"]
        call.destination_number = body["DestinationNumber"]
        call.duration = body["Duration"]
        call.bill_sec = body["Billsec"]
        call.answer_state = body["AnswerState"]
        db.session.commit()
        return "", 200
    else:
        return "", 400




if __name__ == '__main__':
    if not db.get_tables_for_bind():
        db.create_all()
    app.run(debug=True)





