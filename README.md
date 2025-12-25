
# Test Project For practise

This is project built FASTAPI

Project running [standart docker orders]

```docker compose up -d --build```

Seeing logs

```docker compose logs```

```docker compose logs web```

.....


APIES
Authentication(JWT)(6), Fake NLP Parser(2), Events(CRUD)(4)

Wevsocket

client ---> Server (prompt)

client <--- Server (parse(prompt)=draft(json))

client ---> Server(client:Accept-->{draft-->EventCreate-->EventInvites--->Alarm})




<img width="1232" height="962" alt="Screenshot 2025-12-26 at 04 57 36" src="https://github.com/user-attachments/assets/67a58733-737a-4f5c-ae1f-054b1b1a09df" />

1)modellar yozildi

2)http apilar to'liq 
chiqdi(users,events, JWT)

3)client-server websocket logikasi to'liq bitdi

4)LLM ishlamadi torchni m1,m2 chipli kompyuterlar o'qirkan meniki macos lekin core7.
O'rniga fake_parser funksiya qo'shdim o'rni bilinmasligi uchun.
5)broker sifatida rabbitMQ 

6)UMUMAN bitmaganlar:
a)ALARM 
rrule(celery beat ishlatdim ammo buni task sifatida qo'shishga ulgurmadim)

b)Invite (emaillarga tasdiqlovchi notifylar yuborish) ulgurmadim(qila olaman) (celery taskka tashladi )

c)draft tasdiqlangach Event yaratilishi buni yozganman ammo xatosi bor.Shunga koment qilib qo'ydim.

d)Front(react) --umuman bilmayman.Testlab ber desangiz websocketni backendda bemalol testlab beraman.

e)AuditLog ham qo'shib ketishga ulgurmadim





