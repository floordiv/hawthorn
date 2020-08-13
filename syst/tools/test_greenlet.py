import gevent


def f1():
    print(1)
    gevent.sleep(0)
    print(3)


def f2():
    print(2)
    gevent.sleep(0)
    print(4)


gl1 = gevent.spawn(f1)
gl2 = gevent.spawn(f2)
gevent.joinall((gl1, gl2))
# gl1.start(), gl2.start()
# gl1.spawn(), gl2.spawn()
