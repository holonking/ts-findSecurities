import datetime

today=datetime.date.today()
for j in range (10):
	if j==2: continue
	delta=datetime.timedelta(days=j)
	xday=today-delta
	print(str(j)+ " - "+ str(xday) )

