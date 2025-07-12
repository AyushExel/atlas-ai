import unittest
from unittest.mock import patch

from atlas.utils.system import get_dynamic_batch_size


class SystemTest(unittest.TestCase):
    @patch("atlas.utils.system.get_available_memory")
    def test_get_dynamic_batch_size(self, mock_get_available_memory):
        # 1 GB of available memory
        mock_get_available_memory.return_value = 1 * 1024 * 1024 * 1024

        # 1 KB row size
        row_size = 1 * 1024
        batch_size = get_dynamic_batch_size(row_size)
        self.assertEqual(batch_size, int(1 * 1024 * 1024 * 1024 * 0.1 / 1024))

        # 1 MB row size
        row_size = 1 * 1024 * 1024
        batch_size = get_dynamic_batch_size(row_size)
        self.assertEqual(batch_size, int(1 * 1024 * 1024 * 1024 * 0.1 / (1024*1024)))

        # 0 row size (should return default)
        row_size = 0
        batch_size = get_dynamic_batch_size(row_size)
        self.assertEqual(batch_size, 1024)


if __name__ == "__main__":
    unittest.main()
