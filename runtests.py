import unittest

loader = unittest.TestLoader()
runner = unittest.TextTestRunner()

gptSuite = loader.discover('tests/YandexGPT')
dbSuite = loader.discover('tests/dataBase')
crmSuite = loader.discover('tests/crm')

print("Running GPT tests...")
runner.run(gptSuite)
print("Running GPT tests... Done")

print("Running DB tests...")
runner.run(dbSuite)
print("Running DB tests... Done")

print("Running CRM tests...")
runner.run(crmSuite)
print("Running CRM tests... Done")