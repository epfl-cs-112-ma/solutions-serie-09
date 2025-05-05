import re

as_and_b = re.compile('a+b')

print(as_and_b.fullmatch('aaab'))  # <re.Match object>
print(as_and_b.fullmatch('ab'))    # <re.Match object>
print(as_and_b.fullmatch('b'))     # None
print(as_and_b.fullmatch('aaaba')) # None

date_re = re.compile('([0-9]+)/([0-9]+)/([0-9]+)')

result = date_re.fullmatch('1/5/2025')
if result:
    print(result.group(1)) # '1'
    print(result.group(2)) # '5'
    print(result.group(3)) # '2025'

txt = """
La Confédération suisse, telle qu'on la connaît, a reçu sa constitution
en 12/9/1848. Elle est rejoint l'ONU le 11/9/2002. Mais comme elle a été
reconnue neutre le 20/5/1815 perpétuellement, ce n'est pas demain la
veille qu'on la verra dans l'OTAN.
"""

for date_match in date_re.finditer(txt):
    print(date_match.group(0))
