import pandas as pd
import re
from typing import Tuple


# Задача 1
def filter_fsuir_students(data: pd.DataFrame) -> Tuple[int, int, pd.DataFrame]:
    """
    Создает подвыборку студентов факультета систем управления и робототехники (ФСУиР).
    Возвращает количество таких студентов, количество уникальных групп и отфильтрованный датасет.
    """
    data_fsuir = data[
        data["факультет"] == "факультет систем управления и робототехники"
        ].copy()
    fsuir_students_len = data_fsuir.shape[0]
    fsuir_groups_len = len(set(data_fsuir["группа"]))
    return (fsuir_students_len, fsuir_groups_len, data_fsuir)


# Задача 2
def find_homonymous_students(data_fsuir: pd.DataFrame) -> Tuple[bool, int, pd.Series, str]:
    """
    Проверяет наличие однофамильцев на ФСУиР, их количество, распределение по курсам
    и определяет группу с наибольшим числом однофамильцев.
    Возвращает:
     - логическое значение (наличие однофамильцев)
     - общее количество однофамильцев
     - серию с числом однофамильцев по курсам
     - группу с максимальным числом однофамильцев
    """
    data_fsuir["фамилия"] = data_fsuir["фио"].str.split().str[0]
    surname_counts_total = data_fsuir.groupby("фамилия").size()
    namesakes_total = surname_counts_total[surname_counts_total > 1].index
    data_namesakes_total = data_fsuir[data_fsuir["фамилия"].isin(namesakes_total)]
    num_namesakes_total = data_namesakes_total.shape[0]

    course_surname_counts = []
    for course in data_fsuir["курс"].unique():
        data_course = data_fsuir[data_fsuir["курс"] == course]
        surname_counts_course = data_course.groupby("фамилия").size()
        namesakes_course = surname_counts_course[surname_counts_course > 1].index
        data_namesakes_course = data_course[data_course["фамилия"].isin(namesakes_course)]
        course_surname_counts.append(
            {"курс": course, "количество_на_курсе": data_namesakes_course.shape[0]}
        )

    course_surname_counts_data = pd.DataFrame(course_surname_counts)
    course_surname_counts_data = course_surname_counts_data.sort_values(
        by="курс", key=lambda x: x.str.extract(r"(\d+)", expand=False).astype(int)
    )

    group_surname_counts = (
        data_namesakes_total.groupby("группа")
        .size()
        .reset_index(name="количество_в_группе")
    )
    max_group = group_surname_counts.loc[
        group_surname_counts["количество_в_группе"].idxmax()
    ]

    homonyms_per_course = {
        row["курс"]: row["количество_на_курсе"] for _, row in course_surname_counts_data.iterrows()
    }

    return (
        True,
        num_namesakes_total,
        pd.Series(homonyms_per_course),
        max_group["группа"],
    )


# Задача 3
def gender_identification(patronym: str) -> str:
    """
    Определяет пол по отчеству. Возвращает пол: female/male/unknown.
    """
    pass


def analyze_patronyms(data_fsuir: pd.DataFrame) -> Tuple[int, pd.Series]:
    """
    Определяет количество студентов без отчества и распределение студентов по полу на основе отчества.
    Возвращает:
     - количество студентов без отчества
     - серию с распределением студентов по полу 
    """
    data_fsuir["отчество"] = data_fsuir["фио"].str.split().str[2]
    data_fsuir["есть_отчество"] = data_fsuir["отчество"].notna()
    students_no_dad = data_fsuir[~data_fsuir["есть_отчество"]]
    num_students_no_dad = students_no_dad.shape[0]

    male_patronymic_pattern = r".*(?:ович|евич|ич)$"
    female_patronymic_pattern = r".*(?:овна|евна|ична|инична)$"

    data_fsuir["пол_по_отчеству"] = None
    data_fsuir.loc[
        data_fsuir["отчество"].str.contains(male_patronymic_pattern, na=False),
        "пол_по_отчеству",
    ] = "male"
    data_fsuir.loc[
        data_fsuir["отчество"].str.contains(female_patronymic_pattern, na=False),
        "пол_по_отчеству",
    ] = "female"
    num_male = data_fsuir[data_fsuir["пол_по_отчеству"] == "male"].shape[0]
    num_female = data_fsuir[data_fsuir["пол_по_отчеству"] == "female"].shape[0]
    gender_counts = {"male": num_male, "female": num_female}
    return (num_students_no_dad, pd.Series(gender_counts))


