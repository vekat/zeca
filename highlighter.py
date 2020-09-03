from difflib import Differ

"""
Compares two strings and returns two versions of it in a tuple.

The example in the file returns:
('~~s~~er~~a~~ que ~~e~~ amor', '**S**er**á** que **é** amor**?**')

The first string in the tupple has the differing characters stroke through,
and the second string has the differing characters highlighted markdown
style.
"""

def compare_texts(original_text, corrected_text):
    d = Differ()
    comp = list(d.compare(original_text, corrected_text))

    mistakes = []
    correction = []
    for c in comp:
        if c == '   ':
            mistakes.append(' ')
            correction.append(' ')
        elif c[0] == '+':
            correction.append('**{}**'.format(c[-1]))
        elif c[0] == '-':
            mistakes.append('~~{}~~'.format(c[-1]))
        else:
            mistakes.append(c[-1])
            correction.append(c[-1])
        
    mistakes = ''.join(mistakes)
    mistakes = mistakes.replace('~~~~', '') # Remove in-between strike-throughs

    correction = ''.join(correction)
    correction = correction.replace('****', '') # Remove in-between highlights

    return mistakes, correction


if __name__ == "__main__":
    print(compare_texts('sera que e amor', 'Será que é amor?'))
