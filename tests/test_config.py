import tempfile

from sms_circus.config import read_sender_configs


class TestReadSenderConfigs:
    def test_no_yaml_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = read_sender_configs(temp_dir)
            assert result == []

    def test_reads_configs(self):
        expected_name = "TestSender"
        expected_mean_processing_time = 1
        expected_failure_rate = 0.1

        with tempfile.TemporaryDirectory() as temp_dir:
            with open(f"{temp_dir}/test_config.yml", "w") as f:
                f.write(
                    f"name: {expected_name}\nmean_processing_time: {expected_mean_processing_time}\nfailure_rate: {expected_failure_rate}"
                )

            results = read_sender_configs(temp_dir)
            assert len(results) == 1

            result = results[0]
            assert result["name"] == expected_name
            assert result["mean_processing_time"] == expected_mean_processing_time
            assert result["failure_rate"] == expected_failure_rate
