from datetime import datetime


def log(source, message, level="info"):
    msg = f"[{str(source)}] - {str(message)}"
    print("({0}){1}".format(datetime.now().strftime("%m/%d %H:%M:%S"), msg))
