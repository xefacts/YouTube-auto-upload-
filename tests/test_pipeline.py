import contextlib
import json
import os
import tempfile
import unittest

# keep the mocked runs from emitting GitHub Actions annotations during CI tests
os.environ.setdefault("PIPELINE_QUIET_ANNOTATIONS", "1")
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import main


class FixedDatetime(datetime):
    """datetime.now(tz) is pinned to FIXED so slot selection is deterministic."""

    FIXED: datetime = datetime(2026, 7, 15, 13, 0)

    @classmethod
    def now(cls, tz=None):  # type: ignore[override]
        base = main.US_TZ.localize(cls.FIXED.replace(tzinfo=None))
        return base.astimezone(tz) if tz else base


class FakeRequest:
    def __init__(self, fn):
        self._fn = fn

    def execute(self):
        return self._fn()


class FakeValues:
    def __init__(self, rows):
        self.rows = rows
        self.appended = []
        self.header_written = None

    def get(self, spreadsheetId=None, range=None):
        if "A1:L1" in (range or ""):
            return FakeRequest(lambda: {"values": self.rows[:1]})
        return FakeRequest(lambda: {"values": self.rows})

    def update(self, **kwargs):
        def run():
            self.header_written = kwargs["body"]["values"][0]
            if not self.rows:
                self.rows.append(self.header_written)
            return {"values": kwargs["body"]["values"]}
        return FakeRequest(run)

    def append(self, **kwargs):
        def run():
            self.appended.append(kwargs["body"]["values"][0])
            self.rows.append(kwargs["body"]["values"][0])
            return {"updates": {}}
        return FakeRequest(run)


class FakeSpreadsheets:
    """Fake for sheets.spreadsheets(): supports .get() and .values()."""

    def __init__(self, values: "FakeValues"):
        self._values = values

    def get(self, spreadsheetId=None, fields=None):
        return FakeRequest(lambda: {
            "properties": {"title": "Test Sheet"},
            "sheets": [{"properties": {"title": "Sheet1"}}],
        })

    def values(self):
        return self._values


class FakeSheetsClient:
    def __init__(self, rows=None):
        self._values = FakeValues(list(rows if rows is not None else []))
        self._spreadsheets = FakeSpreadsheets(self._values)

    def spreadsheets(self):
        return self._spreadsheets

    def values(self):
        return self._values