# Задача 4
def faculty_statistics(data: pd.DataFrame) -> Tuple[pd.DataFrame, Tuple[str, int], Tuple[str, int]]:
    """
    Подсчитывает количество студентов на каждом факультете,
    а также определяет факультеты с максимальным и минимальным числом студентов.
    """
    faculty_students_counts = []
    for faculty in data["факультет"].unique():
        data_faculty = data[data["факультет"] == faculty]
        data_students_faculty = data_faculty.groupby("факультет").size()
        faculty_students_counts.append(
            {"факультет": faculty, "количество": data_students_faculty.values[0]}
        )

    faculty_students_counts_data = pd.DataFrame(faculty_students_counts)

    max_faculty = faculty_students_counts_data.loc[
        faculty_students_counts_data["количество"].idxmax()
    ]
    min_faculty = faculty_students_counts_data.loc[
        faculty_students_counts_data["количество"].idxmin()
    ]
    return (faculty_students_counts_data, (max_faculty['факультет'], max_faculty['количество']), (min_faculty['факультет'], min_faculty['количество']))


# Задача 5
def course_statistics(data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Вычисляет среднее и медианное число студентов на каждом курсе.
    Возвращает две серии с результатами: сначала средние, потом медиана.
    """
    sorted = data.groupby("курс")["факультет"].value_counts()
    stats = sorted.groupby("курс").agg(["mean", "median"])
    return stats["mean"], stats["median"]


# Задача 6
def most_popular_name(data: pd.DataFrame) -> Tuple[str, str, str, int, float]:
    """
    Определяет самое популярное имя, группу с наибольшим количеством студентов с этим именем,
    факультет, курс и долю таких студентов в общем числе.
    Возвращает результат в следующем порядке:
     1. самое частое имя
     2. группа
     3. факультет
     4. доля
    """
    data["имя"] = data["фио"].str.split(" ").str[1]
    popular_name = data["имя"].value_counts().idxmax()

    name_group = data[data["имя"] == popular_name]["группа"].value_counts().idxmax()

    faculty = data[data["группа"] == name_group]["факультет"].iloc[0]

    course = data[data["группа"] == name_group]["курс"].iloc[0]

    num_copies_popular_name = data["имя"].value_counts().max()
    name_ratio = round(num_copies_popular_name / len(data), 2)
    return (popular_name, name_group, faculty, course, name_ratio)


# Задача 7
def find_students_with_name_starting_P(data: pd.DataFrame) -> pd.DataFrame:
    """
    Находит студентов, чье имя встречается ровно один раз и начинается на "П". Выводит их ФИО, факультет и курс.
    """
    data["имя"] = data["фио"].str.split(" ").str[1]
    starts_with_p = data[data["имя"].str.startswith("П")]
    name_counts = starts_with_p["имя"].value_counts()
    unique_names = name_counts[name_counts == 1].index
    result = starts_with_p[starts_with_p["имя"].isin(unique_names)]
    result = result[["фио", "факультет", "курс"]]
    return result


# Задача 8
def highest_avg_grade_faculty(data: pd.DataFrame) -> Tuple[str, str, int]:
    """
    Находит факультет, на котором средний балл студентов третьего курса самый высокий.
    Определяет пол, средний балл котого выше.
    Сначала возвращает факультет, затем пол, затем балл.
    """
    grade3 = data[data["курс"] == "3-й"].copy()
    avg_facs = []
    for faculty in grade3["факультет"].unique():
        data_fac = grade3[grade3["факультет"] == faculty]
        avg = data_fac["средний_балл"].mean()
        avg_facs.append({"факультет": faculty, "средний_балл": avg})

    avg_facs = pd.DataFrame(avg_facs).sort_values(by="средний_балл", ascending=False)
    fac = avg_facs.iloc[0]["факультет"]

    data_fac = grade3[grade3["факультет"] == fac].copy()
    data_fac["отчество"] = data_fac["фио"].str.split().str[2]
    male_patronymic_pattern = r".*(?:ович|евич|ич)$"
    female_patronymic_pattern = r".*(?:овна|евна|ична|инична)$"
    data_fac["пол_по_отчеству"] = None
    data_fac.loc[
        data_fac["отчество"].str.contains(male_patronymic_pattern, na=False),
        "пол_по_отчеству",
    ] = "male"
    data_fac.loc[
        data_fac["отчество"].str.contains(female_patronymic_pattern, na=False),
        "пол_по_отчеству",
    ] = "female"

    avg_gender = []
    for gender in data_fac["пол_по_отчеству"].unique():
        data_fac_gender = data_fac[data_fac["пол_по_отчеству"] == gender]
        avg = data_fac_gender["средний_балл"].mean()
        avg_gender.append({"пол": gender, "средний_балл": avg})
    avg_gender = pd.DataFrame(avg_gender).sort_values(
        by="средний_балл", ascending=False
    )
    best_gender = avg_gender.iloc[0]["пол"]
    best_grade = round(avg_gender.iloc[0]["средний_балл"])

    return (fac, best_gender, best_grade)


# Задача 9
def find_consecutive_students(data: pd.DataFrame) -> pd.DataFrame:
    """
    Находит первых 5 студентов, которым номера были присвоены подряд.
    Выводит их ФИО, факультет, курс и номер группы.
    """

    data = data.sort_values(by="ису", ascending=True)

    def find_sequence(start_isu, depth):
        if depth == 0:
            return []
        if (data["ису"] == start_isu).any():
            sequence = find_sequence(start_isu + 1, depth - 1)
            if sequence is not None:
                return [int(start_isu)] + sequence
        return None

    for i in range(len(data)):
        current_isu = data["ису"].iloc[i]
        sequence = find_sequence(current_isu, 5)
        if sequence:
            consecutive_students = data[data["ису"].isin(sequence)]
            return consecutive_students[
                ["фио", "ису", "факультет", "курс", "группа"]
            ].sort_values(by="ису")


if __name__ == "__main__":
    data = pd.read_csv("isu_fake_data.csv")
    # data["surname"] = "put your code here"
    # data["name"] = "put your code here"
    # data["patronim"] = "put your code here"

    # Задача 1
    num_students, num_groups, fsuir = filter_fsuir_students(data)
    print(f"Студентов на ФСУиР: {num_students}, Групп: {num_groups}")

    # Задача 2
    has_homonyms, total_homonyms, homonyms_per_course, max_homonym_group = find_homonymous_students(fsuir)
    print(f"Есть однофамильцы: {has_homonyms}, Всего: {total_homonyms}, Группа с максимумом: {max_homonym_group}")
    print(f"На каждом курсе: {homonyms_per_course}")

    # Задача 3
    students_without_patronym, gender_counts = analyze_patronyms(fsuir)
    print(f"Студентов без отчества: {students_without_patronym}")
    print("Распределение по полу:", gender_counts)

    # Задача 4
    faculty_counts, max_faculty, min_faculty = faculty_statistics(data)
    print(f"Факультет с наибольшим числом студентов: {max_faculty}")
    print(f"Факультет с наименьшим числом студентов: {min_faculty}")

    # Задача 5
    mean_students, median_students = course_statistics(data)
    print("Среднее число студентов на курсах:", mean_students)
    print("Медианное число студентов на курсах:", median_students)

    # Задача 6
    popular_name, name_group, faculty, course, name_ratio = most_popular_name(data)
    print(f"Самое популярное имя: {popular_name}, Группа: {name_group}, Факультет: {faculty}, Курс: {course}")
    print(f"Доля студентов с этим именем: {name_ratio}")

    # Задача 7
    result_7 = find_students_with_name_starting_P(data)
    print("Студенты с именем, начинающимся на П и встречающимся ровно один раз:")
    print(result_7)

    # Задача 8
    fac, best_gender, best_grade = highest_avg_grade_faculty(data)
    print(f"Факультет с высоким средним баллом 3-го курса: {fac}")
    print(f"Пол с наивысшим средним баллом: {best_gender}, Средний балл: {best_grade}")

    # Задача 9
    result_9 = find_consecutive_students(data)
    print("Первые 5 студентов с подряд идущими табельными номерами:")
    print(result_9)
