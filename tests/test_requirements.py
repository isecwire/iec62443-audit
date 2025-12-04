"""Tests for iec62443_audit.requirements module.

Validates that the IEC 62443-3-3 foundational requirements and system
requirements data is complete, well-formed, and free of duplicates.
"""

import re
import unittest

from iec62443_audit.requirements import (
    FOUNDATIONAL_REQUIREMENTS,
    FoundationalRequirement,
    SystemRequirement,
    get_all_requirements,
    get_fr_by_id,
    total_sr_count,
)


class TestFoundationalRequirementsDefined(unittest.TestCase):
    """All 7 FRs must be present."""

    def test_seven_frs_exist(self):
        frs = get_all_requirements()
        self.assertEqual(len(frs), 7)

    def test_fr_ids_are_fr1_through_fr7(self):
        fr_ids = [fr.id for fr in get_all_requirements()]
        self.assertEqual(fr_ids, [f"FR{i}" for i in range(1, 8)])

    def test_each_fr_has_required_fields(self):
        for fr in get_all_requirements():
            self.assertIsInstance(fr, FoundationalRequirement)
            self.assertTrue(fr.id, f"FR missing id")
            self.assertTrue(fr.name, f"{fr.id} missing name")
            self.assertTrue(fr.abbreviation, f"{fr.id} missing abbreviation")
            self.assertTrue(fr.description, f"{fr.id} missing description")

    def test_known_abbreviations(self):
        expected = {"IAC", "UC", "SI", "DC", "RDF", "TRE", "RA"}
        actual = {fr.abbreviation for fr in get_all_requirements()}
        self.assertEqual(actual, expected)


class TestSystemRequirements(unittest.TestCase):
    """Each FR has SRs; SRs are well-formed."""

    def test_each_fr_has_at_least_one_sr(self):
        for fr in get_all_requirements():
            self.assertGreater(
                len(fr.system_requirements),
                0,
                f"{fr.id} has no system requirements",
            )

    def test_sr_id_format(self):
        """SR IDs must match 'SR X.Y' where X is the FR number."""
        pattern = re.compile(r"^SR \d+\.\d+$")
        for fr in get_all_requirements():
            fr_num = fr.id.replace("FR", "")
            for sr in fr.system_requirements:
                self.assertRegex(
                    sr.id,
                    pattern,
                    f"SR id '{sr.id}' does not match expected format 'SR X.Y'",
                )
                sr_prefix = sr.id.split()[1].split(".")[0]
                self.assertEqual(
                    sr_prefix,
                    fr_num,
                    f"SR '{sr.id}' does not belong to {fr.id}",
                )

    def test_sl_capability_in_valid_range(self):
        for fr in get_all_requirements():
            for sr in fr.system_requirements:
                self.assertIn(
                    sr.sl_capability,
                    {1, 2, 3, 4},
                    f"{sr.id} has sl_capability={sr.sl_capability}, expected 1-4",
                )

    def test_no_duplicate_sr_ids(self):
        all_ids = []
        for fr in get_all_requirements():
            for sr in fr.system_requirements:
                all_ids.append(sr.id)
        self.assertEqual(len(all_ids), len(set(all_ids)), "Duplicate SR IDs found")

    def test_sr_has_name_and_description(self):
        for fr in get_all_requirements():
            for sr in fr.system_requirements:
                self.assertTrue(sr.name, f"{sr.id} missing name")
                self.assertTrue(sr.description, f"{sr.id} missing description")


class TestLookupHelpers(unittest.TestCase):
    """Tests for get_fr_by_id and total_sr_count."""

    def test_get_fr_by_id_found(self):
        fr = get_fr_by_id("FR1")
        self.assertIsNotNone(fr)
        self.assertEqual(fr.id, "FR1")

    def test_get_fr_by_id_not_found(self):
        self.assertIsNone(get_fr_by_id("FR99"))

    def test_total_sr_count_positive(self):
        count = total_sr_count()
        self.assertGreater(count, 0)

    def test_total_sr_count_matches_manual_count(self):
        manual = sum(len(fr.system_requirements) for fr in get_all_requirements())
        self.assertEqual(total_sr_count(), manual)


if __name__ == "__main__":
    unittest.main()
