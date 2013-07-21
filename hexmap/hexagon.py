__copyright__ = 'Copyright (c) 2004,2012 Norman J. Harman Jr. njharman@gmail.com'
__license__ = '''This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA'''
__doc__ = '''Paper wargame style hexes.

%(copyright)s

%(license)s
''' % {'copyright': __copyright__, 'license': __license__}

import logging
log = logging.getLogger(__name__)

import math


class OffMapError(ValueError):
    '''Hex is off map.'''


class Hex(object):
    '''Traditional wargame four digit hexes, "0142".

     - "Flat" on top hexgrid with "0101 in upper left.
     - Hexsides numbered 1-6 clockwise, 1 at top.
     - "0142" is split into "01", self.x part and '42', self.y part.
     - Hex numbers is unbounded in all directions, neg/pos.
     - If x or y > 99, string value value padding expands as needed "012156",
       "00001234".

    Note:  Consider Hex instances to be "immutable", although this is not
    currently enforeced.
    '''
    digits = 2  # x, y portions of string value are zero padded this many digits mininum.

    __slots__ = ('x', 'y', '_value')

    def __init__(self, x=None, y=None):
        '''
        Following constructions are supported.

          * Hex()           # (0,0) origin.
          * Hex('0134')     # (1,34) even length string.
          * Hex('101034')   # (101,34)
          * Hex('14')       # (1,4)
          * Hex('-1010')    # (-10, 10)
          * Hex('10-10')    # (10, -10)
          * Hex('-10-10')   # (-10, -10)
          * Hex(1, -34)     # (1,-34) +/- integer, +/- integer.
          * Hex(2301)       # (23,01) Even 'length' integer.
          * Hex(101034)     # (101,34)

        Not valid.

          * Hex(110)
          * Hex(0110)
          * Hex(-1010)
          *
        '''
        if x is None:
            x, y = 0, 0
        elif y is None:
            x, y = self.split(x)
        self.x = int(x)  # read-only
        self.y = int(y)  # read-only

    @property
    def value(self):
        # moved out of constructor for lazy eval.
        if not hasattr(self, '_value'):
            digits = max(self.digits, len(str(abs(self.x))), len(str(abs(self.y))))
            # annoying that sign is factored into padding.  -2,4 is '-204' not '-0204'.
            self._value = ('{:0%id}{:=0%id}' % (digits + (self.x < 0), digits + (self.y < 0))).format(self.x, self.y)
        return self._value

    def __str__(self):
        return self.value

    def __len__(self):
        return 2

    def __getitem__(self, idx):
        return [self.x, self.y][idx]

    def __hash__(self):
        # hash tuple to avoid calling .value / string stuff which is expensive
        # and may never need to be calculated.
        return hash((self.x, self.y))
        if not hasattr(self, '_value'):
            self._value = hash((self.x, self.y))
        return self._value

    def __eq__(self, other):
        try:
            if isinstance(other, Hex):
                # Compare this and not .value, much faster.
                return self.x == other.x and self.y == other.y
            elif isinstance(other, str):
                x, y = self.split(other)
            elif isinstance(other, int):
                x, y = self.split(other)
            elif len(other) == 2:
                x, y = other[0], other[1]
            return self.x == int(x) and self.y == int(y)
        except (TypeError, IndexError, ValueError):
            return False

    def __ne__(self, other):
        try:
            if isinstance(other, str):
                other = self.__class__(other)
            elif isinstance(other, int):
                return str(self) != str(other)
            return len(other) != 2 or self.x != other[0] or self.y != other[1]
        except (TypeError, IndexError, OffMapError):
            return False

    def __add__(self, other):
        '''Hex + any two item sequence.'''
        return self.__class__(self.x + int(other[0]), self.y + int(other[1]))

    def __radd__(self, other):
        '''Any two item sequence + Hex.'''
        return self.__class__(self.x + int(other[0]), self.y + int(other[1]))

    def __sub__(self, other):
        '''Hex - any two item sequence.'''
        return self.__class__(self.x - int(other[0]), self.y - int(other[1]))

    def __rsub__(self, other):
        '''Any two item sequence - Hex'''
        return self.__class__(self.x - int(other[0]), self.y - int(other[1]))

    def copy(self):
        return self.__class__(self.x, self.y)

    def distance_to(self, to_hex):
        '''
        :return: Distance in hexes to hex.
        '''
        if to_hex == self:
            return 0
        # if in either triangle formed by extending left/right hexsides to
        # infinity then distance is abs(a-b)
        # in triangle if (rounding up) abs(a1-b1) b2
        (a1, a2) = (self[0], self[1])
        (b1, b2) = (to_hex[0], to_hex[1])
        d1 = abs(b1 - a1)
        d2 = abs(b2 - a2)
        offset = d1 / 2
        if (a1 % 2) and ((b1 + 1) % 2):  # if a is odd and b even
            offset += 1
        triMin = a2 - offset
        triMax = triMin + d1
        # in triangles d1 is the distance.
        distance = d1
        # outside of triangles must add more.
        if b2 < triMin:
                distance += (triMin - b2)
        if b2 > triMax:
            distance += (b2 - triMax)
        return distance

    def hexsides_to(self, to_hex):
        '''Tuple of 1, 2, or 6(same hex) hexsides passed through on way to_hex.
        Accurate for distances up to about 10000 hexes.
        :return: Tuple of integer hexsides.
        '''
        if self == to_hex:
            return (1, 2, 3, 4, 5, 6)
        d_x = to_hex.x - self.x
        d_y = to_hex.y - self.y
        # Same hex column.
        if d_x == 0:
            if d_y < 0:
                return (1,)
            else:
                return (4,)
        # Even / odd columns need a nudge.
        if (self.x % 2) and not (to_hex.x % 2):
            d_y += .5
        if not (self.x % 2) and (to_hex.x % 2):
            d_y -= .5
        # Hexes are wider than tall.
        d_y *= -20.0  # Negative cause math origin is lower left not upper left.
        d_x *= 17.32
        angle = round(math.degrees(math.atan2(d_y, d_x)), 2)
        if angle > 0 and angle < 60:
            answer = (2, )
        elif angle > 60 and angle < 120:
            answer = (1, )
        elif angle > 120 and angle < 180:
            answer = (6, )
        elif angle < 0 and angle > -60:
            answer = (3, )
        elif angle < -60 and angle > -120:
            answer = (4, )
        elif angle < -120 and angle > -180:
            answer = (5, )
        elif angle == 60:
            answer = (1, 2)
        elif angle == 0:
            answer = (2, 3)
        elif angle == -60:
            answer = (3, 4)
        elif angle == -120:
            answer = (4, 5)
        elif abs(angle) == 180:
            answer = (5, 6)
        elif angle == 120:
            answer = (6, 1)
        return answer

    def hex_in_direction(self, direction):
        '''
        :param direction: hexside, numbered 1-6 clockwise, 1 being 'north'
        :return: Hex instance.
        '''
        if direction not in (1, 2, 3, 4, 5, 6):
            raise ValueError('Invalid direction %s.' % (direction, ))
        (x, y) = (self.x, self.y)
        odd = x % 2
        if direction == 1:
            y -= 1
        if direction == 4:
            y += 1
        if direction in (3, 5) and not odd:
            y += 1
        if direction in (2, 6) and odd:
            y -= 1
        if direction in (2, 3):
            x += 1
        if direction in (5, 6):
            x -= 1
        return self.__class__(x, y)

    def sixpack(self, distance=1, include_self=False):
        '''Surrounding hexes to distance.
        :return: set of Hex instances.
        '''
        if distance == 1:
            hexes = set([self.hex_in_direction(x) for x in (1, 2, 3, 4, 5, 6)])
        else:
            hexes = self.arc(1, 6, distance, include_self, full_circle=True)
        if include_self:
            hexes.add(self)
        return hexes

    def arc(self, start, end, distance=1, include_self=False, full_circle=False):
        '''Hexes in arc defined by hexsides (clockwise, inclusive).
        NOTE: The arc 1,6 is not all surrounding hexes. It does not include the
        hexes beyond range 1 betwen the hexrows heading out direction 1 and 6.
        :param start: hexside 1-6.
        :param end: hexside 1-6.
        :param distance: how far out to walk.
        :param include_self: include origin hex.
        :param full_circle: all hexes within x distance (prevents having to repeat walking logic in sixpack).
        :return: set of Hex instances.
        '''
        # Go out 1 in 'start' direction,
        # Walk clockwise around ring until we get to a hex in 'end' direction,
        # Repeat 'distance' times.
        hexes = set()
        if include_self:
            hexes.add(self)
        # Rotations we use to walk *around* ring.
        if full_circle:
            path = [self.rotate(h, 2) for h in self.rotator(start, end)]
        else:
            path = [self.rotate(h, 2) for h in self.rotator(start, end)][:-1]
        start_row = self
        for ring in range(1, distance + 1):
            start_row = start_row.hex_in_direction(start)
            hexes.add(start_row)
            #log.debug('start:%s ring:%i\t%s' % (start_row, ring, [str(h) for h in hexes]))
            current = start_row
            for direction in path:
                for i in range(ring):
                    prev = current
                    current = current.hex_in_direction(direction)
                    hexes.add(current)
                    #log.debug('step:%i in directo %i %s -> %s\t%s' % (i + 1, direction, prev, current, [str(h) for h in hexes]))
        return hexes

    def half_arc(self, hexsides, distance=1, include_self=False):
        '''180deg 'half' arc'''
        # TODO: not really sure what this is...
        # go straight adding (left/rigt) sides
        hexes = set()
        if include_self:
            hexes.add(self)
        straight = hexsides[1]
        left = hexsides[0] - 1
        if left < 1:
            left += 6
        right = hexsides[2] + 1
        if right > 6:
            right -= 6
        center_hex = self.hex_in_direction(straight)
        side = 2
        while distance > 0:
            left_hex = center_hex
            right_hex = center_hex
            for i in range(side):
                left_hex = left_hex.hex_in_direction(left)
                hexes.add(left_hex)
                right_hex = right_hex.hex_in_direction(right)
                hexes.add(right_hex)
            hexes.add(center_hex)
            center_hex = center_hex.hex_in_direction(straight)
            distance -= 1
            side += 2
        return hexes

    @classmethod
    def split(klass, value):
        '''Split value into hex.x and hex.y.'''
        value = str(value)
        length = len(value.replace('-', ''))
        if length % 2:
            raise ValueError('''Hexes can't be constructed from odd length value [%s]''' % (value, ))
        digits = length / 2
        if value.startswith('-'):  # odd length
            x, y = value[:digits + 1], value[digits + 1:]
        else:
            x, y = value[:digits], value[digits:]
        return x, y

    @classmethod
    def delta(klass, start, end):
        '''How many hexsides(0-5) between start(exlusive) and end(inclusive).'''
        # TODO:: kind of cheaty, wasteful
        return len(list(klass.rotator(start, end))) - 1

    @classmethod
    def rotate(klass, hexside, delta):
        '''Calc direction that is 'delta' clockwise rotations from hexside.'''
        hexside += delta
        while hexside > 6:
            hexside -= 6
        while hexside < 1:
            hexside += 6
        return hexside

    @classmethod
    def rotator(klass, start, end):
        '''Generator, iterates clockwise over directions, start -> end, inclusive.'''
        yield start
        while start != end:
            start = klass.rotate(start, 1)
            yield start


