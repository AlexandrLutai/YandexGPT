import unittest

loader = unittest.TestLoader()

suite = loader.discover('tests/YandexGPT')

runner = unittest.TextTestRunner()
runner.run(suite)