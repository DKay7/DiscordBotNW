from config.automoderation.bad_words_config import BAD_WORDS_LIST


cdef list BAD_WORDS = BAD_WORDS_LIST
cdef dict LETTER_ALIASES = {
    'а': ['а', 'a', '@', 'о'],
    'б': ['б', '6', 'b'],
    'в': ['в', 'b', 'v'],
    'г': ['г', 'r', 'g'],
    'д': ['д', 'd'],
    'е': ['е', 'e'],
    'ё': ['ё', 'e'],
    'ж': ['ж', 'zh', '*'],
    'з': ['з', '3', 'z', 'c'],
    'и': ['и', 'u', 'i'],
    'й': ['й', 'u', 'i'],
    'к': ['к', 'k', 'i{', '|{'],
    'л': ['л', 'l', 'ji'],
    'м': ['м', 'm'],
    'н': ['н', 'h', 'n'],
    'о': ['о', 'o', '0', 'a'],
    'п': ['п', 'n', 'p'],
    'р': ['р', 'r', 'p'],
    'с': ['с', 'c', 's', 'з'],
    'т': ['т', 'm', 't'],
    'у': ['у', 'y', 'u'],
    'ф': ['ф', 'f'],
    'х': ['х', 'x', 'h', '}{'],
    'ц': ['ц', 'c', 'u,'],
    'ч': ['ч', 'ch'],
    'ш': ['ш', 'sh'],
    'щ': ['щ', 'sch'],
    'ь': ['ь', 'b'],
    'ы': ['ы', 'bi'],
    'ъ': ['ъ'],
    'э': ['э', 'e'],
    'ю': ['ю', 'io'],
    'я': ['я', 'ya']
}

cdef long levenshtein_distance(str a, str b):
    cdef str first = a.lower()
    cdef str second = b.lower()

    cdef len_first = len(first)
    cdef len_second = len(second)

    cdef list current_row = list(range(len_first + 1))
    cdef int i
    cdef list previous_row
    cdef int j
    cdef int add
    cdef int delete
    cdef int change

    cdef int tmp
    cdef str tmp_s 
    cdef list tmp_l


    if len_first > len_second:
        tmp_s = first
        first = second
        second = tmp_s

        tmp = len_first

        len_first = len_second
        len_second = tmp



    for i in range(1, len_second + 1):
        previous_row  = current_row
        current_row = [i] + [0] * len_first
        
        for j in range(1, len_first + 1):
            add = previous_row[j] + 1
            delete = current_row[j - 1] + 1
            change = previous_row[j - 1]

            if first[j - 1] != second[i - 1]:
                change += 1

            current_row[j] = min(add, delete, change)

    return current_row[len_first]


cdef replace_aliases(str incoming_phrase):
    cdef str phrase = incoming_phrase.lower().strip().replace(" ", "")
    cdef str key
    cdef str letter
    cdef list value
    cdef str phr

    
    for key, value in LETTER_ALIASES.items():
        for letter in value:
            for phr in phrase:
                if letter == phr:
                    phrase = phrase.replace(phr, key)

    return phrase


cpdef int contains_bad_words(str incoming_phrase):
    cdef str phrase = replace_aliases(incoming_phrase)
    cdef str word
    cdef str fragment
    cdef int part


    for word in BAD_WORDS:
        for part in range(len(phrase)):
            fragment = phrase[part: part+len(word)]
            if levenshtein_distance(fragment, word) <= 0.25*len(word):
                return 1

    return 0
