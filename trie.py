import nltk
# Создаем словарь
# 1. Ожегов и Шведова
txt = open("slovarOzhegovShvedova.txt")
txt_string = txt.read()
txt_list = txt_string.split('\n')
dictionary = {}

for part in txt_list:
    import re
    try:
        word = str(re.findall(r'[А-Я]{2,}', part)[0]).lower()
    except IndexError:
        word = ''
    meaning = part.strip(word)
    try:
        first_upper = re.findall(r'[А-Я][а-я]+', meaning)[0]  # Находим первое слово с заглавной буквой в описании
        if first_upper:
            first_upper_index = meaning.index(first_upper[0]) # Берем индекс это заглавной буквы в строке
            meaning = meaning[first_upper_index:]
        else:
            raise IndexError
    except:
        meaning = meaning
    if word and meaning:
        dictionary[f'{word}'] = f'{meaning}'

words = list(dictionary.keys())
meanings = list(dictionary.values())
txt.close()

# Итак, построим префиксное дерево для всех слов нашего словаря
import pygtrie
my_trie = pygtrie.CharTrie()

for word in words:
    my_trie[word] = True

# Поизучаем наше дерево
# (В исходном словаре: АБОНЕМЕНТ, АБОНЕНТ, АБОНИРОВАТЬ, АБОРДАЖ, АБОРИГЕН, АБОРИГЕННЫЙ, АБОРТ, АБОРТИВНЫЙ)
# В дальнейшем нам понадобятся только два метода

#print('Есть ли ключ абонент? - ',my_trie.has_key('абонент')) # True только конечные листья
#print('Есть ли дальше ветки от абоне? - ',my_trie.has_subtrie('абоне'))

# почему дос их пор не написали метод dict.fromvalues()?????
def get_key(dict, value):
    for k, v in dict.items():
        if v == value:
            return k

# создадим список возможных начал слова
first_letters = []

for word in words:
    if word[0] in first_letters:
        pass
    else:
        first_letters += word[0]
import random

# 1. Режим "дольше" (чем больше ветвей в префиксном дереве)
# Но чтобы у нас не всегда выбирался узел дерева с наибольшим количеством ветвей,
# добавим рандом, зависящий от системного времени
import datetime

# Пропишем функцию, в которую будем подавать любую part слова, а она нам выведет все следующие буквы в дереве
def next_letters(part):
    # проверяем, сколько слов начинаются на такую part my_trie.keys(prefix=part)
    words_start_with = my_trie.keys(prefix=part)
    # в каждом таком слове берем следующую букву после part
    glob_next_letters = set()
    for leave_word in words_start_with:
        leave_word = list(leave_word)
        letter_next_ind = leave_word.index(part[-1])+1
        if letter_next_ind >= len(leave_word):
            continue
        letter_next = leave_word[letter_next_ind]
        glob_next_letters.add(letter_next)
    glob_next_letters = list(glob_next_letters)
    return glob_next_letters

# Пропишем функцию, в которую будем подавать любую part слова, а она нам выберет следующую букву с наибольшим кол-вом веток
def next_letter_more_leaves(part):
    next_lets = next_letters(part)
    if len(next_lets) == 1:
        next_letter_more_leaves_found = next_lets[0]
    else:
        dict_lens = {}
        words_start_with = my_trie.keys(prefix=part)
        for next_let in next_lets:
            for leave_word in words_start_with:
                # смотрим длину списка, который возвращает .keys (список всех полных слов с таким префиксом)
                if leave_word.startswith(''.join(part)+next_let) or leave_word == ''.join(part)+next_let:
                    how_many = len(my_trie.keys(prefix=''.join(part)+next_let))
                    dict_lens[next_let] = how_many
                else:
                    pass
        print('Кол-во ветвей от каждой следующей буквы - ', dict_lens)
        # выбираем максимальную длину у таких списков
        if dict_lens:
            max_len = max(list(dict_lens.values()))
            print('Максимальное кол-во продолжений - ', max_len)
            # и достаем из нашего словаря длин букву
            # добавив рандом, зависящий от времени
            now = datetime.datetime.now()
            now = str(now)
            if int(now[-1]) != 8:
                next_letter_more_leaves_found = get_key(dict_lens,max_len)
                print('следующая буква', next_letter_more_leaves_found)
            else:
                next_lets = list(next_lets)
                next_letter_more_leaves_found = random.choice(next_lets)
                print('Cработал рандом, следующая буква - ', next_letter_more_leaves_found)
        else:
            next_lets = list(next_lets)
            next_letter_more_leaves_found = random.choice(next_lets)
    return next_letter_more_leaves_found

