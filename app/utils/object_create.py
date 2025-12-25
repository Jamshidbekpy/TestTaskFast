# eventdata = {
#     'client_id' = 'cd9040b3-041b-4e27-8b60-439703a99259',
#     'title': 'Muhokama sessiyasi', 
#     'all_day': 'True',
#     'time_start': '2025-12-25 00:00:00',  
#     'time_end': '2025-12-26 00:00:00', 
#     'repeat': 'None', 
#     'url': 'None', 
#     'note': 'None' 
#}


from sqlalchemy.orm import Session
from ..models import Event
from datetime import datetime
import uuid

def create_event(eventdata: dict, db: Session = None):
    """
    Database'ga event yaratish
    """
    try:
        event = Event(
            id=uuid.uuid4(),  
            user_id=uuid.UUID(eventdata['client_id']), 
            title=eventdata['title'],
            all_day=bool(eventdata['all_day']), 
            time_start=datetime.fromisoformat(eventdata['time_start'].replace(' ', 'T')) if eventdata['time_start'] != 'None' else None,
            time_end=datetime.fromisoformat(eventdata['time_end'].replace(' ', 'T')) if eventdata['time_end'] != 'None' else None,
            repeat=eventdata['repeat'] if eventdata['repeat'] != 'None' else None,
            url=eventdata['url'] if eventdata['url'] != 'None' else None,
            note=eventdata['note'] if eventdata['note'] != 'None' else None
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        print(f" Event created: {event.id}")
        return event
        
    except Exception as e:
        db.rollback()  # Xatolikda rollback
        print(f"Error creating event: {e}")
        raise
    
    
# def create_event_invites(db: Session, eventinvites: list):
#     """
#     Database'ga event invites yaratish
#     """
#     try:
#         eventinvites = [EventInvite(**invite) for invite in eventinvites]
#         db.bulk_save_objects(eventinvites)
#         db.commit()
#     except Exception as e:
#         db.rollback()  # Xatolikda rollback
#         print(f"Error creating event invites: {e}")
#         raise
    