import os

# Больше этой суммы (в млн руб.) в колонку таблицы не поместится
MAX_MONEY = 999999999

# Одна запись в файле - одна строка вида: название;адрес;вкладчики;сумма
SEPARATOR = ";"

# Путь строится от папки программы, чтобы файл находился при запуске из любой папки
PROGRAM_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(PROGRAM_FOLDER, "data", "banks.txt")


class Bank:
    def __init__(self, name, address, depositors, money):
        self.name = name              # название
        self.address = address        # адрес
        self.depositors = depositors  # количество вкладчиков
        self.money = money            # сумма вкладов, млн руб.


# ===== Работа с данными: эти функции ничего не печатают и не спрашивают =====


def check_text(value):
    value = value.strip()
    if value == "":
        return None, "поле не может быть пустым"
    # ";" разделяет поля в файле, с ним запись потом не прочитается
    if SEPARATOR in value:
        return None, "нельзя использовать символ ;"
    return value, None


def check_depositors(value):
    try:
        number = int(value.strip())
    except ValueError:
        return None, "количество вкладчиков должно быть целым числом"
    if number < 0:
        return None, "количество вкладчиков не может быть отрицательным"
    return number, None


def check_money(value):
    # Пользователи часто пишут дробную часть через запятую
    try:
        number = float(value.strip().replace(",", "."))
    except ValueError:
        return None, "сумма вкладов должна быть числом"
    if number >= 0 and number <= MAX_MONEY:
        return number, None
    return None, f"сумма вкладов должна быть от 0 до {MAX_MONEY}"


# Строка из файла проверяется теми же функциями, что и ручной ввод,
# чтобы правила для файла и для клавиатуры не различались
def read_line(line):
    parts = line.split(SEPARATOR)
    if len(parts) != 4:
        return None, "должно быть 4 поля через ;"
    name, error = check_text(parts[0])
    if error is not None:
        return None, "название - " + error
    address, error = check_text(parts[1])
    if error is not None:
        return None, "адрес - " + error
    depositors, error = check_depositors(parts[2])
    if error is not None:
        return None, error
    money, error = check_money(parts[3])
    if error is not None:
        return None, error
    return Bank(name, address, depositors, money), None


# Строка с ошибкой не прерывает загрузку: она пропускается,
# а её номер и причина попадают в список errors
def load_banks(path):
    banks = []
    errors = []
    with open(path, encoding="utf-8") as file:
        number = 0
        for line in file:
            number += 1
            if line.strip() == "":
                continue
            bank, error = read_line(line)
            if error is None:
                banks.append(bank)
            else:
                errors.append(f"строка {number}: {error}")
    return banks, errors


def save_banks(path, banks):
    with open(path, "w", encoding="utf-8") as file:
        for bank in banks:
            file.write(bank.name + SEPARATOR + bank.address + SEPARATOR
                       + str(bank.depositors) + SEPARATOR + str(bank.money) + "\n")


def find_banks(banks, field, text):
    text = text.lower()
    found = []
    for bank in banks:
        if field == "name":
            value = bank.name
        else:
            value = bank.address
        # lower() с обеих сторон, чтобы "сбер" находил "Сбербанк"
        if text in value.lower():
            found.append(bank)
    return found


# Сортировка умеет работать с двумя полями, поэтому число для сравнения
# достаётся в отдельной функции
def get_number(bank, field):
    if field == "depositors":
        return bank.depositors
    return bank.money


# Сортировка вставками: каждая запись сдвигается влево, пока не встанет на своё место
def sort_banks(banks, field, descending):
    for i in range(1, len(banks)):
        current = banks[i]
        value = get_number(current, field)
        j = i - 1
        while j >= 0:
            other = get_number(banks[j], field)
            # Сравнение строгое, иначе записи с равными числами поменялись бы местами
            if descending and other >= value:
                break
            if not descending and other <= value:
                break
            banks[j + 1] = banks[j]
            j -= 1
        banks[j + 1] = current


# ===== Вывод на экран и ввод с клавиатуры =====


