import arrow

def humanize_arrow_date(date):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case.
    """
    try:
        then = arrow.get(date)
        now = arrow.utcnow()
        now = now.replace(hour=0, minute=0, second=0)
        if then.date() == now.date():
            human = "Today"
        else:
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
            elif human == "a day ago":
                human = "Yesterday"
    except:
        human = date
    return human

def name():
    print("My Name: ", __name__)
    return __name__