import requests
import json
import os
import urls
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
data_dir = project_dir / "data"
if not data_dir.exists():
    data_dir.mkdir()

schedule_raw_url = urls.schedule(124402)
schedule_raw_path = data_dir / "schedule_raw.json"
schedule_parsed_path = data_dir / "schedule_parsed.json"


groupNumber = 124402
day_order = {
    "Понедельник": 1,
    "Вторник": 2,
    "Среда": 3,
    "Четверг": 4,
    "Пятница": 5,
    "Суббота": 6
}

subjects_with_queues = (
    "ММДТТ",
    "СТРWeb",
    "ТВиА",
    "СиТАиРИС",
    "ПМИС",
    "ПрогСП"
)



def get_and_parse_schedule(update_schedule=True):
    parsed_schedule = None
    try:
        if update_schedule:
            raw_schedule = get_schedule_raw(update_schedule=update_schedule)
            parsed_schedule = get_schedule_parsed(schedule_raw=raw_schedule)
        else:
            if os.path.exists(schedule_parsed_path) and os.path.getsize(schedule_parsed_path) > 0:
                with open(schedule_parsed_path, 'r', encoding='utf-8') as parsed_file:
                    parsed_schedule = json.load(parsed_file)
            else:
                if os.path.exists(schedule_raw_path) and os.path.getsize(schedule_raw_path) > 0:
                    parsed_schedule = get_schedule_raw(update_schedule=False)
                else:
                    parsed_schedule = get_schedule_raw(update_schedule=update_schedule)
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")
    finally:
        return parsed_schedule


def get_schedule_raw(update_schedule=True):
    schedule_raw = None
    try:
        if update_schedule:
            response = requests.get(schedule_raw_url)

            if response.status_code == 200:
                schedule_raw = response.json()

                with open(schedule_raw_path, 'w', encoding='utf-8') as raw_file:
                    json.dump(schedule_raw, raw_file, indent=4, ensure_ascii=False)
            else:
                raise Exception(f"Failed to retrieve {schedule_raw_path}. Status code: {response.status_code}")
        else:
            if os.path.exists(schedule_raw_path) and os.path.getsize(schedule_raw_path) > 0:
                with open(schedule_raw_path, 'r', encoding='utf-8') as raw_file:
                    schedule_raw = raw_file.read()
            else:
                raise Exception(f"{schedule_raw_path} file does not exist or is empty. Use update=True to update the schedule.")

    except Exception as e:
        raise Exception(f"An error occurred while getting raw schedule data: {str(e)}")
    finally:
        return schedule_raw


def get_schedule_parsed(schedule_raw):
    if not schedule_raw:
        return None
    sorted_days = sorted(schedule_raw["schedules"].keys(), key=lambda x: day_order[x])
    parsed = {1: {}, 2: {}, 3: {}, 4: {}}
    for day in sorted_days:
        lessons = schedule_raw["schedules"][day]
        for lesson in lessons:
            for week_num in lesson["weekNumber"]:
                if day not in parsed[week_num]:
                    parsed[week_num][day] = []
                parsed[week_num][day].append({
                    "subject": lesson["subject"],
                    "lessonTypeAbbrev": lesson["lessonTypeAbbrev"],
                    "subjectFullName": lesson["subjectFullName"],
                    "startLessonTime": lesson["startLessonTime"],
                    "endLessonTime": lesson["endLessonTime"],
                    "numSubgroup": lesson["numSubgroup"]
                })
    with open(schedule_parsed_path, 'w', encoding='utf-8') as parsed_file:
        json.dump(parsed, parsed_file, ensure_ascii=False, indent=4)
    return parsed


if __name__ == '__main__':
    schedule = get_and_parse_schedule(update_schedule=False)

    for week_num, week_schedule in schedule.items():
        print(f"Неделя {week_num}")
        for day, subjects in week_schedule.items():
            print(day)
            for subject in subjects:
                print('\t', end='')
                print(f'{subject["startLessonTime"]}-{subject["endLessonTime"]}: {subject["lessonTypeAbbrev"]} {subject["numSubgroup"]} {subject["subject"]}')
