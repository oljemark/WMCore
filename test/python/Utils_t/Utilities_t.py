#!/usr/bin/env python
"""
Unittests for Utilities functions
"""

from builtins import object
import os
import tempfile
import unittest

from Utils.Utilities import makeList, makeNonEmptyList, strToBool, \
    safeStr, rootUrlJoin, zipEncodeStr, lowerCmsHeaders, getSize, \
    encodeUnicodeToBytes, diskUse, numberCouchProcess, normalize_spaces, \
    extractFromXML


class UtilitiesTests(unittest.TestCase):
    """
    unittest for Utilities functions
    """

    def testMakeList(self):
        """
        Test the makeList function
        """
        self.assertEqual(makeList([]), [])
        self.assertEqual(makeList(""), [])
        self.assertEqual(makeList(['123']), ['123'])
        self.assertEqual(makeList([456]), [456])
        self.assertListEqual(makeList(['123', 456, '789']), ['123', 456, '789'])

        self.assertEqual(makeList('123'), ['123'])
        self.assertEqual(makeList('123'), ['123'])
        self.assertListEqual(makeList('123,456'), ['123', '456'])
        self.assertListEqual(makeList('123,456'), ['123', '456'])
        self.assertListEqual(makeList('["aa","bb","cc"]'), ['aa', 'bb', 'cc'])
        self.assertListEqual(makeList(' ["aa", "bb", "cc"] '), ['aa', 'bb', 'cc'])

        self.assertRaises(ValueError, makeList, 123)
        self.assertRaises(ValueError, makeList, 123.456)
        self.assertRaises(ValueError, makeList, {1: 123})

    def testLowerCmsHeaders(self):
        "Test lowerCmsHeaders function"
        val = 'cms-xx-yy'
        headers = {'CAPITAL': 1, 'Camel': 1, 'Cms-Xx-Yy': val, 'CMS-XX-YY': val, 'cms-xx-yy': val}
        lheaders = lowerCmsHeaders(headers)
        self.assertEqual(sorted(lheaders.keys()), sorted(['CAPITAL', 'Camel', val]))
        self.assertEqual(lheaders['CAPITAL'], 1)
        self.assertEqual(lheaders['Camel'], 1)
        self.assertEqual(lheaders[val], val)
        self.assertEqual(len(lheaders), 3)

    def testMakeNonEmptyList(self):
        """
        Test the makeNonEmptyList function.
        It has exactly the same behaviour as makeList, but throws an exception
        for empty list or string.
        """
        self.assertEqual(makeList(['123']), makeNonEmptyList(['123']))
        self.assertListEqual(makeList(['123', 456, '789']), makeNonEmptyList(['123', 456, '789']))

        self.assertListEqual(makeList('123,456'), makeNonEmptyList('123, 456'))
        self.assertListEqual(makeList('["aa","bb","cc"]'), makeNonEmptyList('["aa", "bb", "cc"]'))

        self.assertRaises(ValueError, makeNonEmptyList, [])
        self.assertRaises(ValueError, makeNonEmptyList, "")

    def testStrToBool(self):
        """
        Test the strToBool function.
        """
        for v in [True, "True", "TRUE", "true"]:
            self.assertTrue(strToBool(v))
        for v in [False, "False", "FALSE", "false"]:
            self.assertFalse(strToBool(v))

        for v in [1, 0, "", "alan", [], [''], {'a': 123}]:
            self.assertRaises(ValueError, strToBool, v)

    def testSafeStr(self):
        """
        Test the safeStr function.
        """
        for v in ['123', '123', 123]:
            self.assertEqual(safeStr(v), '123')
        self.assertEqual(safeStr(123.45), '123.45')
        self.assertEqual(safeStr(False), 'False')
        self.assertEqual(safeStr(None), 'None')
        self.assertEqual(safeStr(""), "")

        for v in [[1, 2], {'x': 123}, set([1])]:
            self.assertRaises(ValueError, safeStr, v)

    def testRootUrlJoin(self):
        """
        Test the testRootUrlJoin function.
        """
        urlbase = "root://site.domain//somepath"
        self.assertEqual(rootUrlJoin(urlbase, "extend"), "root://site.domain//somepath/extend")
        urlbase = "random"
        self.assertEqual(rootUrlJoin(urlbase, "extend"), None)
        urlbase = None
        self.assertEqual(rootUrlJoin(urlbase, "extend"), None)

    def testZipEncodeStr(self):
        """
        Test the zipEncodeStr function.
        """
        message = """
%MSG-s CMSException:  AfterFile 02-Jun-2010 14:31:43 CEST PostEndRun
cms::Exception caught in cmsRun
---- EventProcessorFailure BEGIN
EventProcessingStopped
---- ScheduleExecutionFailure BEGIN
ProcessingStopped
---- InvalidReference BEGIN
BadRefCore Attempt to dereference a RefCore containing an invalid
ProductID has been detected. Please modify the calling
code to test validity before dereferencing.
cms::Exception going through module PatMCMatching/analyzePatMCMatching run: 1 lumi: 666672 event: 305
---- InvalidReference END
Exception going through path p
---- ScheduleExecutionFailure END
an exception occurred during current event processing
cms::Exception caught in CMS.EventProcessor and rethrown
---- EventProcessorFailure END
"""
        encodedMessage = \
            'eNp1j8FqwzAMhu95Cl0G2yEhaXvyrU3dkkFHqfcCnq02hkQOtlz6+HM2MrbDdBLS9/1CxdNJHcsI7UnJh8GJnScBsL0yhoMbEOpV+ZqoXNVNDc1GrBuxWUMr1TucfWRJ9pKoMGMU4scHo9OtZ3C5G+O8L3OBvCPxOXiDMfpw0G5IAWEnj91b8Xvn6KbYTxPab0+ZHm0aUD7QpDn/r/qP1dFdD85e8IoBySz0Ts+j1md9y4zjxMAebGYWTsMCGE+sHeVk0JS/+Qqc79lkuNtDryN8IBLAc1VVL5+o0W8i'
        encodedMessage = encodeUnicodeToBytes(encodedMessage)
        self.assertEqual(zipEncodeStr(message, maxLen=300, compressLevel=9, steps=10, truncateIndicator=" (...)"),
                         encodedMessage)
        # Test different maximum lengths
        # Encoded message should always be less than the maximum limit.
        for maxLen in (800, 500, 20):
            self.assertLessEqual(
                    len(zipEncodeStr(message, maxLen=maxLen, compressLevel=9, steps=10, truncateIndicator=" (...)")),
                    maxLen)

    def testGetSize(self):
        """
        Test the getSize function.
        """
        for item in (1234, 1234.1234, set([12, 34]), "test", (1, 2), {'k1': 'v1'}):
            self.assertTrue(getSize(item) > 20)
        with self.assertRaises(TypeError):
            getSize(zipEncodeStr)

        class TestClass1():
            def __init__(self):
                self.data = "blah"

        cls1 = TestClass1()
        print(getSize(cls1)) # py2: 1129, py3: 205
        self.assertTrue(getSize(cls1) > 200)

        class TestClass2(object):
            """
            In python2, classes that inherit from `object` have a smaller
            memory footprint
            """
            def __init__(self):
                self.data = "blah"

        cls2 = TestClass2()
        print(getSize(cls2)) # py2: 426, py3: 205
        self.assertTrue(getSize(cls2) > 200)

    def testDiskUse(self):
        """
        Test the `diskUse` function.
        """
        data = diskUse()

        # `data` is a list of dictionaries with three keys each:
        # [
        #   {
        #    "filesystem": "devtmpfs",
        #    "mounted": "/dev",
        #    "percent": "0%"
        #  },
        #  {
        #    "filesystem": "/dev/vda1",
        #    "mounted": "/",
        #    "percent": "76%"
        #  }
        #  [...]
        # ]
        print(data)

        # assuming nodes will always have at least 3 partitions/mount points
        self.assertTrue(len(data) > 2)

        # - 1. every dictionary in the list needs to contain all of the 
        #   expexted keys and their values must be a non-empty string
        # - 2. the value of the "percent" key needs to be either "100" 
        #   or a one or two digits int, followed by a percentage character "%"
        # - 3. there must be at least one entry whose filesystem contains `/dev/*`
        filesystem_is_dev = 0
        for entry in data:
            print(entry)

            # check 1.
            self.assertTrue("filesystem" in entry)
            self.assertTrue("mounted" in entry)
            self.assertTrue("percent" in entry)
            for value in entry.values():
                self.assertTrue(isinstance(value, str))
                self.assertTrue(len(value) > 0)

            import re
            # ref: https://docs.python.org/3/library/re.html#re.search
            # re.search() returns None if no position in the string matches the pattern

            # check 2.
            self.assertTrue(re.search("^(100|[0-9]{1,2})%$", entry["percent"]) is not None)

            # check 3.
            if re.search("^/dev/.+$" , entry["filesystem"]):
                filesystem_is_dev += 1

        self.assertTrue(filesystem_is_dev > 0)

    def testNormalizeSpaces(self):
        """
        Test the `normalize_spaces` function.
        """
        data = normalize_spaces("bla bla     bla    ")
        expect = "bla bla bla"
        self.assertEqual(data, expect)

    def testNumberCouchProcess(self):
        """
        Test the `numberCouchProcess` function.
        """
        data = numberCouchProcess()
        # there should be at least one process, but who knows...
        self.assertTrue(data >= 0)

    def testExtractFromXML(self):
        """Test extracting an existing element from XML."""

        # create new xmlContent file
        xmlContent = """<?xml version="1.0"?>
        <Daemon>
            <ProcessID Value="1953175"/>
            <ParentProcessID Value="1"/>
            <ProcessGroupID Value="1953174"/>
        </Daemon>"""

        tempXML = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        tempXML.write(xmlContent.encode("utf-8"))
        tempXML.close()

        value = extractFromXML(tempXML.name, "ProcessID")
        self.assertEqual(value, "1953175")
        value = extractFromXML(tempXML.name, "NonExistingElement")
        self.assertIsNone(value)

        # remove tempXML
        os.unlink(tempXML.name)

if __name__ == '__main__':
    unittest.main()
