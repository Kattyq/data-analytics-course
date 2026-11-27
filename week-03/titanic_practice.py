import json
from titanic_stats import load_data, survival_by, mean, median, survival_rate

DATA_PATH = "week-03/train.csv"


def family_group(size):
    if size == 1:
        return "alone"
    return "with_family"


def rate_where(rows, condition):
    selected = [r for r in rows if condition(r)]
    return len(selected), survival_rate(selected)


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

    # Задание 4: титул из имени
    # значительно больше выжили мальчики по сравнению с взрослыми мужчинами, и значительно больше выжили женщины, но с небольшим отрывом замужние женщины
    for row in rows:
        row["Title"] = row["Name"].split(", ")[1].split(".")[0].strip()
    main_titles = ["Mr", "Miss", "Mrs", "Master"]
    for row in rows:
        if row["Title"] not in main_titles:
            row["Title"] = "Rare"
    by_title = survival_by(rows, "Title")
    print("Выживаемость по титулам:")
    for title, stats in sorted(by_title.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"  {title}: {stats['count']} чел., {stats['rate']:.1%}")
    assert len(by_title) == 5

    # Задание 5: топ-5 самых дорогих билетов
    top5 = sorted(rows, key=lambda r: r["Fare"], reverse=True)[:5]
    print("Топ-5 дорогих билетов:")

    for r in top5:
        if r["Survived"] == 1:
            status = "Выжил"
        else:
            status = "Не выжил"
        print(
            f"  {r['Name']} ({r['Pclass']} класс): {r['Fare']:.2f} | {status}")
        assert round(top5[0]["Fare"], 2) == 512.33

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

    # Задание 8: дети до 10 лет
    # выживаемость детей конечно выше, но не абсолютная, и взрослых намного больше чем детей было
    n, rate = rate_where(
        rows, lambda r: r["Age"] is not None and r["Age"] < 10)
    print(f"Дети до 10 лет: {n} чел., выжили {rate:.1%}")
    assert n > 0 and 0 <= rate <= 1
    
    n_adult, rate_adult = rate_where(
        rows, lambda r: r["Age"] is not None and r["Age"] >= 18)
    print(f"Взрослые от 18ти лет: {n_adult} чел., выжили {rate_adult:.1%}")

    # Гипотеза: почему в Шербуре выживали чаще?
    # Гипотеза: доля 1 класса по портам
    # выживаемость в порту Шербура объясняется большим наличием наличием пассажирова 1ого класса, чем тем, что там больше женщин
    print("Доля 1ого класса по портам:")
    for port in ["C", "S", "Q"]:
        port_rows = [r for r in rows if r["Embarked"] == port]
        first = [r for r in port_rows if r["Pclass"] == "1"]
        women = [r for r in port_rows if r["Sex"] == "female"]
        share = len(first) / len(port_rows)
        share_w = len(women) / len(port_rows)
        print(f"  {port}: {len(port_rows)} чел., 1 класс {share:.1%}, женщин {share_w:.1%}")

    # когда нужно вывести value по значению
    # for row in rows:
    #     if row["Name"] == "Fortune, Mr. Charles Alexander":
    #         print(row)


if __name__ == "__main__":
    main()
