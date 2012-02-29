import pandas._tseries as lib
from datetime import datetime

from pandas.core.index import DatetimeIndex
from pandas.core.frame import DataFrame

import unittest
import numpy as np

from pandas import Series

from numpy.random import rand

from pandas.util.testing import assert_series_equal

from pandas.core.groupby import Tinterval
from pandas.core.datetools import Minute

class TestDatetime64(unittest.TestCase):

    def setUp(self):
        dti = DatetimeIndex(start=datetime(2005,1,1),
                            end=datetime(2005,1,10), offset='Min')

        self.series = Series(rand(len(dti)), dti)


    def test_yearoffset(self):
        off = lib.YearOffset(dayoffset=0, biz=0, anchor=datetime(2002,1,1))

        for i in range(500):
            t = lib.Timestamp(off.ts)
            self.assert_(t.day == 1)
            self.assert_(t.month == 1)
            self.assert_(t.year == 2002 + i)
            off.next()

        for i in range(499, -1, -1):
            off.prev()
            t = lib.Timestamp(off.ts)
            self.assert_(t.day == 1)
            self.assert_(t.month == 1)
            self.assert_(t.year == 2002 + i)

        off = lib.YearOffset(dayoffset=-1, biz=0, anchor=datetime(2002,1,1))

        for i in range(500):
            t = lib.Timestamp(off.ts)
            self.assert_(t.month == 12)
            self.assert_(t.day == 31)
            self.assert_(t.year == 2001 + i)
            off.next()

        for i in range(499, -1, -1):
            off.prev()
            t = lib.Timestamp(off.ts)
            self.assert_(t.month == 12)
            self.assert_(t.day == 31)
            self.assert_(t.year == 2001 + i)

        off = lib.YearOffset(dayoffset=-1, biz=-1, anchor=datetime(2002,1,1))

        stack = []

        for i in range(500):
            t = lib.Timestamp(off.ts)
            stack.append(t)
            self.assert_(t.month == 12)
            self.assert_(t.day == 31 or t.day == 30 or t.day == 29)
            self.assert_(t.year == 2001 + i)
            self.assert_(t.weekday() < 5)
            off.next()

        for i in range(499, -1, -1):
            off.prev()
            t = lib.Timestamp(off.ts)
            self.assert_(t == stack.pop())
            self.assert_(t.month == 12)
            self.assert_(t.day == 31 or t.day == 30 or t.day == 29)
            self.assert_(t.year == 2001 + i)
            self.assert_(t.weekday() < 5)

    def test_monthoffset(self):
        off = lib.MonthOffset(dayoffset=0, biz=0, anchor=datetime(2002,1,1))

        for i in range(12):
            t = lib.Timestamp(off.ts)
            self.assert_(t.day == 1)
            self.assert_(t.month == 1 + i)
            self.assert_(t.year == 2002)
            off.next()

        for i in range(11, -1, -1):
            off.prev()
            t = lib.Timestamp(off.ts)
            self.assert_(t.day == 1)
            self.assert_(t.month == 1 + i)
            self.assert_(t.year == 2002)

        off = lib.MonthOffset(dayoffset=-1, biz=0, anchor=datetime(2002,1,1))

        for i in range(12):
            t = lib.Timestamp(off.ts)
            self.assert_(t.day >= 28)
            self.assert_(t.month == (12 if i == 0 else i))
            self.assert_(t.year == 2001 + (i != 0))
            off.next()

        for i in range(11, -1, -1):
            off.prev()
            t = lib.Timestamp(off.ts)
            self.assert_(t.day >= 28)
            self.assert_(t.month == (12 if i == 0 else i))
            self.assert_(t.year == 2001 + (i != 0))

        off = lib.MonthOffset(dayoffset=-1, biz=-1, anchor=datetime(2002,1,1))

        stack = []

        for i in range(500):
            t = lib.Timestamp(off.ts)
            stack.append(t)
            if t.month != 2:
                self.assert_(t.day >= 28)
            else:
                self.assert_(t.day >= 26)
            self.assert_(t.weekday() < 5)
            off.next()

        for i in range(499, -1, -1):
            off.prev()
            t = lib.Timestamp(off.ts)
            self.assert_(t == stack.pop())
            if t.month != 2:
                self.assert_(t.day >= 28)
            else:
                self.assert_(t.day >= 26)
            self.assert_(t.weekday() < 5)

        for i in (-2, -1, 1, 2):
            for j in (-1, 0, 1):
                off1 = lib.MonthOffset(dayoffset=i, biz=j, stride=12,
                                       anchor=datetime(2002,1,1))
                off2 = lib.YearOffset(dayoffset=i, biz=j,
                                      anchor=datetime(2002,1,1))

                for k in range(500):
                    self.assert_(off1.ts == off2.ts)
                    off1.next()
                    off2.next()

                for k in range(500):
                    self.assert_(off1.ts == off2.ts)
                    off1.prev()
                    off2.prev()

    def test_dayoffset(self):
        off = lib.DayOffset(biz=0, anchor=datetime(2002,1,1))

        us_in_day = 1e6 * 60 * 60 * 24

        t0 = lib.Timestamp(off.ts)
        for i in range(500):
            off.next()
            t1 = lib.Timestamp(off.ts)
            self.assert_(t1.value - t0.value == us_in_day)
            t0 = t1

        t0 = lib.Timestamp(off.ts)
        for i in range(499, -1, -1):
            off.prev()
            t1 = lib.Timestamp(off.ts)
            self.assert_(t0.value - t1.value == us_in_day)
            t0 = t1

        off = lib.DayOffset(biz=1, anchor=datetime(2002,1,1))

        t0 = lib.Timestamp(off.ts)
        for i in range(500):
            off.next()
            t1 = lib.Timestamp(off.ts)
            self.assert_(t1.weekday() < 5)
            self.assert_(t1.value - t0.value == us_in_day or
                         t1.value - t0.value == 3 * us_in_day)
            t0 = t1

        t0 = lib.Timestamp(off.ts)
        for i in range(499, -1, -1):
            off.prev()
            t1 = lib.Timestamp(off.ts)
            self.assert_(t1.weekday() < 5)
            self.assert_(t0.value - t1.value == us_in_day or
                         t0.value - t1.value == 3 * us_in_day)
            t0 = t1


    def test_dayofmonthoffset(self):
        for week in (-1, 0, 1):
            for day in (0, 2, 4):
                off = lib.DayOfMonthOffset(week=-1, day=day, 
                                           anchor=datetime(2002,1,1))

                stack = []

                for i in range(500):
                    t = lib.Timestamp(off.ts)
                    stack.append(t)
                    self.assert_(t.weekday() == day) 
                    off.next()

                for i in range(499, -1, -1):
                    off.prev()
                    t = lib.Timestamp(off.ts)
                    self.assert_(t == stack.pop())
                    self.assert_(t.weekday() == day)

    def test_datetimeindex_accessors(self):
        dti = DatetimeIndex(offset='Q@JAN', start=datetime(1997,12,31),
                            periods=100)

        self.assertEquals(dti.year[0], 1998)
        self.assertEquals(dti.month[0], 1)
        self.assertEquals(dti.day[0], 31)
        self.assertEquals(dti.hour[0], 0)
        self.assertEquals(dti.minute[0], 0)
        self.assertEquals(dti.second[0], 0)
        self.assertEquals(dti.microsecond[0], 0)
        self.assertEquals(dti.dayofweek[0], 5)

        self.assertEquals(dti.dayofyear[0], 31)
        self.assertEquals(dti.dayofyear[1], 120) 

        self.assertEquals(dti.weekofyear[0], 5)
        self.assertEquals(dti.weekofyear[1], 18) 

        self.assertEquals(dti.quarter[0], 1)
        self.assertEquals(dti.quarter[1], 2)

        self.assertEquals(len(dti.year), 100)
        self.assertEquals(len(dti.month), 100)
        self.assertEquals(len(dti.day), 100)
        self.assertEquals(len(dti.hour), 100)
        self.assertEquals(len(dti.minute), 100)
        self.assertEquals(len(dti.second), 100)
        self.assertEquals(len(dti.microsecond), 100)
        self.assertEquals(len(dti.dayofweek), 100)
        self.assertEquals(len(dti.dayofyear), 100)
        self.assertEquals(len(dti.weekofyear), 100)
        self.assertEquals(len(dti.quarter), 100)

    def test_datetimeindex_diff(self):
        dti1 = DatetimeIndex(offset='Q@JAN', start=datetime(1997,12,31),
                             periods=100)
        dti2 = DatetimeIndex(offset='Q@JAN', start=datetime(1997,12,31),
                             periods=98)
        self.assert_( len(dti1.diff(dti2)) == 2)

    def test_datetimecache(self):
        lib.flush_tcache('W@TUE')

        tc = lib.get_tcache('W@TUE', first = datetime(2004,1,6),
                            last = datetime(2004,12,28))
        cache = tc.cache()

        self.assert_(lib.Timestamp(cache[0]) == datetime(2004,1,6))
        self.assert_(lib.Timestamp(cache[-1]) == datetime(2004,12,28))

        cache = tc.extend(cache[0], cache[-1], 1)

        self.assert_(lib.Timestamp(cache[0]) == datetime(2003,12,30))
        self.assert_(lib.Timestamp(cache[-1]) == datetime(2005,1,4))

        cache = tc.extend(cache[0], cache[-1], 1)

        self.assert_(lib.Timestamp(cache[0]) == datetime(2003,12,23))
        self.assert_(lib.Timestamp(cache[-1]) == datetime(2005,1,11))

        lib.flush_tcache('W@TUE')

    def test_fancy_getitem(self):
        dti = DatetimeIndex(offset='WOM@1FRI', start=datetime(2005,1,1),
                            end=datetime(2010,1,1))

        s = Series(np.arange(len(dti)), index=dti) 

        self.assertEquals(s[48], 48)
        self.assertEquals(s['1/2/2009'], 48)
        self.assertEquals(s['2009-1-2'], 48)
        self.assertEquals(s[datetime(2009,1,2)], 48)
        self.assertEquals(s[lib.Timestamp(datetime(2009,1,2))], 48)
        self.assertRaises(KeyError, s.__getitem__, '2009-1-3') 

        assert_series_equal(s['3/6/2009':'2009-06-05'],
                            s[datetime(2009,3,6):datetime(2009,6,5)])

    def test_fancy_setitem(self):
        dti = DatetimeIndex(offset='WOM@1FRI', start=datetime(2005,1,1),
                            end=datetime(2010,1,1))

        s = Series(np.arange(len(dti)), index=dti) 
        s[48] = -1
        self.assertEquals(s[48], -1)
        s['1/2/2009'] = -2
        self.assertEquals(s[48], -2)
        s['1/2/2009':'2009-06-05'] = -3
        self.assert_((s[48:54] == -3).all())

    def test_custom_grouper(self):

        dti = DatetimeIndex(offset='Min', start=datetime(2005,1,1),
                            end=datetime(2005,1,10))

        data = np.array([1]*len(dti))
        s = Series(data, index=dti)

        b = Tinterval(Minute(5))
        g = s.groupby(b)

        self.assertEquals(g.ngroups, 2593)

        # construct expected val
        arr = [5] * 2592
        arr.append(1)
        idx = dti[0:-1:5]
        idx = idx.append(DatetimeIndex([np.datetime64(dti[-1])]))
        expect = Series(arr, index=idx)

        result = g.agg(np.sum)
        assert_series_equal(result, expect)

        data = np.random.rand(len(dti), 10)
        df = DataFrame(data, index=dti)
        r = df.groupby(b).agg(np.sum)

        self.assertEquals(len(r.columns), 10)
        self.assertEquals(len(r.index), 2593)

    def test_convert_basic(self):
        s = self.series

        result = s.convert('5Min')

        grouper = Tinterval(Minute(5), closed='right', label='right')
        expect = s.groupby(grouper).agg(lambda x: x[-1])

        assert_series_equal(result, expect)

        # from daily
        dti = DatetimeIndex(start=datetime(2005,1,1), 
                            end=datetime(2005,1,10), offset='D')

        s = Series(rand(len(dti)), dti)

        # to weekly
        result = s.convert('W') # implicitly @SUN

        self.assertEquals(len(result), 3)
        self.assert_((result.index.dayofweek == [6,6,6]).all())
        self.assertEquals(result.irow(0), s['1/2/2005'])
        self.assertEquals(result.irow(1), s['1/9/2005'])
        self.assertEquals(result.irow(2), s.irow(-1))

        result = s.convert('W@MON')
        self.assertEquals(len(result), 2)
        self.assert_((result.index.dayofweek == [0,0]).all())
        self.assertEquals(result.irow(0), s['1/3/2005'])
        self.assertEquals(result.irow(1), s['1/10/2005'])

        result = s.convert('W@TUE')
        self.assertEquals(len(result), 2)
        self.assert_((result.index.dayofweek == [1,1]).all())
        self.assertEquals(result.irow(0), s['1/4/2005'])
        self.assertEquals(result.irow(1), s['1/10/2005'])

        result = s.convert('W@WED')
        self.assertEquals(len(result), 2)
        self.assert_((result.index.dayofweek == [2,2]).all())
        self.assertEquals(result.irow(0), s['1/5/2005'])
        self.assertEquals(result.irow(1), s['1/10/2005'])

        result = s.convert('W@THU')
        self.assertEquals(len(result), 2)
        self.assert_((result.index.dayofweek == [3,3]).all())
        self.assertEquals(result.irow(0), s['1/6/2005'])
        self.assertEquals(result.irow(1), s['1/10/2005'])

        result = s.convert('W@FRI')
        self.assertEquals(len(result), 2)
        self.assert_((result.index.dayofweek == [4,4]).all())
        self.assertEquals(result.irow(0), s['1/7/2005'])
        self.assertEquals(result.irow(1), s['1/10/2005'])

        # to biz day
        result = s.convert('B')
        self.assertEquals(len(result), 6)
        self.assert_((result.index.dayofweek == [0,1,2,3,4,0]).all())
        self.assertEquals(result.irow(0), s['1/3/2005'])
        self.assertEquals(result.irow(1), s['1/4/2005'])
        self.assertEquals(result.irow(5), s['1/10/2005'])

    def test_convert_upsample(self):
        # from daily
        dti = DatetimeIndex(start=datetime(2005,1,1), 
                            end=datetime(2005,1,10), offset='D')

        s = Series(rand(len(dti)), dti)

        # to minutely, by padding
        result = s.convert('Min', method='pad')
        self.assertEquals(len(result), 12961)
        self.assertEquals(result[0], s[0])
        self.assertEquals(result[-1], s[-1])

    def test_convert_olhc(self):
        s = self.series

        grouper = Tinterval(Minute(5), closed='right', label='right')
        expect = s.groupby(grouper).agg(lambda x: x[-1])
        result = s.convert('5Min', how='ohlc')

        self.assertEquals(len(result), len(expect))
        self.assertEquals(len(result.columns), 4)
        
        xs = result.irow(-1)
        self.assertEquals(xs['open'], s[-5])
        self.assertEquals(xs['high'], s[-5:].max())
        self.assertEquals(xs['low'], s[-5:].min())
        self.assertEquals(xs['close'], s[-1])

        xs = result.irow(1)
        self.assertEquals(xs['open'], s[1])
        self.assertEquals(xs['high'], s[1:6].max())
        self.assertEquals(xs['low'], s[1:6].min())
        self.assertEquals(xs['close'], s[5])

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)