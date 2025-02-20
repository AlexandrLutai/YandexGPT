import unittest

loader = unittest.TestLoader()
runner = unittest.TextTestRunner()

gptSuite = loader.discover('tests/YandexGPT')
crmSuite = loader.discover('tests/crm')

print("Running GPT tests...")
runner.run(gptSuite)
print("Running GPT tests... Done")

print("Running CRM tests...")
runner.run(crmSuite)
print("Running CRM tests... Done")