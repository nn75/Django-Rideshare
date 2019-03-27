import datetime


def datestrFormat(date_in):
    date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
    date_processing = [int(v) for v in date_processing]
    date_out = datetime.datetime(*date_processing)
    return date_out