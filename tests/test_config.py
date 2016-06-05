# #! ../env/bin/python
# # -*- coding: utf-8 -*-
# from app import create_app
#
#
# class TestConfig:
#
#     def test_dev_config(self):
#         """ Tests if the development config loads correctly """
#
#         app = create_app('app.settings.DevConfig')
#
#         assert app.config['DEBUG'] is True
#         assert app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql://localhost/36T"
#
#     def test_test_config(self):
#         """ Tests if the test config loads correctly """
#
#         app = create_app('app.settings.TestConfig')
#
#         assert app.config['DEBUG'] is True
#         assert app.config['SQLALCHEMY_ECHO'] is True
#
#     def test_prod_config(self):
#         """ Tests if the production config loads correctly """
#
#         app = create_app('app.settings.ProdConfig')
#
#         assert app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql://localhost/36T"