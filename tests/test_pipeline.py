import json
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import main


class PipelineRulesTests(unittest.TestCase):
    def test_slots_are_2pm_and_8pm_eastern_during_daylight_time(self):
        now_et = main.US_TZ.localize(datetime(2026, 7, 15, 13, 0))

        slots = main.next_open_slots(already_today=0, now_et=now_et)

        self.assertEqual(
            [main.to_youtube_publish_at(slot) for slot in slots],
            ["2026-07-15T18:00:00Z", "2026-07-16T00:00:00Z"],
        )

    def test_slots_are_2pm_and_8pm_eastern_during_standard_time(self):
        now_et = main.US_TZ.localize(datetime(2026, 1, 15, 13, 0))

        slots = main.next_open_slots(already_today=0, now_et=now_et)

        self.assertEqual(
            [main.to_youtube_publish_at(slot) for slot in slots],
            ["2026-01-15T19:00:00Z", "2026-01-16T01:00:00Z"],
        )

    def test_late_run_uses_next_future_slot_and_never_exceeds_two(self):
        now_et = main.US_TZ.localize(datetime(2026, 1, 15, 16, 0))

        slots = main.next_open_slots(already_today=0, now_et=now_et)

        self.assertEqual(len(slots), 2)
        self.assertEqual(
            [slot.strftime("%Y-%m-%d %H:%M %Z") for slot in slots],
            ["2026-01-15 20:00 EST", "2026-01-16 14:00 EST"],
        )

    def test_topic_normalization_is_case_and_punctuation_insensitive(self):
        self.assertEqual(
            main.normalize_topic("How to Build Wealth: 3 Smart Ways!"),
            "build wealth 3 smart ways",
        )

    def test_gemini_score_below_90_marks_video_for_ignoring(self):
        response = Mock()
        response.text = json.dumps(
            {
                "source_text": "Save more each month",
                "topic": "monthly savings",
                "title": "A Better Monthly Savings Plan",
                "description": "Practical savings advice.",
                "tags": ["saving", "budget"],
                "score": 89,
                "reason": "The opening hook is unclear.",
                "skip": False,
            }
        )
        model = Mock()
        model.generate_content.return_value = response
        candidate = main.VideoCandidate(name="savings.mp4", source="local")

        with patch.object(main, "configure_gemini"), patch.object(
            main.genai, "GenerativeModel", return_value=model
        ):
            main.analyze_video_with_gemini(candidate, None, None)

        self.assertEqual(candidate.score, 89)
        self.assertTrue(candidate.skip)
        self.assertEqual(candidate.topic, "monthly savings")
        self.assertEqual(candidate.tags, ["saving", "budget"])

    def test_sheet_state_does_not_dedupe_dry_runs_or_failed_uploads(self):
        rows = [
            main.SHEET_HEADERS,
            ["", "dry.mp4", "drive-dry", "Dry topic", "", "", "Dry topic", "95", "DRY_RUN", "", "", ""],
            ["", "failed.mp4", "drive-failed", "Failed topic", "", "", "Failed topic", "95", "FAILED", "", "", ""],
            ["", "ready.mp4", "drive-ready", "Ready topic", "", "", "Ready topic", "95", "SCHEDULED", "2026-01-15 14:00 EST", "yt-id", ""],
        ]
        sheets = Mock()
        sheets.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "values": rows
        }

        file_keys, used_topics = main.load_sheet_state(sheets)

        self.assertEqual(file_keys, {"ready.mp4", "drive-ready", "ready topic"})
        self.assertEqual(used_topics, {"ready topic"})

    def test_sheet_log_keeps_the_12_defined_columns_in_order(self):
        candidate = main.VideoCandidate(
            name="budget.mp4",
            source="drive",
            drive_id="drive-id-1",
            title="Budget basics",
            description="A clear description",
            tags=["budgeting", "personal finance"],
            topic="budgeting basics",
            score=96,
        )

        with patch.object(main, "append_sheet_row") as append:
            main.log_row(None, candidate, "SCHEDULED", "2026-01-15 14:00 EST", "yt-id")

        row = append.call_args.args[1]
        self.assertEqual(len(row), len(main.SHEET_HEADERS))
        self.assertEqual(row[1:4], ["budget.mp4", "drive-id-1", "Budget basics"])
        self.assertEqual(row[6:10], ["budgeting basics", "96", "SCHEDULED", "2026-01-15 14:00 EST"])
        self.assertEqual(row[10], "yt-id")


if __name__ == "__main__":
    unittest.main()