def the_end():
    print("Урааааааа, вы отгадали слово!")

# 2. Режим "невероятно" (чем меньше вероятность следующей буквы)
# Построим марковские цепи
# И вычислим частоту каждого символа во всех словах нашего словаря
import nltk

chars = [char for word in words for char in word]
cfreq = nltk.ConditionalFreqDist(nltk.bigrams(chars))


# Итак, как обычно мухлюет ведущий в игре контакт, не загадаем сразу слово, а начнем выдавать по одной букве
print("Если вы хотите играть в течение всего карантина, выберите режим 1, если вы хотите неожиданности - выберите режим 2")
regime = input("Ваш режим? - ")

if regime == "1":
    first_letter = random.choice(first_letters)
    part_shown = [f'{first_letter}']
    print('Первая буква - ', first_letter)
    while True:
        letter_found = next_letter_more_leaves(part_shown)
        part_shown += letter_found
        print(part_shown)
        if my_trie.has_subtrie(''.join(part_shown)) == False:
            found_word = ''.join(part_shown)
            print(f'(Загаданное слово - {found_word})')
            break

    let_num = 0
    print('Первая буква - ', found_word[let_num])
    while let_num < len(found_word):
        if_contact = input("Если вы сконтачились, введите 'Contact'\n")
        if if_contact == 'Contact':
            if_word = input("Введите ваше слово с маленькой буквы\n")
            if if_word == found_word:
                the_end()
                break
            else:
                let_num += 1
                print(f'Нет, это не {if_word}. Следующая буква - ', found_word[let_num])
    else:
        print('Вы открыли все буквы!')
        the_end()


elif regime == "2":
    first_letter = random.choice(first_letters)
    # Генерируем маловероятное слово
    known_part = first_letter
    print('Первая буква - ', known_part)
    while True:
        next_letters_all = next_letters(known_part)
        next_letter_freqs = cfreq[known_part[-1]].items() # пары буква-частотность
        # профильтурем наш словарь по наличию следующих букв в дереве
        new_cfeq = {}

        for key, value in cfreq[known_part[-1]].items():
            if key in next_letters_all:
                new_cfeq[key] = value
            else:
                pass
        print('Вероятности следующих букв - ', new_cfeq)
        least_probable_letter = get_key(new_cfeq, min(new_cfeq.values())) # буква с самой маленькой частотностью
        print('Буква с самой маленькой вероятностью - ', least_probable_letter)
        known_part += least_probable_letter
        if my_trie.has_subtrie(known_part) == False:
            found_word = known_part
            print(f'(Загаданное слово - {found_word})')
            break

    let_num = 0
    while let_num < len(found_word):
        if_contact = input("Если вы сконтачились, введите 'Contact'\n")
        if if_contact == 'Contact':
            if_word = input("Введите ваше слово с маленькой буквы\n")
            if if_word == found_word:
                the_end()
                if_meaning = input('Вы хотите узнать значение этого слова? (y/n) ')
                if if_meaning == 'y':
                    print(f'Значение слова {found_word} - ', dictionary.get(found_word))
                else:
                    pass
                break
            else:
                let_num += 1
                print(f'Нет, это не {if_word}. Следующая буква - ', found_word[let_num])
    else:
        print('Вы открыли все буквы!')
        the_end()
        if_meaning = input('Вы хотите узнать значение этого слова? (y/n) ')
        if if_meaning == 'y':
            print(f'Значение слова {found_word} - ', dictionary.get(found_word))
        else:
            pass

else:
    print("Введите '1' или '2' в зависимости от выбранного рижима.")
