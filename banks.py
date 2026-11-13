import os

# Больше этой суммы (в млн руб.) в колонку таблицы не поместится
max_money = 999999999


class Bank:
    def __init__(self, name, address, depositors, deposits):
        self.name = name              # название
        self.address = address        # адрес
        self.depositors = depositors  # количество вкладчиков
        self.deposits = deposits      # сумма вкладов, млн руб.


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


# Проверки не печатают сами, чтобы их можно было использовать и при загрузке файла
def check_text(value):
    value = value.strip()
    if value == "":
        return None, "поле не может быть пустым"
    # ";" будет разделять поля в файле
    if ";" in value:
        return None, "нельзя использовать символ ;"
    return value, None


def to_depositors(value):
    try:
        number = int(value.strip())
    except ValueError:
        return None, "количество вкладчиков должно быть целым числом"
    if number < 0:
        return None, "количество вкладчиков не может быть отрицательным"
    return number, None


def to_deposits(value):
    # Пользователи часто пишут дробную часть через запятую
    try:
        number = float(value.strip().replace(",", "."))
    except ValueError:
        return None, "сумма вкладов должна быть числом"
    if number >= 0 and number <= max_money:
        return number, None
    return None, f"сумма вкладов должна быть от 0 до {max_money}"


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

# Меню
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
    depositors = ask_value("Количество вкладчиков: ", to_depositors)
    if depositors is None:
        return
    deposits = ask_value("Сумма вкладов, млн руб.: ", to_deposits)
    if deposits is None:
        return
    bank = Bank(name, address, depositors, deposits)
    banks.append(bank)
    print()
    print("Банк добавлен. Записей в памяти:", len(banks))
    print()
    print_table([bank])
    pause()


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
        deposits = f"{bank.deposits:.2f}"
        print(str(number).rjust(3) + " | " + bank.name.ljust(name_width) + " | "
              + bank.address.ljust(address_width) + " | "
              + str(bank.depositors).rjust(10) + " | " + deposits.rjust(15))
        number += 1
    print()


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


def find_banks(banks, field, query):
    query = query.lower()
    found = []
    for bank in banks:
        if field == "name":
            text = bank.name
        else:
            text = bank.address
        # lower() с обеих сторон, чтобы "сбер" находил "Сбербанк"
        if query in text.lower():
            found.append(bank)
    return found


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
    query = ask_value("Что искать: ", check_text)
    if query is None:
        return
    found = find_banks(banks, field, query)
    print()
    if len(found) == 0:
        print("Ничего не найдено")
    else:
        print("Найдено:", len(found))
        print()
        print_table(found)
    pause()


# Сортировка умеет работать с двумя полями, поэтому число для сравнения
# достаётся в отдельной функции
def get_number(bank, field):
    if field == "depositors":
        return bank.depositors
    return bank.deposits


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
        field = "deposits"
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
        elif choice == "2":
            menu_add(banks)
        elif choice == "3":
            menu_show(banks)
        elif choice == "4":
            menu_search(banks)
        elif choice == "5":
            menu_sort(banks)
        elif choice in ("1", "6"):
            print("Функция в разработке")
            pause()
        else:
            show_error("Главное меню", "нет такого пункта, введите число от 0 до 6")


if __name__ == "__main__":
    # Ctrl+C во время ввода иначе завершил бы программу длинным сообщением об ошибке
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Программа завершена")
