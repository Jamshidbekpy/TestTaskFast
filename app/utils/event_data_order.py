
# data

# {
#     'original_text': 'eccef', 
#     'success': True, 
#     'client_id': 'cd9040b3-041b-4e27-8b60-439703a99259',
#     'timestamp': '2025-12-25T21:09:53.553943',
#     'type': 'parsed_result', 'requires_confirmation': True,
#     'message_id': 'msg_1766696993_37d54826',
#     'intent': 'create', 
#     'language': 'ru', 
#     'confidence': '0.65', 
#     'title': 'Muhokama sessiyasi', 
#     'time_start': '2025-12-25 00:00:00', 
#     'time_end': '2025-12-26 00:00:00', 
#     'all_day': 'True', 
#     'repeat': 'None', 
#     'invites': "['jamshidbekshodibekov2004@gmail.com']", 
#     'alerts': "['P1D']", 
#     'url': 'None', 
#     'note': 'None', 
#     'warnings': '[]', 
#     'confirmation_question': "'Muhokama sessiyasi' tadbirini yaratishni tasdiqlaysizmi? (Ha/Yo'q)"
#     }

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

# eventinvites = invites.copy()
# eventalarm = alerts.copy()

def event_data_order(data)-> list:
    
    eventdata = {
        'client_id': data['client_id'],
        'title': data['title'], 
        'all_day': data['all_day'],
        'time_start': data['time_start'],  
        'time_end': data['time_end'], 
        'repeat': data['repeat'], 
        'url': data['url'], 
        'note': data['note'] 
    }
    
    eventinvites = data['invites'].copy()
    eventalarms = data['alerts'].copy()
    
    return [eventdata, eventinvites, eventalarms]