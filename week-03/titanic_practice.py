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

if __name__ == "__main__":
    main()
