import os
import csv
from datetime import datetime
from collections.abc import Iterator

# Ветка feature-filter: добавлен новый функционал
# ============================================================
# 1. ОСНОВНОЙ КЛАСС с итератором
# ============================================================

class TrafficLightRecord:
    """Класс для хранения одной записи о работе светофора"""

    # Статический счётчик для всех записей
    _total_records = 0

    def __init__(self, record_id, start_datetime, end_datetime, cars_passed, cars_waiting):
        # Используем __setattr__ для установки значений
        self._validate_datetime(start_datetime, "дата и время включения БАРАБАН")
        self._validate_datetime(end_datetime, "дата и время выключения")
        self._validate_positive_int(cars_passed, "количество проехавших автомобилей")
        self._validate_positive_int(cars_waiting, "количество автомобилей в ожидании")

        self.__setattr__('_id', record_id)
        self.__setattr__('_start_datetime', start_datetime)
        self.__setattr__('_end_datetime', end_datetime)
        self.__setattr__('_cars_passed', cars_passed)
        self.__setattr__('_cars_waiting', cars_waiting)

        TrafficLightRecord._total_records += 1

    # 3. ВАЛИДАЦИЯ через статические методы
    @staticmethod
    def _validate_datetime(dt_str, field_name):
        """Статический метод для проверки формата даты/времени"""
        try:
            datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Неверный формат {field_name}. Используйте YYYY-MM-DD HH:MM:SS")

    @staticmethod
    def _validate_positive_int(value, field_name):
        """Статический метод для проверки положительного целого числа"""
        if value < 0:
            raise ValueError(f"{field_name} не может быть отрицательным")

    # 4. ПЕРЕГРУЗКА __setattr__ (запись только через него)
    def __setattr__(self, name, value):
        """Контроль установки значений свойств"""
        if name.startswith('_'):
            # Внутренние атрибуты можно устанавливать
            super().__setattr__(name, value)
        else:
            # Публичные атрибуты запрещаем - только через методы
            raise AttributeError(f"Изменение атрибута {name} запрещено. Используйте методы класса.")

    # 7. ГЕНЕРАТОР длительности работы
    def duration_generator(self):
        """Генератор, возвращающий длительность работы светофора в минутах"""
        start = datetime.strptime(self._start_datetime, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(self._end_datetime, "%Y-%m-%d %H:%M:%S")
        duration_minutes = int((end - start).total_seconds() / 60)

        for minute in range(1, duration_minutes + 1):
            yield minute

    # 5. ПЕРЕГРУЗКА repr
    def __repr__(self):
        return (f"TrafficLightRecord(id={self._id}, start='{self._start_datetime}', "
                f"end='{self._end_datetime}', passed={self._cars_passed}, waiting={self._cars_waiting})")

    def __str__(self):
        return (f"№{self._id}: {self._start_datetime} → {self._end_datetime} | "
                f"Проехало: {self._cars_passed} | В очереди: {self._cars_waiting}")

    # Геттеры для доступа к данным
    @property
    def id(self):
        return self._id

    @property
    def start_datetime(self):
        return self._start_datetime

    @property
    def end_datetime(self):
        return self._end_datetime

    @property
    def cars_passed(self):
        return self._cars_passed

    @property
    def cars_waiting(self):
        return self._cars_waiting

    @property
    def duration_minutes(self):
        start = datetime.strptime(self._start_datetime, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(self._end_datetime, "%Y-%m-%d %H:%M:%S")
        return int((end - start).total_seconds() / 60)

    # Статический метод для создания из словаря
    @staticmethod
    def from_dict(data_dict):
        return TrafficLightRecord(
            record_id=data_dict['№'],
            start_datetime=data_dict['дата и время включения'],
            end_datetime=data_dict['дата и время выключения'],
            cars_passed=data_dict['количество проехавших автомобилей'],
            cars_waiting=data_dict['количество автомобилей в ожидании']
        )

    # 4. Продолжение __setattr__ - обновление запрещено
    def update(self, **kwargs):
        """Единственный способ обновить запись"""
        for key, value in kwargs.items():
            if key == 'start_datetime':
                self._validate_datetime(value, "дата и время включения")
                self.__setattr__('_start_datetime', value)
            elif key == 'end_datetime':
                self._validate_datetime(value, "дата и время выключения")
                self.__setattr__('_end_datetime', value)
            elif key == 'cars_passed':
                self._validate_positive_int(value, "количество проехавших автомобилей")
                self.__setattr__('_cars_passed', value)
            elif key == 'cars_waiting':
                self._validate_positive_int(value, "количество автомобилей в ожидании")
                self.__setattr__('_cars_waiting', value)
            else:
                raise KeyError(f"Неизвестное поле: {key}")


# ============================================================
# 2. НАСЛЕДОВАНИЕ
# ============================================================

class AnalyzableTrafficRecord(TrafficLightRecord):
    """Расширенный класс с методами анализа"""

    def __init__(self, record_id, start_datetime, end_datetime, cars_passed, cars_waiting, road_name="Unknown"):
        super().__init__(record_id, start_datetime, end_datetime, cars_passed, cars_waiting)
        self.__setattr__('_road_name', road_name)

    @property
    def road_name(self):
        return self._road_name

    # Новый статический метод для расчёта эффективности
    @staticmethod
    def calculate_efficiency(cars_passed, cars_waiting):
        """Расчёт эффективности работы светофора (0-100%)"""
        total = cars_passed + cars_waiting
        if total == 0:
            return 100.0
        return (cars_passed / total) * 100

    @property
    def efficiency(self):
        return self.calculate_efficiency(self._cars_passed, self._cars_waiting)

    # Аналитический метод
    def get_congestion_level(self):
        """Оценка уровня загруженности"""
        waiting_percent = (self._cars_waiting / (self._cars_passed + self._cars_waiting)) * 100
        if waiting_percent < 10:
            return "Низкий"
        elif waiting_percent < 30:
            return "Средний"
        elif waiting_percent < 50:
            return "Высокий"
        else:
            return "Критический"

    def __repr__(self):
        return (f"AnalyzableTrafficRecord(id={self._id}, road='{self._road_name}', "
                f"efficiency={self.efficiency:.1f}%)")

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str} | Дорога: {self._road_name} | Эффективность: {self.efficiency:.1f}%"


# ============================================================
# 3. КОЛЛЕКЦИЯ С ДОСТУПОМ ПО ИНДЕКСУ И ИТЕРАТОР
# ============================================================

class TrafficLightCollection(Iterator):
    """Класс-коллекция записей с итератором и доступом по индексу"""

    def __init__(self, records=None):
        self._records = records if records is not None else []
        self._index = 0

    # 5. ДОСТУП ПО ИНДЕКСУ (__getitem__)
    def __getitem__(self, index):
        if isinstance(index, slice):
            return TrafficLightCollection(self._records[index])
        if isinstance(index, int):
            if -len(self._records) <= index < len(self._records):
                return self._records[index]
            raise IndexError("Индекс вне диапазона")
        raise TypeError("Индекс должен быть целым числом")

    def __setitem__(self, index, value):
        if not isinstance(value, (TrafficLightRecord, AnalyzableTrafficRecord)):
            raise TypeError("Можно добавлять только объекты TrafficLightRecord")
        if 0 <= index < len(self._records):
            self._records[index] = value
        else:
            raise IndexError("Индекс вне диапазона")

    def __len__(self):
        return len(self._records)

    # 1. ИТЕРАТОР
    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._records):
            result = self._records[self._index]
            self._index += 1
            return result
        raise StopIteration

    # Добавление записи
    def add(self, record):
        if isinstance(record, (TrafficLightRecord, AnalyzableTrafficRecord)):
            self._records.append(record)
        else:
            raise TypeError("Можно добавлять только объекты TrafficLightRecord")

    # 7. ГЕНЕРАТОР для фильтрации
    def filter_by_cars_passed(self, min_passed):
        """Генератор, возвращающий записи с количеством проехавших > min_passed"""
        for record in self._records:
            if record.cars_passed > min_passed:
                yield record

    # Генератор для фильтрации по очереди
    def filter_by_waiting(self, max_waiting):
        """Генератор, возвращающий записи с количеством ожидающих <= max_waiting"""
        for record in self._records:
            if record.cars_waiting <= max_waiting:
                yield record

    # Сортировка (возвращает новую коллекцию)
    def sort_by_start_time(self):
        sorted_records = sorted(self._records, key=lambda x: x.start_datetime)
        return TrafficLightCollection(sorted_records)

    def sort_by_cars_passed(self):
        sorted_records = sorted(self._records, key=lambda x: x.cars_passed)
        return TrafficLightCollection(sorted_records)

    # Статический метод для загрузки из CSV
    @staticmethod
    def load_from_csv(filename, use_analyzable=True):
        """Статический метод для загрузки коллекции из CSV"""
        records = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    record_id = int(row['№'])
                    start = row['дата и время включения']
                    end = row['дата и время выключения']
                    passed = int(row['количество проехавших автомобилей'])
                    waiting = int(row['количество автомобилей в ожидании'])

                    if use_analyzable:
                        record = AnalyzableTrafficRecord(record_id, start, end, passed, waiting)
                    else:
                        record = TrafficLightRecord(record_id, start, end, passed, waiting)
                    records.append(record)
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
        except Exception as e:
            print(f"Ошибка при чтении: {e}")

        return TrafficLightCollection(records)

    # Сохранение в CSV
    def save_to_csv(self, filename):
        fieldnames = ['№', 'дата и время включения', 'дата и время выключения',
                      'количество проехавших автомобилей', 'количество автомобилей в ожидании']

        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for record in self._records:
                writer.writerow({
                    '№': record.id,
                    'дата и время включения': record.start_datetime,
                    'дата и время выключения': record.end_datetime,
                    'количество проехавших автомобилей': record.cars_passed,
                    'количество автомобилей в ожидании': record.cars_waiting
                })
        print(f"Данные сохранены в {filename}")

    # Вывод всех записей
    def print_all(self, title="Данные"):
        print(f"\n{title}:")
        print("-" * 100)
        for record in self._records:
            print(record)
        print("-" * 100)


