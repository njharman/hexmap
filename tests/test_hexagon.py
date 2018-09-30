'Copyright (c) 2004-2005, 2012, 2016 Norman J. Harman Jr. njharman@gmail.com'

import unittest

import hexmap


class BaseTestCase(unittest.TestCase):
    longMessage = True

    def assertHexesEqual(self, expected, hexes, *args, **kwargs):
        for hex in hexes:
            self.assertIsInstance(hex, hexmap.Hex, *args, **kwargs)
        self.assertEqual(set(expected), set(str(h) for h in hexes), *args, **kwargs)


class HexTestCase(BaseTestCase):
    def test_creation(self):
        tests = (
            ((), 0, 0, '0000'),
            (('0000', ), 0, 0, '0000'),
            (('0234', ), 2, 34, '0234'),
            (('002034', ), 2, 34, '0234'),  # "reduces" to 0234 cause min digits is 2
            (('24', ), 2, 4, '0204'),
            (('-24', ), -2, 4, '-0204'),
            (('-02-04', ), -2, -4, '-02-04'),
            (('02-34', ), 2, -34, '02-34'),
            ((0, 1), 0, 1, '0001'),
            ((5678, ), 56, 78, '5678'),
            ((567890, ), 567, 890, '567890'),
            ((67, -89), 67, -89, '67-89'),
            ((-567, 890), -567, 890, '-567890'),
            )
        for (args, expected_x, expected_y, expected_value) in tests:
            t = hexmap.Hex(*args)
            self.assertEqual(expected_x, t.x, 'Hex(%s)' % (args, ))
            self.assertEqual(expected_y, t.y, 'Hex(%s)' % (args, ))
            self.assertEqual(expected_value, t.value, 'Hex(%s)' % (args, ))

    def test_digits(self):
        class Foo(hexmap.Hex):
            digits = 3
        tests = (
            ((), 0, 0, '000000'),
            (('0000', ), 0, 0, '000000'),
            (('0234', ), 2, 34, '002034'),
            (('002034', ), 2, 34, '002034'),  # "reduces" to 0234 cause min digits is 2
            ((1, 0), 1, 0, '001000'),
            )
        for (args, expected_x, expected_y, expected_value) in tests:
            t = Foo(*args)
            self.assertEqual(expected_x, t.x, 'Hex(%s)' % (args, ))
            self.assertEqual(expected_y, t.y, 'Hex(%s)' % (args, ))
            self.assertEqual(expected_value, t.value, 'Hex(%s)' % (args, ))

    def test_copy(self):
        t1 = hexmap.Hex('0102')
        t2 = t1.copy()
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

    def test_hashable(self):
        ahex = hexmap.Hex()
        bhex = hexmap.Hex('0101')
        chex = hexmap.Hex('0101')
        self.assertEqual(hash(bhex), hash(chex))
        # sets
        t1 = set()
        t1.add(ahex)
        t1.add(ahex)
        self.assertEqual(1, len(t1))
        t1.add(bhex)
        self.assertEqual(2, len(t1))
        t1.add(chex)
        self.assertEqual(2, len(t1))
        # dicts
        t2 = dict()
        t2[ahex] = 'boo'
        self.assertEqual(1, len(t2))
        t2[bhex] = 'boo'
        self.assertEqual(2, len(t2))
        t2[chex] = 'boo'
        self.assertEqual(2, len(t2))

    def test_equality(self):
        t = hexmap.Hex(12, 34)
        self.assertEqual(1234, t)
        self.assertEqual((12, 34), t)
        self.assertEqual('1234', t)
        self.assertEqual('012034', t)
        self.assertEqual(hexmap.Hex('1234'), t)
        self.assertNotEqual(123400, t)
        self.assertNotEqual((123, 34), t)
        self.assertNotEqual((12, 22), t)
        self.assertNotEqual('1222', t)
        self.assertNotEqual('-1234', t)
        self.assertNotEqual('12-34', t)
        self.assertNotEqual('-12-34', t)
        self.assertNotEqual(hexmap.Hex('1111'), t)
        t2 = hexmap.Hex('0101')
        self.assertEqual((1, 1), t2)
        # negative
        t = hexmap.Hex(12, -34)
        self.assertEqual((12, -34), t)
        self.assertEqual('12-34', t)
        self.assertNotEqual((12, 34), t)
        self.assertNotEqual('1234', t)

    def test_str(self):
        tests = (
                ('1234', (12, 34)),
                ('-12-34', (-12, -34)),
                ('01-01', (1, -1)),
                ('-0101', (-1, 1)),
                ('-1234', (-12, 34)),
                ('12-34', (12, -34)),
                ('1020', (10, 20)),
                ('1000', (1000, )),
                ('100000', (100, 0)),
                ('010100', (10, 100)),
                ('0000', ()),
                ('0000', ('0000', )),
                ('0101', ('0101', )),
                ('0101', ('001001', )),
                )
        for (expected, args) in tests:
            self.assertEqual(expected, str(hexmap.Hex(*args)))

    def test_sequence_stuff(self):
        # len() tuple() list() indexing
        self.assertEqual(2, len(hexmap.Hex()))
        self.assertEqual(2, len(hexmap.Hex(1231231231)))
        t = hexmap.Hex(12, 34)
        self.assertEqual((12, 34), tuple(t))
        self.assertEqual([12, 34], list(t))
        self.assertEqual(12, t[0])
        self.assertEqual(34, t[1])
        self.assertRaises(IndexError, lambda: t[3])

    def test_math(self):
        H = hexmap.Hex
        tests = (
                ('0001', '00-01', H(), H('01')),
                ('0102', '-01-02', H(), H('0102')),
                ('0713', '01-03', H('0405'), H('0308')),
                ('0713', '-0103', H('0308'), H('0405')),
                ('0103', '07-13', H('04-05'), H('-0308')),
                ('0100', '-0100', H(), ('01', '00')),
                )
        for (add, sub, a, b) in tests:
            result = a + b
            self.assertIsInstance(result, hexmap.Hex)
            self.assertEqual(add, result)
            result = b + a
            self.assertIsInstance(result, hexmap.Hex)
            self.assertEqual(add, result)
            result = a - b
            self.assertIsInstance(result, hexmap.Hex)
            self.assertEqual(sub, result)

    def test_hex_in_direction(self):
        tests = (
                ('0222', 1, '0221'),
                ('0222', 2, '0322'),
                ('0222', 3, '0323'),
                ('0222', 4, '0223'),
                ('0222', 5, '0123'),
                ('0222', 6, '0122'),
                (1519, 2, '1618'),
                (1519, 3, '1619'),
                (1519, 5, '1419'),
                )
        for (hex, direction, expected) in tests:
            t = hexmap.Hex(hex)
            result = t.hex_in_direction(direction)
            self.assertIsInstance(result, hexmap.Hex)
            self.assertEqual(expected, result)

    def test_distance_to(self):
        tests = (
                ('5454', '5454', 0),
                ('5454', '5455', 1),
                ('5454', '5554', 1),
                ('1111', '1113', 2),
                ('5554', '5952', 4),
                )
        for (from_hex, to_hex, expected) in tests:
            to = hexmap.Hex(to_hex)
            t = hexmap.Hex(from_hex)
            self.assertEqual(expected, t.distance_to(to))

    def test_sixpack(self):
        expected = ['1110', '1210', '1211', '1112', '1011', '1010']
        t = hexmap.Hex(11, 11)
        self.assertHexesEqual(expected, t.sixpack())
        self.assertHexesEqual(expected, t.sixpack(1))
        expected.append('1111')
        self.assertHexesEqual(expected, t.sixpack(include_self=True))
        expected2 = ['1508', '1608', '1609', '1510', '1409', '1408', '1507', '1607', '1708', '1709', '1710', '1610', '1511', '1410', '1310', '1309', '1308', '1407']
        t2 = hexmap.Hex('1509')
        self.assertHexesEqual(expected2, t2.sixpack(2))

    def test_arc(self):
        data = (
            (('5512', ), 0, 1, 2, []),
            (('5512', ), 0, 5, 4, []),
            (('5512', ), 2, 1, 2, ['5511', '5611', '5510', '5610', '5711']),
            (('2211', ), 1, 1, 6, ['2210', '2311', '2312', '2212', '2112', '2111']),
            # arc(1,6) has less hexes than you may think, 1 less in fact, no 1407.
            (('1509', ), 2, 1, 6, ['1508', '1608', '1609', '1510', '1409', '1408', '1507', '1607', '1708', '1709', '1710', '1610', '1511', '1410', '1310', '1309', '1308']),
            ((1117, ), 3, 5, 6, ['1017', '1016', '0918', '0917', '0916', '0818', '0817', '0816', '0815']),
            (('0318', ), 2, 1, 2, ['0317', '0417', '0316', '0416', '0517']),
            (('0322', ), 2, 2, 4, ['0422', '0421', '0323', '0523', '0522', '0423', '0521', '0324']),
            ((1117, ), 3, 5, 1, ['1017', '1016', '1116', '0918', '0917', '0916', '1015', '1115', '0818', '0817', '0816', '0815', '0915', '1014', '1114']),
            (('0322', ), 2, 2, 5, ['0421', '0422', '0323', '0222', '0521', '0522', '0523', '0423', '0324', '0223', '0123']),
            ((1117, ), 3, 5, 2, ['1017', '1016', '1116', '1216', '0918', '0917', '0916', '1015', '1115', '1215', '1316', '0818', '0817', '0816', '0815', '0915', '1014', '1114', '1214', '1315', '1415']),
            (('0703', ), 1, 1, 2, ['0702', '0802', ]),
            )
        for (args, distance, start, end, expected) in data:
            t = hexmap.Hex(*args)
            hexes = t.arc(start, end, distance)
            self.assertHexesEqual(expected, hexes, msg='\nhex:%s from %s to %s, distance %s -> %s' % (t, start, end, distance, sorted(str(h) for h in hexes)))
        t = hexmap.Hex('5512')
        hexes = t.arc(5, 4, 0, True)
        self.assertHexesEqual(['5512', ], hexes)

    def test_half_arc(self):
        data = (
            (('0322',), 2, (2, 3, 4), ['0421', '0420', '0422', '0323', '0223', '0522', '0521', '0520', '0519', '0523', '0423', '0324', '0224', '0125']),
            ((1117,), 3, (6, 1, 2), ['1016', '0917', '1116', '1216', '1317', '1015', '0916', '0816', '0717', '1115', '1215', '1316', '1416', '1517', '1014', '0915', '0815', '0716', '0616', '0517', '1114', '1214', '1315', '1415', '1516', '1616', '1717']),
            )
        for (args, distance, directions, expected) in data:
            t = hexmap.Hex(*args)
            hexes = t.half_arc(directions, distance)
            self.assertHexesEqual(expected, hexes, msg='\nhex:%s %s, distance %s -> %s' % (t, directions, distance, sorted(str(h) for h in hexes)))

    def test_hexsides_to(self):
        tests = (
                # from,       to,        (list of faces)
                (('5554', ), ('5554', ), (1, 2, 3, 4, 5, 6)),
                (('0000', ), ('0000', ), (1, 2, 3, 4, 5, 6)),
                # odd, even sixpack
                (('5554', ), ('5553', ), (1, )),
                (('5554', ), ('5653', ), (2, )),
                (('5554', ), ('5654', ), (3, )),
                (('5554', ), ('5555', ), (4, )),
                (('5554', ), ('5454', ), (5, )),
                (('5554', ), ('5453', ), (6, )),
                # even, odd sixpack
                (('5211', ), ('5210', ), (1, )),
                (('5211', ), ('5311', ), (2, )),
                (('5211', ), ('5312', ), (3, )),
                (('5211', ), ('5212', ), (4, )),
                (('5211', ), ('5112', ), (5, )),
                (('5211', ), ('5111', ), (6, )),
                # even, even sixpack
                (('5414', ), ('5413', ), (1, )),
                (('5414', ), ('5514', ), (2, )),
                (('5414', ), ('5515', ), (3, )),
                (('5414', ), ('5415', ), (4, )),
                (('5414', ), ('5315', ), (5, )),
                (('5414', ), ('5314', ), (6, )),
                # origin sixpack
                (('0000', ), (0, -1), (1, )),
                (('0000', ), (1, 0), (2, )),
                (('0000', ), (1, 1), (3, )),
                (('0000', ), (0, 1), (4, )),
                (('0000', ), (-1, 1), (5, )),
                (('0000', ), (-1, 0), (6, )),
                # 2 hexes straight line
                (('5554', ), ('5753', ), (2, )),
                (('5554', ), ('5755', ), (3, )),
                (('5554', ), ('5355', ), (5, )),
                (('5554', ), ('5353', ), (6, )),
                # along a vertex
                (('5554', ), ('5652', ), (1, 2)),
                (('5554', ), ('5754', ), (2, 3)),
                (('5554', ), ('5655', ), (3, 4)),
                (('5554', ), ('5455', ), (4, 5)),
                (('5554', ), ('5354', ), (5, 6)),
                (('5554', ), ('5452', ), (6, 1)),
                # 2 hexes out, one over
                (('5554', ), ('5651', ), (1, )),
                (('5554', ), ('5451', ), (1, )),
                (('5554', ), ('5853', ), (2, )),
                (('5554', ), ('5752', ), (2, )),
                (('5554', ), ('5854', ), (3, )),
                (('5554', ), ('5756', ), (3, )),
                (('5554', ), ('5656', ), (4, )),
                (('5554', ), ('5456', ), (4, )),
                (('5554', ), ('5356', ), (5, )),
                (('5554', ), ('5254', ), (5, )),
                (('5554', ), ('5253', ), (6, )),
                (('5554', ), ('5352', ), (6, )),
                # way out
                (('00010001', ), ('99990002', ), (3, )),
                (('00010001', ), ('99990000', ), (2, )),
                (('00010001', ), ('00029999', ), (4, )),
                # even row
                (('5653', ), ('5753', ), (2, )),
                (('5653', ), ('5953', ), (2, )),
                (('5653', ), ('5851', ), (2, )),
                (('5653', ), ('6251', ), (2, )),
                (('5653', ), ('6153', ), (2, )),
                (('5653', ), ('5553', ), (6, )),
                (('02020001', ), ('02039999', ), (4, )),
                # negatives
                ((-55, 54), (-55, 53), (1, )),
                ((55, -54), (56, -55), (2, )),
                ((55, -54), (56, -54), (3, )),
                ((55, -54), (55, -53), (4, )),
                ((-55, 54), (-56, 54), (5, )),
                ((-55, 54), (-56, 53), (6, )),
                )
        for (from_args, to_args, expected) in tests:
            from_hex = hexmap.Hex(*from_args)
            to_hex = hexmap.Hex(*to_args)
            results = from_hex.hexsides_to(to_hex)
            if expected != results:
                self.fail('Got %s not %s from %s to %s' % (results, expected, from_hex, to_hex))

    def test_delta(self):
        tests = (
                (0, 1, 1),
                (1, 1, 2),
                (2, 1, 3),
                (3, 1, 4),
                (4, 1, 5),
                (5, 1, 6),
                (1, 2, 3),
                (1, 3, 4),
                (5, 6, 5),
                (4, 4, 2),
                )
        t = hexmap.Hex()
        for (expected, start, end) in tests:
            self.assertEqual(expected, t.delta(start, end), 'start: %s end: %s' % (start, end))

    def test_rotate(self):
        tests = (
                (1, 1, 0),
                (2, 1, 1),
                (6, 1, 5),
                (1, 1, 6),
                (1, 1, 12),
                (6, 1, 11),
                (6, 1, -1),
                (2, 1, -5),
                (1, 1, -6),
                (1, 1, -12),
                (2, 1, -11),
                (3, 3, 0),
                (4, 3, 1),
                (2, 3, 5),
                (3, 3, 6),
                (3, 3, 12),
                (2, 3, 11),
                (2, 3, -1),
                (4, 3, -5),
                (3, 3, -6),
                (3, 3, -12),
                (4, 3, -11),
                )
        t = hexmap.Hex()
        for (expected, hexside, delta) in tests:
            self.assertEqual(expected, t.rotate(hexside, delta), 'start: %s rotate: %s' % (hexside, delta))

    def test_rotator(self):
        tests = (
                (1, 1, (1, )),
                (1, 2, (1, 2, )),
                (1, 3, (1, 2, 3, )),
                (1, 4, (1, 2, 3, 4, )),
                (1, 5, (1, 2, 3, 4, 5, )),
                (1, 6, (1, 2, 3, 4, 5, 6)),
                (2, 2, (2, )),
                (2, 4, (2, 3, 4)),
                (4, 2, (4, 5, 6, 1, 2)),
                (6, 1, (6, 1)),
                )
        t = hexmap.Hex()
        for (start, end, expected) in tests:
            result = list(t.rotator(start, end))
            self.assertSequenceEqual(expected, result, 'start: %s end: %s' % (start, end))


