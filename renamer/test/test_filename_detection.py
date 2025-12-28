#!/usr/bin/env python3
"""Test script for filename metadata detection with assertions"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from renamer.extractors.filename_extractor import FilenameExtractor

def test_detection():
    with open('renamer/test/test_cases.json', 'r') as f:
        test_cases = json.load(f)

    print("Testing filename metadata detection with assertions...\n")

    passed = 0
    failed = 0

    for i, case in enumerate(test_cases, 1):
        filename = case['filename']
        expected = case['expected']
        testname = case.get('testname', f'Test {i}')

        print(f"{testname}: {filename}")
        
        extractor = FilenameExtractor(filename)

        actual = {
            "order": extractor.extract_order(),
            "title": extractor.extract_title(),
            "year": extractor.extract_year(),
            "source": extractor.extract_source(),
            "frame_class": extractor.extract_frame_class(),
            "hdr": extractor.extract_hdr(),
            "movie_db": extractor.extract_movie_db(),
            "special_info": extractor.extract_special_info(),
            "audio_langs": extractor.extract_audio_langs()
        }

        # Check each field
        test_passed = True
        for key, exp_value in expected.items():
            act_value = actual[key]
            if act_value != exp_value:
                print(f"  ❌ {key}: expected {exp_value!r}, got {act_value!r}")
                test_passed = False
            else:
                print(f"  ✅ {key}: {act_value!r}")

        if test_passed:
            print("  ✅ PASSED\n")
            passed += 1
        else:
            print("  ❌ FAILED\n")
            failed += 1

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == '__main__':
    success = test_detection()
    sys.exit(0 if success else 1)