# ============================================================
# 4. ДОПОЛНИТЕЛЬНЫЙ КЛАСС ДЛЯ РАБОТЫ С ДИРЕКТОРИЯМИ
# ============================================================

class DirectoryAnalyzer:
    """Класс для работы с файловой системой (наследуется от object)"""

    def __init__(self, path=None):
        self._path = path
        self._file_count = 0

    @staticmethod
    def count_files(directory):
        """Статический метод для подсчёта файлов в директории"""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise NotADirectoryError(f"Директория {directory} не существует")

        file_count = 0
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                file_count += 1
        return file_count

    @staticmethod
    def get_user_directory():
        """Статический метод для получения пути от пользователя"""
        while True:
            directory = input("Введите путь к директории: ")
            if os.path.exists(directory) and os.path.isdir(directory):
                return directory
            print("Директория не существует. Попробуйте ещё раз.")


# ============================================================
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================

def create_sample_data():
    """Создание примера данных для демонстрации"""
    records = [
        AnalyzableTrafficRecord(1, '2026-03-01 08:00:00', '2026-03-01 08:30:00', 150, 20, "Ленина-Железнодорожная"),
        AnalyzableTrafficRecord(2, '2026-03-01 12:00:00', '2026-03-01 12:45:00', 200, 35, "Ленина-Железнодорожная"),
        AnalyzableTrafficRecord(3, '2026-03-01 17:30:00', '2026-03-01 18:15:00', 300, 50, "Ленина-Железнодорожная"),
        AnalyzableTrafficRecord(4, '2026-03-02 07:45:00', '2026-03-02 08:20:00', 120, 15, "Советская-Железнодорожная"),
        AnalyzableTrafficRecord(5, '2026-03-02 16:00:00', '2026-03-02 16:40:00', 180, 25, "Советская-Железнодорожная"),
    ]
    collection = TrafficLightCollection(records)
    collection.save_to_csv("data.csv")
    return collection


