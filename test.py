import schedule
stroka = "1"

def line():
    print(stroka)


while True:
    schedule.run_pending()
    stroka = "2"