# Старые результаты не должны смешиваться с новым выводом
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# Без паузы сообщение исчезло бы при следующей очистке экрана
def pause():
    input("Нажмите Enter, чтобы продолжить...")


def show_error(title, reason):
    clear_screen()
    print(title)
    print()
    print("Ошибка:", reason)
    print()
    pause()


# Пустой ввод возвращает None, чтобы пункт меню можно было бросить на полпути
def ask_value(prompt, check):
    while True:
        text = input(prompt)
        if text.strip() == "":
            return None
        value, error = check(text)
        if error is None:
            return value
        print("Ошибка:", error)


# Выбор файла одинаковый для загрузки и сохранения, поэтому вынесен отдельно.
# Возвращает None, если пользователь передумал
def ask_path():
    print("1. Стандартный файл (data/banks.txt)")
    print("2. Указать другой файл")
    print("0. Назад")
    print()
    choice = input("Ваш выбор: ").strip()
    if choice == "0":
        return None
    elif choice == "1":
        return DEFAULT_FILE
    elif choice != "2":
        show_error("Выбор файла", "нет такого пункта, введите 0, 1 или 2")
        return None

    print()
    print("Пустой ввод - возврат в главное меню")
    path = input("Путь к файлу: ").strip()
    if path == "":
        return None
    return path


# Спрашивает перед действиями, которые нельзя отменить
def confirm(question):
    answer = input(question + " (д/н): ").strip().lower()
    return answer == "д" or answer == "да"


# Таблица принимает любой список, чтобы ей могли пользоваться поиск и сортировка
def print_table(banks):
    # Ширина по самому длинному значению, иначе колонки разъедутся
    name_width = len("Название")
    address_width = len("Адрес")
    for bank in banks:
        if len(bank.name) > name_width:
            name_width = len(bank.name)
        if len(bank.address) > address_width:
            address_width = len(bank.address)

    # ljust и rjust дополняют строку пробелами до нужной ширины
    header = ("№".rjust(3) + " | " + "Название".ljust(name_width) + " | "
              + "Адрес".ljust(address_width) + " | " + "Вкладчики".rjust(10) + " | "
              + "Сумма, млн руб.".rjust(15))
    print(header)
    print("-" * len(header))
    number = 1
    for bank in banks:
        money = f"{bank.money:.2f}"
        print(str(number).rjust(3) + " | " + bank.name.ljust(name_width) + " | "
              + bank.address.ljust(address_width) + " | "
              + str(bank.depositors).rjust(10) + " | " + money.rjust(15))
        number += 1
    print()


# ===== Меню =====


def menu_load(banks):
    clear_screen()
    print("=== ЗАГРУЗКА ИЗ ФАЙЛА ===")
    print()
    path = ask_path()
    if path is None:
        return

    try:
        loaded, errors = load_banks(path)
    except FileNotFoundError:
        show_error("Загрузка из файла", "файл не найден: " + path)
        return

    print()
    if len(loaded) == 0:
        print("В файле нет ни одной подходящей записи, данные в памяти не изменены")
    else:
        if len(banks) > 0:
            answer = confirm(f"Записи в памяти ({len(banks)}) будут заменены. Продолжить?")
            if not answer:
                return
        banks.clear()
        banks.extend(loaded)
        print("Загружено записей:", len(banks))

    if len(errors) > 0:
        print("Пропущено строк:", len(errors))
        for error in errors:
            print("  " + error)
    print()
    pause()


def menu_add(banks):
    clear_screen()
    print("=== ДОБАВЛЕНИЕ БАНКА ===")
    print("Пустой ввод - возврат в главное меню")
    print()
    name = ask_value("Название: ", check_text)
    if name is None:
        return
    address = ask_value("Адрес: ", check_text)
    if address is None:
        return
    depositors = ask_value("Количество вкладчиков: ", check_depositors)
    if depositors is None:
        return
    money = ask_value("Сумма вкладов, млн руб.: ", check_money)
    if money is None:
        return
    bank = Bank(name, address, depositors, money)
    banks.append(bank)
    print()
    print("Банк добавлен. Записей в памяти:", len(banks))
    print()
    print_table([bank])
    pause()


