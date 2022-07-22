#  type: ignore
from behave import given, then, when  # pylint: disable=no-name-in-module


@given("we have behave installed")
def step_impl_0(_):
    pass


@when("we implement a test")
def step_impl_1(_):
    assert True is not False


@then("behave will test it for us")
def step_impl_2(context):
    assert context.failed is False
