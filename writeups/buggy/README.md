# Buggy

Автор: [@nsychev](https://github.com/nsychev)

Этот сервис — простой TCP-сервер на баше, позволяющий создавать и читать заметки по ключу.

```bash
$ nc 10.117.1.2 3333
Welcome to SAFEST STORAGE EVER!!!!!
Put/get?
put
Token?
key
Secret?
value
OK!

$ nc 10.117.1.2 3333
Welcome to SAFEST STORAGE EVER!!!!!
Put/get?
get
Token?
key
Your secret:
value
```

## TL;DR

Суть сервиса в одном сообщении

```
Nikita Sychev, [19.10.18 02:39]
суть сервиса будет в том, что оно само по себе одно большое RCE, и его надо тупо переписать на пухтон
```

## Баг 1 — put

Запись секрета в файл происходит вот так:

```bash
bash -c "echo $flag > storage/$filename"
```

Проще всего передать в качестве секрета такую строку:

```bash
$(cat storage/*)
```

Тогда в файлик `$filename` запишутся все имеющиеся файлы в `storage/`, в том числе и все флаги. Потом получим их с помощью `get`.

[Код эксплойта](nsychev_buggy_put.py)

### Как исправлять? 

Самый простой способ — убрать `bash -c`. Также можно добавить проверку на отсутствие файла:

```bash
if [[ ! -f "$filename" ]]; then
    echo $flag > storage/$filename
fi
```

Однако, мы всё ещё можем писать в любую директорию (передав в `$filename`, например, `../../../tmp/somefile`). Об этом чуть ниже.


## Баг 2 — get

Чтение секрета происходит не менее безопасно, чем запись:

```bash
bash -c "cat storage/$filename"
```

Воспользуемся другим трюком — передадим в качестве токена
`*`. Что же произойдет? Удивительно, но выведутся все файлы из `storage/`.

[Код эксплойта](nsychev_buggy_get.py)

### Как исправлять?

Опять же, можно просто убрать `bash -c` и проверять существование файла:

```bash
if [[ -f "storage/$filename" ]]; then
    echo "Your secret:"
    cat storage/$filename
```

## Баг 3 — AFR

Даже накатив два фикса выше, мы не исправим сервис полностью.

Мы всё ещё можем читать произвольный файл в системе и создавать новые файлы там, где у нас есть права доступа. Таким образом можно попробовать создать файл в `/tmp/` и попробовать как-то его использовать из другого сервиса.

А всё из-за того, что писать на баше сервисы не стоит.

Лучший вариант — просто всё переписать. Например, на питоне:

```
#!/usr/bin/env python3

import re
import os

print("Welcome to SAFEST STORAGE EVER!!!!!")
print("Put/get?", flush=True)
cmd = input()

print("Token?", flush=True)
token = input()

# search for dots and slashes 
if re.search("[.\\]", token):
    print("Invalid token!", flush=True)
elif cmd == "put":
    print("Secret?", flush=True)
    secret = input()
    
    with open(os.path.join("storage/", token), "w") as f:
        print(secret, file=f)
    
    print("OK", flush=True)
elif cmd == "get":
    with open(os.path.join("storage/", token)) as f:
        print(f.read())
    
    print("OK", flush=True)
else:
    print("Bad command", flush=True)
```

Получилось на 10 строк больше, зато, возможно, без дыр.