def menu_show(banks):
    if len(banks) == 0:
        print("Записей нет. Добавьте банк или загрузите файл")
        pause()
        return
    clear_screen()
    print("=== ВСЕ БАНКИ ===")
    print()
    print_table(banks)
    pause()


def menu_search(banks):
    if len(banks) == 0:
        print("Записей нет. Добавьте банк или загрузите файл")
        pause()
        return
    clear_screen()
    print("=== ПОИСК ===")
    print()
    print("1. По названию")
    print("2. По адресу")
    print("0. Назад")
    print()
    choice = input("Ваш выбор: ").strip()
    if choice == "0":
        return
    elif choice == "1":
        field = "name"
    elif choice == "2":
        field = "address"
    else:
        show_error("Поиск", "нет такого пункта, введите 0, 1 или 2")
        return

    print()
    print("Пустой ввод - возврат в главное меню")
    text = ask_value("Что искать: ", check_text)
    if text is None:
        return
    found = find_banks(banks, field, text)
    print()
    if len(found) == 0:
        print("Ничего не найдено")
    else:
        print("Найдено:", len(found))
        print()
        print_table(found)
    pause()


def menu_sort(banks):
    if len(banks) == 0:
        print("Записей нет. Добавьте банк или загрузите файл")
        pause()
        return
    clear_screen()
    print("=== СОРТИРОВКА ===")
    print()
    print("1. По количеству вкладчиков")
    print("2. По сумме вкладов")
    print("0. Назад")
    print()
    choice = input("Ваш выбор: ").strip()
    if choice == "0":
        return
    elif choice == "1":
        field = "depositors"
    elif choice == "2":
        field = "money"
    else:
        show_error("Сортировка", "нет такого пункта, введите 0, 1 или 2")
        return

    print()
    print("1. По возрастанию")
    print("2. По убыванию")
    print("0. Назад")
    print()
    choice = input("Ваш выбор: ").strip()
    if choice == "0":
        return
    elif choice == "1":
        descending = False
    elif choice == "2":
        descending = True
    else:
        show_error("Сортировка", "нет такого пункта, введите 0, 1 или 2")
        return

    sort_banks(banks, field, descending)
    print()
    print_table(banks)
    pause()


def menu_save(banks):
    if len(banks) == 0:
        print("Записей нет, сохранять нечего")
        pause()
        return
    clear_screen()
    print("=== СОХРАНЕНИЕ В ФАЙЛ ===")
    print()
    path = ask_path()
    if path is None:
        return

    print()
    if os.path.exists(path):
        answer = confirm("Файл уже существует и будет перезаписан. Продолжить?")
        if not answer:
            return
    try:
        save_banks(path, banks)
    except OSError:
        show_error("Сохранение в файл", "не удалось записать файл: " + path)
        return
    print("Сохранено записей:", len(banks))
    print("Файл:", path)
    print()
    pause()


def print_menu(count):
    print("=== БАНКИ ГОРОДА ===")
    print("Записей в памяти:", count)
    print()
    print("1. Загрузить из файла")
    print("2. Добавить банк")
    print("3. Показать все банки")
    print("4. Поиск")
    print("5. Сортировка")
    print("6. Сохранить в файл")
    print("0. Выход")
    print()


def main():
    banks = []
    while True:
        clear_screen()
        print_menu(len(banks))
        choice = input("Ваш выбор: ").strip()
        if choice == "0":
            print("До свидания!")
            break
        elif choice == "1":
            menu_load(banks)
        elif choice == "2":
            menu_add(banks)
        elif choice == "3":
            menu_show(banks)
        elif choice == "4":
            menu_search(banks)
        elif choice == "5":
            menu_sort(banks)
        elif choice == "6":
            menu_save(banks)
        else:
            show_error("Главное меню", "нет такого пункта, введите число от 0 до 6")


if __name__ == "__main__":
    # Ctrl+C во время ввода иначе завершил бы программу длинным сообщением об ошибке
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Программа завершена")
