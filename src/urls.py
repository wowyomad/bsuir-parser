#URLs used for making HTTPS requests

BASE_URL = "https://iis.bsuir.by/api/v1/"
def schedule(group_number):
    return f'{BASE_URL}schedule?studentGroup={group_number}'
