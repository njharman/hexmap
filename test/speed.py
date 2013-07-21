import sys
import pstats
import cProfile

from hexmap import Hex


def arc(count):
    t = Hex()
    foo = t.arc(1, 4 , count)
    sys.stderr.write('\n\n%s hexes\n\n' % len(foo))


def fouronthefloor(count):
    t = Hex()
    foo = t.sixpack(count)
    sys.stderr.write('\n\n%s hexes\n\n' % len(foo))


cProfile.run('fouronthefloor(200)', 'profile.stats')
p = pstats.Stats('profile.stats')
p.strip_dirs().sort_stats('time').print_stats(10)