def main():
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №4 - КЛАССЫ")
    print("Демонстрация всех требований:")
    print("1. Итератор | 2. Перегрузка __repr__ | 3. Наследование")
    print("4. __setattr__ | 5. __getitem__ | 6. Статические методы | 7. Генераторы")
    print("=" * 60)

    # ===== ЗАДАНИЕ 1: Работа с директорией =====
    print("\nЗАДАНИЕ 1: Подсчёт файлов в директории")
    print("-" * 50)
    try:
        directory = DirectoryAnalyzer.get_user_directory()
        file_count = DirectoryAnalyzer.count_files(directory)
        print(f"Количество файлов: {file_count}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # ===== ЗАДАНИЕ 2: Работа с данными светофора =====
    print("\nЗАДАНИЕ 2: Работа с данными светофора (ООП)")
    print("-" * 50)

    # Загрузка или создание данных
    if os.path.exists("data.csv"):
        collection = TrafficLightCollection.load_from_csv("data.csv")
        if len(collection) == 0:
            print("Файл data.csv пуст, создаём пример данных...")
            collection = create_sample_data()
    else:
        print("Создание примера данных...")
        collection = create_sample_data()

    # Проверяем, что коллекция не пустая
    if len(collection) == 0:
        print("Ошибка: нет данных для работы!")
        return

    # 2. ДЕМОНСТРАЦИЯ __repr__
    print("\nДемонстрация __repr__:")
    print(repr(collection[0]))

    # Демонстрация __str__
    print("\nДемонстрация __str__:")
    print(collection[0])

    # 5. ДЕМОНСТРАЦИЯ __getitem__ (доступ по индексу)
    print("\nДемонстрация __getitem__ (доступ по индексу):")
    print(f"Первый элемент: {collection[0]}")
    if len(collection) > 1:
        print(f"Последний элемент: {collection[-1]}")
    if len(collection) >= 3:
        print(f"Срез [1:3]: {[str(r) for r in collection[1:3]]}")

    # 1. ДЕМОНСТРАЦИЯ ИТЕРАТОРА
    print("\nДемонстрация итератора (перебор всех записей):")
    for i, record in enumerate(collection):
        print(f"  {i + 1}. {record}")

    # 3. ДЕМОНСТРАЦИЯ НАСЛЕДОВАНИЯ (AnalyzableTrafficRecord)
    print("\nДемонстрация наследования (расширенный класс с анализом):")
    for record in collection:
        if isinstance(record, AnalyzableTrafficRecord):
            print(f"  Запись {record.id}: Эффективность={record.efficiency:.1f}%, "
                  f"Загруженность={record.get_congestion_level()}")

    # 7. ДЕМОНСТРАЦИЯ ГЕНЕРАТОРОВ
    print("\nДемонстрация генераторов:")

    # Генератор в самом классе записи
    print("  Генератор длительности работы (первые 5 минут записи №1):")
    duration_gen = collection[0].duration_generator()
    for _ in range(min(5, collection[0].duration_minutes)):
        try:
            minute = next(duration_gen)
            print(f"    Минута {minute}")
        except StopIteration:
            break

    # Генераторы в коллекции
    print("\n  Генератор filter_by_cars_passed (>200 проехавших):")
    found = False
    for record in collection.filter_by_cars_passed(200):
        print(f"    {record}")
        found = True
    if not found:
        print("    (нет записей)")

    print("\n  Генератор filter_by_waiting (<=25 в очереди):")
    found = False
    for record in collection.filter_by_waiting(25):
        print(f"    {record}")
        found = True
    if not found:
        print("    (нет записей)")

    # 6. ДЕМОНСТРАЦИЯ СТАТИЧЕСКИХ МЕТОДОВ
    print("\nДемонстрация статических методов:")
    efficiency = AnalyzableTrafficRecord.calculate_efficiency(200, 30)
    print(f"  calculate_efficiency(200, 30) = {efficiency:.1f}%")
    print(f"  DirectoryAnalyzer.count_files('.') = {DirectoryAnalyzer.count_files('.')}")

    # 4. ДЕМОНСТРАЦИЯ __setattr__ (попытка прямого изменения)
    print("\nДемонстрация __setattr__ (защита от прямого изменения):")
    try:
        # Через update() - разрешённый способ
        old_value = collection[0].cars_passed
        collection[0].update(cars_passed=999)
        print(f"  Через update() изменили: {old_value} → {collection[0].cars_passed}")
        # Возвращаем обратно
        collection[0].update(cars_passed=old_value)

        # Попытка прямого изменения публичного атрибута
        try:
            collection[0].cars_passed = 999
            print("  Это не должно было сработать!")
        except AttributeError as e:
            print(f"  Прямое изменение cars_passed запрещено (AttributeError) - правильно")
    except Exception as e:
        print(f"  Ошибка: {e}")

    # ===== ЗАДАНИЕ 3: Добавление новой записи =====
    print("\nЗАДАНИЕ 3: Добавление новой записи")
    print("-" * 50)

    add_new = input("Хотите добавить новую запись? (да/нет): ").lower()
    if add_new in ['да', 'yes', 'y', 'д']:
        print("\n--- Ввод новой записи ---")
        next_id = max(r.id for r in collection) + 1

        while True:
            start = input("Дата и время включения (YYYY-MM-DD HH:MM:SS): ")
            try:
                datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                print("Неверный формат!")

        while True:
            end = input("Дата и время выключения (YYYY-MM-DD HH:MM:SS): ")
            try:
                datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                print("Неверный формат!")

        while True:
            try:
                passed = int(input("Количество проехавших автомобилей: "))
                break
            except ValueError:
                print("Введите целое число!")

        while True:
            try:
                waiting = int(input("Количество автомобилей в ожидании: "))
                break
            except ValueError:
                print("Введите целое число!")

        road = input("Название дороги (опционально): ") or "Неизвестная"

        new_record = AnalyzableTrafficRecord(next_id, start, end, passed, waiting, road)
        collection.add(new_record)
        collection.save_to_csv("data.csv")

        print("\nНовая запись добавлена:")
        print(f"  {new_record}")

    # Итоговый вывод
    print("\n" + "=" * 80)
    print("ИЗМЕНЕНИЕ В ОРИГИНАЛЕ")
    print(" ИТОГОВЫЕ ДАННЫЕ В КОЛЛЕКЦИИ:")
    collection.print_all()

    # Демонстрация работы срезов и статистики
    print("\nСТАТИСТИКА:")
    print(f"Всего записей: {len(collection)}")
    if len(collection) > 0 and isinstance(collection[0], AnalyzableTrafficRecord):
        efficiencies = [r.efficiency for r in collection if isinstance(r, AnalyzableTrafficRecord)]
        if efficiencies:
            print(f"  Средняя эффективность: {sum(efficiencies) / len(efficiencies):.1f}%")

    print("\nПрограмма завершена!")


if __name__ == "__main__":
    main()


#import pandas as pd
#df = pd.read_csv('data.csv')
#sorted_df = df.sort_values('дата и время включения')
#filtered_df = df[df['количество проехавших автомобилей'] > 150]

