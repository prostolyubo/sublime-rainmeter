# import sys

# from unittest import TestCase

# program_path_provider = sys.modules["Rainmeter.path.program_path_provider"]


# class TestProgramPathProvider(TestCase):

#     def test_path_program_path_with_rainmeter_from_default_path(self):
#         """
#         If the user installed the application into the default directory
#         it is in "C:/Program Files/Rainmeter"
#         """
#         default_program_path = program_path_provider._get_rainmeter_path_from_default_path()

#         self.assertEqual(default_program_path, "C:\\Program Files\\Rainmeter")

# def test_get_rainmeter_registry_key(self):
#     """
#     test
#     """
#     key = program_path_provider._get_rainmeter_registry_key()

#     self.assertEqual(key, "test")

# def test_path_program_path_with_rainmeter_from_registry(self):
#     """
#     Upon normal installation it will leave a registry entry to detect.
#     We can use this to find the actual Rainmeter.
#     Since we use the default installation path, there should no difference
#     """
#     registry_program_path = program_path_provider._get_rainmeter_path_from_registry()

#     self.assertEqual(registry_program_path, "C:\\Program Files\\Rainmeter")

# def test_path_program_path_with_rainmeter_installed_return_drive(self):
#     """
#     Per default we install it onto "C:/Program Files/Rainmeter"
#     """
#     program_path = program_path_provider.get_cached_program_path()

#     self.assertEqual(program_path, "C:\\Program Files\\Rainmeter")
