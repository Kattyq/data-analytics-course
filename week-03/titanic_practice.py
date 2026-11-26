import json
from titanic_stats import load_data, survival_by, mean, median

DATA_PATH = "week-03/train.csv"


def family_group(size):
    if size == 1:
        return "alone"
    return "with_family"


def main():
    rows = load_data(DATA_PATH)
    print("Всего пассажиров:", len(rows))

    for row in rows:
        if row["Embarked"] == "":
            row["Embarked"] = "Unknown"
    by_port = survival_by(rows, "Embarked")

    # задание 1: Выживаемость по порту посадки
    # В Шербуре выживаемость выше всего (55%). Гипотеза: там село больше пассажиров 1 класса и женщин, надо проверить

    assert by_port['C']["count"] == 168
    # print(by_port) - это обычный вариант в Python, но в нашем случае он не очень удобен, потому что словарь большой и не очень читаемый. Поэтому мы выводим его построчно:
    print("Выживаемость по порту:")
    for port, stats in by_port.items():
        print(
            f"  {port}: {stats['survived']} из {stats['count']} = {stats['rate']:.2%}")

    # Задание 2: Стоимость билета по классам
    # среднее и медиана так отличаются потому что кто-то покупал очень дорогие билеты
    print("Стоимость билета по классам:")
    for pclass in ["1", "2", "3"]:
        fares = [row["Fare"] for row in rows if row["Pclass"] == pclass]
        # print(pclass, len(fares), fares[:3])
        print(
            f"  {pclass} класс: среднее {mean(fares):.2f}, медиана {median(fares):.2f}")
        if pclass == "1":
            assert round(mean(fares), 2) == 84.15

    # Задание 3: одиночки против семей
    for row in rows:
        row["FamilySize"] = row["SibSp"] + row["Parch"] + 1
        row["FamilyGroup"] = family_group(row["FamilySize"])
    by_family = survival_by(rows, "FamilyGroup")

    print("Выживаемость одиночек против семей:")
    for group, stats in by_family.items():
        print(
            f"  {group}: {stats['survived']} из {stats['count']} "
            f"= {stats['rate']:.2%}"
        )

    # Задание 6. Медианный возраст по классам
    # более взрослые люди могли позволить себе более дорогие билеты
    print("Медианный возраст по классам:")
    for pclass in ["1", "2", "3"]:
        ages = [row["Age"] for row in rows if row["Pclass"]
                == pclass and row["Age"] is not None]
        print(f"  {pclass} класс: медиана {median(ages):.1f} лет")
        if pclass == "1":
            assert median(ages) == 37.0

    # Задание 7: выживаемость класс × пол
    # категория пола влияла больше на выживаемость, и при этом женщины и мужчины тем не менее в более дорогих классах выживали лучше
    for row in rows:
        row["class_sex"] = f"{row['Pclass']}_{row['Sex']}"
    by_class_sex = survival_by(rows, "class_sex")
    print("Выживаемость по классу и полу:")
    for group, stats in sorted(by_class_sex.items()):
        print(f"  {group}: {stats['rate']:.1%}")
        assert by_class_sex["1_female"]['rate'] == 0.968

    with open("week-03/class_sex.json", "w", encoding="utf-8") as f:
        json.dump(by_class_sex, f, ensure_ascii=False, indent=2)
        print("Сохранено в week-03/class_sex.json")

if __name__ == "__main__":
    main()