class BoundedHexTestCase(BaseTestCase):
    def test_creation(self):
        tests = (
            ((), 1, 1, '0101'),
            ((1, 1), 1, 1, '0101'),
            (('0234', ), 2, 34, '0234'),
            (('002034', ), 2, 34, '0234'),
            (('24', ), 2, 4, '0204'),
            ((5678, ), 56, 78, '5678'),
            )
        for (args, expected_x, expected_y, expected_value) in tests:
            t = hexmap.BoundedHex(*args)
            self.assertEqual(expected_x, t.x, 'Hex(%s)' % (args, ))
            self.assertEqual(expected_y, t.y, 'Hex(%s)' % (args, ))
            self.assertEqual(expected_value, t.value, 'Hex(%s)' % (args, ))
        fail = (
            (0, 1, ),
            ('0000', ),
            (567890, ),
            ('-24', ),
            ('-02-04', ),
            ('02-34', ),
            (67, -89, ),
            (-567, 890, ),
            )
        for args in fail:
            self.assertRaises(ValueError, hexmap.BoundedHex, *args)

    def test_hex_in_direction(self):
        tests = (
                ('0101', 1, None),
                ('0101', 2, None),
                ('0101', 3, '0201'),
                ('0101', 4, '0102'),
                ('0101', 5, None),
                ('0101', 6, None),
                ('9999', 1, '9998'),
                ('9999', 2, None),
                ('9999', 3, None),
                ('9999', 4, None),
                ('9999', 5, '9899'),
                ('9999', 6, '9898'),
                )
        for (hex, direction, expected) in tests:
            t = hexmap.BoundedHex(hex)
            if expected is None:
                self.assertRaises(hexmap.OffMapError, t.hex_in_direction, direction)
            else:
                result = t.hex_in_direction(direction)
                self.assertIsInstance(result, hexmap.BoundedHex)
                self.assertEqual(expected, result)

    def test_sixpack(self):
        expected = ['0201', '0102', ]
        t = hexmap.BoundedHex()
        self.assertHexesEqual(expected, t.sixpack())
        self.assertHexesEqual(expected, t.sixpack(1))
        expected.append('0101')
        self.assertHexesEqual(expected, t.sixpack(include_self=True))
        expected2 = ['0801', '0702', '0601', '0901', '0902', '0802', '0703', '0602', '0502', '0501', ]
        t2 = hexmap.BoundedHex('0701')
        self.assertHexesEqual(expected2, t2.sixpack(2))

    def test_arc(self):
        data = (
            (('5512', ), 0, 1, 2, []),
            (('5512', ), 0, 5, 4, []),
            (('5512', ), 2, 1, 2, ['5511', '5611', '5510', '5610', '5711']),
            (('2211', ), 1, 1, 6, ['2210', '2311', '2312', '2212', '2112', '2111']),
            # arc(1,6) has less hexes than you may think, 1 less in fact, no 1407.
            (('1509', ), 2, 1, 6, ['1508', '1608', '1609', '1510', '1409', '1408', '1507', '1607', '1708', '1709', '1710', '1610', '1511', '1410', '1310', '1309', '1308']),
            ((1117, ), 3, 5, 6, ['1017', '1016', '0918', '0917', '0916', '0818', '0817', '0816', '0815']),
            (('0318', ), 2, 1, 2, ['0317', '0417', '0316', '0416', '0517']),
            (('0322', ), 2, 2, 4, ['0422', '0421', '0323', '0523', '0522', '0423', '0521', '0324']),
            ((1117, ), 3, 5, 1, ['1017', '1016', '1116', '0918', '0917', '0916', '1015', '1115', '0818', '0817', '0816', '0815', '0915', '1014', '1114']),
            (('0322', ), 2, 2, 5, ['0421', '0422', '0323', '0222', '0521', '0522', '0523', '0423', '0324', '0223', '0123']),
            ((1117, ), 3, 5, 2, ['1017', '1016', '1116', '1216', '0918', '0917', '0916', '1015', '1115', '1215', '1316', '0818', '0817', '0816', '0815', '0915', '1014', '1114', '1214', '1315', '1415']),
            (('0703', ), 1, 1, 2, ['0702', '0802', ]),
            )
        for (args, distance, start, end, expected) in data:
            t = hexmap.BoundedHex(*args)
            hexes = t.arc(start, end, distance)
            self.assertHexesEqual(expected, hexes, msg='\nhex:%s from %s to %s, distance %s -> %s' % (t, start, end, distance, sorted(str(h) for h in hexes)))
        t = hexmap.BoundedHex('5512')
        hexes = t.arc(5, 4, 0, True)
        self.assertHexesEqual(['5512', ], hexes)
