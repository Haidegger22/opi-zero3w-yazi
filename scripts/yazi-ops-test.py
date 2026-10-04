#!/usr/bin/env python3
# yazi_ops_final.py — проверка всех файловых операций yazi (копирование, перенос, удаление,
# переименование, копирование пути) в псевдотерминале, с проверкой результата на диске.
import fcntl, os, pty, re, select, shutil, struct, subprocess, termios, time

D = os.path.join(os.path.expanduser("~"), "yazi-ops-test")
ERRLOG = "/tmp/yazi-pty-err.txt"
ENV = {**os.environ, "DISPLAY": ":0", "XAUTHORITY": os.path.expanduser("~/.Xauthority"),
       "TERM": "xterm-256color"}
COLS, ROWS = 120, 34

def start():
    pid, fd = pty.fork()
    if pid == 0:
        os.makedirs(D, exist_ok=True); os.chdir(D)
        os.execvpe("bash", ["bash", "-c", f'exec yazi "{D}" 2>{ERRLOG}'], ENV)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
    return pid, fd

def drain(fd, seconds):
    buf, end = b"", time.time() + seconds
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try: buf += os.read(fd, 65536)
            except OSError: break
    return buf.decode(errors="replace")

def clipboard():
    return subprocess.run(["xclip", "-o", "-selection", "clipboard"], env=ENV,
                          capture_output=True, text=True).stdout.strip()

def run(keys, clipboard_after=False):
    pid, fd = start()
    time.sleep(3.5); drain(fd, 1.0)
    for k in keys:
        os.write(fd, k); time.sleep(0.9)
    cl = clipboard() if clipboard_after else None
    drain(fd, 0.8)
    os.write(fd, b"q"); time.sleep(0.7)
    try: os.kill(pid, 9); os.waitpid(pid, 0)
    except Exception: pass
    return cl

def prepare():
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D + "/dst")
    open(D + "/a-note.txt", "w").write("файл A\n")
    open(D + "/b-note.txt", "w").write("файл B\n")
    open(D + "/c-del.txt", "w").write("файл C\n")

J, K, L, ENTER = b"j", b"k", b"l", b"\r"

print("=== КОПИРОВАНИЕ ФАЙЛА В ПОДКАТАЛОГ: j (файл) → y → k (папка) → l → p ===")
prepare()
run([J, b"y", K, L, b"p"])
print("   dst:", sorted(os.listdir(D + "/dst")), "| рядом с папкой:", sorted(os.listdir(D)))

print("=== ПЕРЕНОС (вырезать/вставить): j j → x → k k → l → p ===")
prepare()
run([J, J, b"x", K, K, L, b"p"])
print("   dst:", sorted(os.listdir(D + "/dst")), "| рядом с папкой:", sorted(os.listdir(D)))

print("=== УДАЛЕНИЕ В КОРЗИНУ: j j j → d ===")
prepare()
run([J, J, J, b"d"])
print("   рядом с папкой:", sorted(os.listdir(D)))

print("=== ПЕРЕИМЕНОВАНИЕ: j → r → добавить «-2» → Enter ===")
prepare()
run([J, b"r", b"-2", ENTER])
print("   рядом с папкой:", sorted(os.listdir(D)))

print("=== КОПИРОВАНИЕ ПУТИ В БУФЕР: j → c → c ===")
prepare()
cl = run([J, b"c", b"c"], clipboard_after=True)
print("   буфер обмена:", repr(cl))

print("=== КОПИРОВАНИЕ ИМЕНИ ФАЙЛА: j → c → f ===")
print("   буфер обмена:", repr(run([J, b"c", b"f"], clipboard_after=True)))

print("=== ПУТЬ КАТАЛОГА: j j (папка) → c → d ===")
# порядок: dst, a-note.txt, b-note.txt, c-del.txt → j j = a-note? проверим оба варианта
print("   буфер обмена:", repr(run([K, b"c", b"d"], clipboard_after=True)))
