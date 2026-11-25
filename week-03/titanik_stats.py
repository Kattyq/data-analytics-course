import csv
import json
import math
import statistics

DATA_PATH = "week-03/train.csv"
RESULTS_PATH = "week-03/results.json"

# rows — список (list), внутри которого словари (dict)
# my_list = ["Анна", "Иван", "Мария"]
# my_list[2]  # "Мария" — третий элемент
# к словарю можно обратиться по ключу:
# my_dict = {"name": "Анна", "age": 25}
# 3. Как обращаться к словарю внутри списка
# people[1]["age"]   Возраст второго человека: 30

def load_data(path):
    # Задача 1: загрузка CSV
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Задача 2: перевод в числа и пропуски
    for passenger in rows:
        for column in ["Age", "Fare", "SibSp", "Parch", "Survived"]:
            try:
                passenger[column] = float(passenger[column])
            except (ValueError, TypeError):
                passenger[column] = None

    return rows

def mean(values):
    return sum(values) / len(values)

def median(values):
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2

def std(values):
    if len(values) < 2:
        raise ValueError("Нужно минимум два значения")

    m = mean(values)
    squared = [(x - m) ** 2 for x in values]
    return math.sqrt(sum(squared) / (len(values) - 1))

def missing_report(rows):
    report = {}
    for column in rows[0].keys():
        empty = sum(1 for row in rows if row[column] is None or row[column] == "")
        report[column] = empty
    return report

def group_by(rows, key):
    groups = {}
    for row in rows:
        k = row[key]
        if k not in groups:
            groups[k] = []
        groups[k].append(row)
    return groups

def survival_rate(rows):
    if not rows:
        return 0

    survived = sum(1 for r in rows if r["Survived"] == 1)
    return survived / len(rows)

def survival_by(rows, key):
    groups = {}
    groups = group_by(rows, key)

    result = {}

    for k, group_rows in sorted(groups.items()):
        result[k] = {
            "count": len(group_rows),
            "survived": sum(1 for r in group_rows if r["Survived"] == 1),
            "rate": round(survival_rate(group_rows), 3),
        }

    return result

def survival_by_two(rows, key1, key2):
    groups = {}
    for row in rows:
        k = (row[key1], row[key2])
        groups.setdefault(k, []).append(row)
    result = {}
    for k in sorted(groups):
        result[k] = round(survival_rate(groups[k]), 3)
    return result

def age_group(age):
    if age is None:
        return "unknown"
    if age < 18:
        return "0-17"
    if age < 35:
        return "18-34"
    if age < 60:
        return "35-59"
    return "60+"

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    rows = load_data(DATA_PATH)

    print("Всего пассажиров:", len(rows))
    print("Первая строка:", rows[3])
    print("Возраст:", rows[3]["Age"])
    print("Тип возраста:", type(rows[3]["Age"]))

    # Задача 3: известный возраст и пропуски
    ages = [r["Age"] for r in rows if r["Age"] is not None]

    print(
        "Возраст известен у:", len(ages),
        "| пропусков:", len(rows) - len(ages)
    )

    # Задача 4: доля выживших
    survived = sum(1 for r in rows if r["Survived"] == 1)
    rate = survived / len(rows)

    print("Выживших:", survived)
    print(f"Доля выживших: {rate:.2%}")

    assert round(rate, 3) == 0.384

    # Задача 5: статистика по возрасту
    print(f"Возраст: среднее {mean(ages):.2f}, медиана {median(ages):.1f}, "
          f"std {std(ages):.2f}, мин {min(ages)}, макс {max(ages)}")
    assert math.isclose(mean(ages), statistics.mean(ages))
    assert median(ages) == statistics.median(ages)
    assert math.isclose(std(ages), statistics.stdev(ages))
    assert median([3, 1, 2]) == 2 and median([4, 1, 3, 2]) == 2.5

    # Задача 6: пропуски по столбцам
    report = missing_report(rows)
    print("Пропуски по столбцам:")
    for column, empty in report.items():
        if empty > 0:
            print(f"  {column}: {empty} ({empty / len(rows):.1%})")

    # Задача 7: выживаемость по классам
    by_class = survival_by(rows, "Pclass")
    print("Выживаемость по классу:")
    for pclass, stats in by_class.items():
        print(f"  {pclass} класс: {stats['survived']} из {stats['count']} = {stats['rate']:.1%}")
    assert sum(s["count"] for s in by_class.values()) == len(rows)
    
    # Задача 8: выживаемость по полу
    by_sex = survival_by(rows, "Sex")
    print("Выживаемость по полу:")
    for sex, stats in by_sex.items():
        print(f"  {sex}: {stats['survived']} из {stats['count']} = {stats['rate']:.1%}")
        
    # Задача 9: выживаемость по классу и полу
    by_class_sex = survival_by_two(rows, "Pclass", "Sex")
    print("Выживаемость по классу и полу:")
    for (pclass, sex), r in by_class_sex.items():
        print(f"  {pclass} | {sex:<6} | {r:.1%}")

    # Задача 10: выживаемость по возрастным группам
    for row in rows:
        row["AgeGroup"] = age_group(row["Age"])
    by_age = survival_by(rows, "AgeGroup")
    print("Выживаемость по возрастным группам:")
    for g, stats in by_age.items():
        print(f"  {g:<8} {stats['count']:>4} чел. {stats['rate']:.1%}")

    # Задача 11: сохранение результатов в JSON
    fares = [row["Fare"] for row in rows]
    results = {
        "rows": len(rows),
        "survival_rate": round(rate, 3),
        "age": {
            "known": len(ages),
            "mean": round(mean(ages), 2),
            "median": median(ages),
            "std": round(std(ages), 2),
        },
        "fare_median": median(fares),
        "missing": {c: n for c, n in report.items() if n > 0},
        "by_class": by_class,
        "by_sex": by_sex,
        "by_age_group": by_age,
    }
    save_json(results, RESULTS_PATH)
    loaded = load_json(RESULTS_PATH)
    assert loaded["survival_rate"] == 0.384
    print("Результаты сохранены в", RESULTS_PATH)

if __name__ == "__main__":
    main()
