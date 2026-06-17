import pytest
import tempfile
from pathlib import Path
from evaluation.golden_sample import GoldenSample, GoldenSampleManager


class TestGoldenSampleManager:
    @pytest.fixture
    def manager(self, tmp_path):
        return GoldenSampleManager(data_dir=tmp_path)

    def test_save_and_load(self, manager):
        sample = GoldenSample(
            id="test-001",
            query="What is 1+1?",
            expected_answer="2",
            domain="math",
        )
        manager.save([sample], "math")
        loaded = manager.load("math")
        assert len(loaded) == 1
        assert loaded[0].id == "test-001"
        assert loaded[0].query == "What is 1+1?"

    def test_add_deduplicates(self, manager):
        s1 = GoldenSample(id="s1", query="q1", expected_answer="a1", domain="d")
        s2 = GoldenSample(id="s1", query="q1-updated", expected_answer="a1-updated", domain="d")
        manager.add(s1)
        manager.add(s2)
        loaded = manager.load("d")
        assert len(loaded) == 1
        assert loaded[0].query == "q1-updated"

    def test_remove(self, manager):
        sample = GoldenSample(id="s1", query="q", expected_answer="a", domain="d")
        manager.add(sample)
        assert manager.remove("s1", "d") is True
        assert manager.load("d") == []

    def test_remove_nonexistent(self, manager):
        assert manager.remove("nope", "d") is False

    def test_list_domains(self, manager):
        manager.save([GoldenSample(id="1", query="q", expected_answer="a", domain="finance")], "finance")
        manager.save([GoldenSample(id="2", query="q", expected_answer="a", domain="qa")], "qa")
        domains = manager.list_domains()
        assert set(domains) == {"finance", "qa"}

    def test_count(self, manager):
        manager.save([
            GoldenSample(id="1", query="q", expected_answer="a", domain="d"),
            GoldenSample(id="2", query="q", expected_answer="a", domain="d"),
        ], "d")
        assert manager.count("d") == 2

    def test_load_all(self, manager):
        manager.save([GoldenSample(id="1", query="q", expected_answer="a", domain="d1")], "d1")
        manager.save([GoldenSample(id="2", query="q", expected_answer="a", domain="d2")], "d2")
        all_samples = manager.load_all()
        assert len(all_samples) == 2

    def test_load_nonexistent_domain(self, manager):
        assert manager.load("nonexistent") == []