def make_candidate(name="budget-tips.mp4", source="local", path=None, **kwargs):
    return main.VideoCandidate(name=name, source=source, path=path or (Path("videos") / name), **kwargs)


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

    def test_two_a_day_cap_holds_when_a_slot_is_already_booked(self):
        now_et = main.US_TZ.localize(datetime(2026, 7, 15, 9, 0))
        booked = {"2026-07-15 14"}

        slots = main.next_open_slots(already_today=1, now_et=now_et, booked_slots=booked)

        self.assertEqual(len(slots), 2)
        self.assertEqual(
            [slot.strftime("%Y-%m-%d %H:%M %Z") for slot in slots],
            ["2026-07-15 20:00 EDT", "2026-07-16 14:00 EDT"],
        )

    def test_full_day_moves_to_the_next_day(self):
        now_et = main.US_TZ.localize(datetime(2026, 7, 15, 9, 0))
        booked = {"2026-07-15 14", "2026-07-15 20"}

        slots = main.next_open_slots(already_today=2, now_et=now_et, booked_slots=booked)

        self.assertEqual(
            [slot.strftime("%Y-%m-%d %H:%M %Z") for slot in slots],
            ["2026-07-16 14:00 EDT", "2026-07-16 20:00 EDT"],
        )

    def test_topic_normalization_is_case_and_punctuation_insensitive(self):
        self.assertEqual(
            main.normalize_topic("How to Build Wealth: 3 Smart Ways!"),
            "build wealth 3 smart ways",
        )

    def test_slot_labels_are_parsed_even_when_sheets_coerced_them_to_dates(self):
        expected = main.US_TZ.localize(datetime(2026, 10, 11, 14, 0))
        for label in (
            "2026-10-11 14:00 EDT",
            "2026-10-11 14:00:00",
            "10/11/2026 14:00:00",
            "10/11/2026 14:00",
            "2026-10-11T18:00:00Z",
        ):
            with self.subTest(label=label):
                self.assertEqual(main.parse_slot_label(label), expected)

    def test_booked_slots_only_count_committed_rows(self):
        rows = [
            ["", "a.mp4", "", "", "", "", "t1", "95", "SCHEDULED", "2026-10-11 14:00 EDT", "yt", ""],
            ["", "b.mp4", "", "", "", "", "t2", "95", "DRY_RUN", "2026-10-11 20:00 EDT", "", ""],
            ["", "c.mp4", "", "", "", "", "t3", "95", "FAILED", "2026-10-12 14:00 EDT", "", ""],
            ["", "d.mp4", "", "", "", "", "t4", "95", "PUBLISHED", "2026-10-12 20:00 EDT", "yt", ""],
        ]

        self.assertEqual(
            main.booked_slot_keys(rows),
            {"2026-10-11 14", "2026-10-12 20"},
        )

    def test_gemini_score_below_90_marks_video_for_ignoring(self):
        client = Mock()
        client.generate.return_value = json.dumps(
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
        candidate = main.VideoCandidate(name="savings.mp4", source="local")

        main.analyze_video_with_gemini(candidate, None, None, client=client)

        self.assertEqual(candidate.score, 89)
        self.assertTrue(candidate.skip)
        self.assertEqual(candidate.topic, "monthly savings")
        self.assertEqual(candidate.tags, ["saving", "budget"])
        prompt = client.generate.call_args.args[0][0]["text"]
        self.assertIn("personal finance and business", prompt)
        self.assertIn("90", prompt)

    def test_gemini_analysis_attaches_first_frame_and_opening_audio(self):
        client = Mock()
        client.generate.return_value = json.dumps(
            {"topic": "index funds", "title": "T", "description": "D", "tags": [], "score": 95}
        )
        candidate = main.VideoCandidate(name="video.mp4", source="local")
        with tempfile.TemporaryDirectory() as tmp:
            frame = Path(tmp) / "frame.jpg"
            frame.write_bytes(b"\xff\xd8\xff\xe0frame")
            audio = Path(tmp) / "open.mp3"
            audio.write_bytes(b"ID3audio")

            main.analyze_video_with_gemini(candidate, frame, audio, client=client)

        parts = client.generate.call_args.args[0]
        self.assertTrue(parts[0]["text"].startswith("You are a senior YouTube SEO strategist"))
        self.assertEqual(parts[1]["inlineData"]["mimeType"], "image/jpeg")
        self.assertEqual(parts[2]["inlineData"]["mimeType"], "audio/mpeg")

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

    def test_ranking_keeps_topics_unique(self):
        a = make_candidate("a.mp4", topic="index funds", score=99)
        b = make_candidate("b.mp4", topic="Index Funds!", score=98)
        c = make_candidate("c.mp4", topic="budget planning", score=97)

        ordered = main.rank_sequence([a, b, c])

        self.assertEqual([item.name for item in ordered], ["a.mp4", "c.mp4", "b.mp4"])


class CredentialShapeTests(unittest.TestCase):
    def test_authorized_user_token_is_understood(self):
        fields = main.extract_token_fields(
            {"client_id": "cid", "client_secret": "csec", "refresh_token": "rtok"}
        )
        self.assertEqual(fields["client_id"], "cid")
        self.assertEqual(fields["refresh_token"], "rtok")
        self.assertTrue(main.token_diagnosis(fields, live=True)[0])

    def test_installed_client_secret_and_aliases_are_understood(self):
        payload = {"installed": {"client_id": "cid", "client_secret": "csec"}, "refreshToken": "rtok"}

        fields = main.extract_token_fields(payload)

        self.assertEqual(fields["client_id"], "cid")
        self.assertEqual(fields["client_secret"], "csec")
        self.assertEqual(fields["refresh_token"], "rtok")

    def test_client_secret_file_without_refresh_token_is_unusable_for_live_uploads(self):
        payload = {"installed": {"client_id": "cid", "client_secret": "csec"}}

        usable, message = main.token_diagnosis(payload, live=True)

        self.assertFalse(usable)
        self.assertIn("refresh_token", message)
        self.assertIn("client_id", message)  # only the field name is reported, never the value

    def test_access_token_only_token_is_accepted_with_warning(self):
        usable, message = main.token_diagnosis({"access_token": "ya29.abc"}, live=True)

        self.assertTrue(usable)
        self.assertIn("access_token", message)

    def test_split_secrets_satisfy_the_youtube_credentials(self):
        env = {
            "YOUTUBE_CLIENT_ID": "cid",
            "YOUTUBE_CLIENT_SECRET": "csec",
            "YOUTUBE_REFRESH_TOKEN": "rtok",
        }
        with patch.dict("os.environ", env, clear=False):
            usable, message = main.token_diagnosis(None, live=True)
            fields = main.extract_token_fields({})

        self.assertTrue(usable)
        self.assertIn("refresh_token", message)
        self.assertEqual(fields["client_id"], "cid")
        self.assertEqual(fields["refresh_token"], "rtok")

    def test_missing_token_is_fatal_only_for_live_runs(self):
        self.assertTrue(main.token_diagnosis(None, live=False)[0])
        self.assertFalse(main.token_diagnosis(None, live=True)[0])

    def test_key_paths_never_expose_values(self):
        paths = main.key_paths({"installed": {"client_secret": "super-secret-value"}})
        self.assertIn("installed.client_secret", paths)
        self.assertNotIn("super-secret-value", json.dumps(paths))

    def test_sanitize_redacts_secret_values(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSy-super-secret-key"}):
            text = main.sanitize("failed with key AIzaSy-super-secret-key")
        self.assertNotIn("AIzaSy-super-secret-key", text)
        self.assertIn("[REDACTED]", text)


class PipelineRunTests(unittest.TestCase):
    """End-to-end run() with the Google/YouTube edges mocked out."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.work = Path(self.tempdir.name) / "work"
        self.video = Path(self.tempdir.name) / "budget-tips.mp4"
        self.video.write_bytes(b"0" * 32)

    def _analyzed(self, candidate, frame=None, audio=None, client=None):
        candidate.topic = "monthly savings plan"
        candidate.title = "Monthly Savings Plan That Works"
        candidate.description = "Hook\n\nBody\n\n#money"
        candidate.tags = ["savings", "budget"]
        candidate.score = 95
        candidate.reason = "clear hook"
        return candidate

    def _run(self, sheets, *, dry_run, upload=None, rows_state=None):
        candidate = make_candidate(path=self.video)
        patches = [
            patch.object(main, "DRY_RUN", dry_run),
            patch.object(main, "WORK_DIR", self.work),
            patch.object(main, "datetime", FixedDatetime),
            patch.object(main, "load_service_account", return_value=(sheets, Mock())),
            patch.object(main, "ensure_sheet_headers"),
            patch.object(main, "list_drive_videos", return_value=[]),
            patch.object(main, "list_local_videos", return_value=[candidate]),
            patch.object(main, "materialize_file", return_value=self.video),
            patch.object(main, "extract_first_frame", return_value=None),
            patch.object(main, "extract_audio_clip", return_value=None),
            patch.object(main, "analyze_video_with_gemini", side_effect=self._analyzed),
            patch.object(main, "move_drive_to_processed", return_value=None),
            patch.object(main, "resolve_sheet_tab", return_value="Sheet1"),
            patch.object(main, "_SHEET_TAB_CACHE", "Sheet1"),
        ]
        if upload is not None:
            patches.append(patch.object(main, "upload_to_youtube", side_effect=upload))
        patches.append(patch.object(main, "load_youtube_client", return_value=None if dry_run else Mock()))
        with contextlib.ExitStack() as stack:
            for p in patches:
                stack.enter_context(p)
            return main.run(), sheets

    def test_dry_run_logs_slot_without_uploading(self):
        sheets = FakeSheetsClient([main.SHEET_HEADERS])

        status, sheets = self._run(sheets, dry_run=True)

        self.assertEqual(status, 0)
        self.assertEqual(len(sheets.values().appended), 1)
        row = sheets.values().appended[0]
        self.assertEqual(row[8], "DRY_RUN")
        self.assertEqual(row[9], "2026-07-15 14:00 EDT")
        self.assertEqual(row[10], "")
        self.assertEqual(row[7], "95")

    def test_live_run_uploads_once_and_logs_youtube_id(self):
        sheets = FakeSheetsClient([main.SHEET_HEADERS])
        upload = Mock(return_value="yt-123")

        status, sheets = self._run(sheets, dry_run=False, upload=upload)

        self.assertEqual(status, 0)
        upload.assert_called_once()
        rows = sheets.values().appended
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][8], "SCHEDULED")
        self.assertEqual(rows[0][10], "yt-123")

    def test_committed_slots_and_topics_block_duplicates_in_later_runs(self):
        existing = [main.SHEET_HEADERS]
        existing.append(
            ["", "old.mp4", "drive-1", "Old topic", "", "", "monthly savings plan", "95",
             "SCHEDULED", "2026-07-15 14:00 EDT", "yt-old", ""]
        )
        sheets = FakeSheetsClient(existing)

        status, sheets = self._run(sheets, dry_run=True)

        self.assertEqual(status, 0)
        # topic already used -> logged as duplicate, nothing scheduled
        self.assertEqual(sheets.values().appended[0][8], "DUPLICATE_TOPIC")

    def test_upload_failure_is_logged_and_fails_the_run(self):
        sheets = FakeSheetsClient([main.SHEET_HEADERS])
        upload = Mock(side_effect=RuntimeError("quota exceeded"))

        status, sheets = self._run(sheets, dry_run=False, upload=upload)

        self.assertEqual(status, 1)
        self.assertEqual(sheets.values().appended[0][8], "FAILED")

    def test_live_run_without_youtube_credentials_raises(self):
        sheets = FakeSheetsClient([main.SHEET_HEADERS])
        with patch.object(main, "DRY_RUN", False), \
             patch.object(main, "load_service_account", return_value=(sheets, Mock())), \
             patch.object(main, "resolve_sheet_tab", return_value="Sheet1"), \
             patch.object(main, "_SHEET_TAB_CACHE", "Sheet1"), \
             patch.object(main, "load_youtube_client", return_value=None):
            with self.assertRaises(RuntimeError):
                main.run()


class YouTubeClientTests(unittest.TestCase):
    def test_load_youtube_client_refreshes_with_a_request_instance(self):
        payload = {"client_id": "cid", "client_secret": "csec", "refresh_token": "rtok"}
        fake_creds = Mock()
        fake_creds.token = None
        fake_creds.expired = True
        fake_creds.refresh_token = "rtok"

        with patch.object(main, "read_youtube_token_payload", return_value=payload), \
             patch.object(main, "UserCredentials", return_value=fake_creds), \
             patch.object(main, "build") as build:
            client = main.load_youtube_client()

        refresh_args = fake_creds.refresh.call_args.args
        self.assertEqual(len(refresh_args), 1)
        self.assertIsInstance(refresh_args[0], main.Request)
        build.assert_called_once()
        self.assertIsNotNone(client)

    def test_load_youtube_client_refuses_unusable_token(self):
        payload = {"web": {"client_id": "cid", "client_secret": "csec"}}

        with patch.object(main, "read_youtube_token_payload", return_value=payload), \
             patch.object(main, "build"):
            with self.assertRaises(RuntimeError) as ctx:
                main.load_youtube_client()

        self.assertIn("refresh_token", str(ctx.exception))

    def test_doctor_refresh_uses_request_instance(self):
        payload = {"client_id": "cid", "client_secret": "csec", "refresh_token": "rtok"}
        fake_creds = Mock()
        fake_creds.token = None
        fake_creds.expired = True

        sheets, drive = Mock(), Mock()
        with patch.object(main, "read_youtube_token_payload", return_value=payload), \
             patch.object(main, "UserCredentials", return_value=fake_creds), \
             patch.object(main, "configure_gemini") as gemini, \
             patch.object(main, "_have_ffmpeg", return_value=True), \
             patch.object(main, "load_service_account", return_value=(sheets, drive)), \
             patch.object(main, "resolve_sheet_tab", return_value="Sheet1"), \
             patch.object(main, "_SHEET_TAB_CACHE", "Sheet1"), \
             patch.object(main, "retry_call", side_effect=lambda fn, **kw: fn()):
            gemini.return_value.resolve_model.return_value = "gemini-3.8-flash"
            gemini.return_value.generate.return_value = "OK"
            sheets.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
                "values": [main.SHEET_HEADERS]
            }
            drive.files.return_value.list.return_value.execute.return_value = {"files": []}
            drive.files.return_value.get.return_value.execute.return_value = {
                "id": "p", "name": "Processed", "capabilities": {"canAddChildren": True}
            }
            status = main.doctor()

        self.assertEqual(status, 0)
        self.assertIsInstance(fake_creds.refresh.call_args.args[0], main.Request)


class GeminiClientTests(unittest.TestCase):
    def test_generate_falls_back_to_the_next_model_when_one_is_overloaded(self):
        client = main.GeminiClient("test-key", model="gemini-3.8-flash")
        urls = []

        def fake_request(method, url, *, payload=None, label=""):
            urls.append(url)
            if "gemini-3.8-flash" in url:
                raise main.GeminiError(
                    "Gemini API error (503): This model is currently experiencing high demand."
                )
            return {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]}

        client._request = fake_request

        self.assertEqual(client.generate([{"text": "hi"}]), '{"ok": true}')
        self.assertEqual(len(urls), 2)
        self.assertIn("gemini-3.7-flash", urls[1])
        self.assertEqual(client.model, "gemini-3.7-flash")

    def test_generate_retries_without_json_mode_when_the_model_rejects_it(self):
        client = main.GeminiClient("test-key", model="gemini-3.8-flash")
        configs = []

        def fake_request(method, url, *, payload=None, label=""):
            configs.append(payload["generationConfig"])
            if "responseMimeType" in payload["generationConfig"]:
                raise main.GeminiError("Gemini API error (400): responseMimeType is not supported")
            return {"candidates": [{"content": {"parts": [{"text": "plain answer"}]}}]}

        client._request = fake_request

        self.assertEqual(client.generate([{"text": "hi"}]), "plain answer")
        self.assertNotIn("responseMimeType", configs[-1])

    def test_generate_reports_blocked_prompts(self):
        client = main.GeminiClient("test-key", model="gemini-3.8-flash")
        client._request = lambda *a, **k: {"promptFeedback": {"blockReason": "SAFETY"}}

        with self.assertRaises(main.GeminiError) as ctx:
            client.generate([{"text": "hi"}])

        self.assertIn("blockReason=SAFETY", str(ctx.exception))

    def test_retry_call_retries_transient_connection_errors(self):
        import requests

        attempts = {"n": 0}

        def flaky():
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise requests.ConnectionError("connection reset")
            return "done"

        with patch.object(main.time, "sleep"):
            self.assertEqual(main.retry_call(flaky, label="test retry"), "done")
        self.assertEqual(attempts["n"], 3)

    def test_retry_call_does_not_retry_permanent_errors(self):
        attempts = {"n": 0}

        def broken():
            attempts["n"] += 1
            raise ValueError("permanent")

        with self.assertRaises(ValueError):
            main.retry_call(broken, label="test permanent")
        self.assertEqual(attempts["n"], 1)


class UploadTests(unittest.TestCase):
    def test_upload_retries_transient_chunk_errors(self):
        class FakeResp:
            status = 503
            reason = "Service Unavailable"

        from googleapiclient.errors import HttpError

        error = HttpError(FakeResp(), b"backend error")
        request = Mock()
        request.next_chunk.side_effect = [error, (None, {"id": "yt-99"})]
        youtube = Mock()
        youtube.videos.return_value.insert.return_value = request
        candidate = make_candidate(title="T", description="D", tags=["a"])
        candidate.path = Path("videos") / "x.mp4"

        with patch.object(main, "MediaFileUpload"), patch.object(main.time, "sleep") as sleep:
            yt_id = main.upload_to_youtube(youtube, candidate.path, candidate, "2026-07-15T18:00:00Z")

        self.assertEqual(yt_id, "yt-99")
        sleep.assert_called_once()


if __name__ == "__main__":
    unittest.main()