class BoundedHex(Hex):
    '''Same as Hex, except "map" has boundries and Hex instances outside those
    won't be returned and can't be created.
    '''
    # Boundries of map, inclusive.
    xmin = 1
    xmax = 99
    ymin = 1
    ymax = 99

    def __init__(self, x=None, y=None):
        if x is None and y is None:
            x = self.xmin
            y = self.ymin
        super(BoundedHex, self).__init__(x, y)
        if not self._valid(self):
            raise OffMapError('Out of bounds [%s].' % self)

    @classmethod
    def _valid(klas, hex):
        return not (hex.x < klas.xmin or
                    hex.y < klas.ymin or
                    hex.x > klas.xmax or
                    hex.y > klas.ymax
                    )

    def sixpack(self, *args, **kwargs):
        # Kind of hackish, inefficient. Use unbounded Hex() to do sixpack.  Then
        # loop over and strip out the out of bounds hexes.
        proxy = Hex(self)
        hexes = proxy.sixpack(*args, **kwargs)
        return set(self.__class__(h) for h in hexes if self._valid(h))

    def arc(self, *args, **kwargs):
        proxy = Hex(self.x, self.y)
        hexes = proxy.arc(*args, **kwargs)
        return set(self.__class__(h) for h in hexes if self._valid(h))
