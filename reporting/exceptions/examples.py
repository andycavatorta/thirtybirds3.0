#!/usr/bin/python

#############
# S E T U P #
#############

import capture_exceptions 

def callback_for_capture_exceptions(class_ref,exception_details):
    # in a real use case, this data could be passed to a parent script,
    # recorded in a log file, or sent over a network to another process.
    print("time_epoch:", exception_details["time_epoch"])
    print("time_local:", exception_details["time_local"])
    print("hostname:", exception_details["hostname"])
    print("path:", exception_details["path"])
    print("script_name:", exception_details["script_name"])
    print("class_name:", exception_details["class_name"])
    print("method_name:", exception_details["method_name"])
    print("args:", exception_details["args"])
    print("kwargs:", exception_details["kwargs"])
    print("exception_type:", exception_details["exception_type"])
    print("exception_message:", exception_details["exception_message"])
    print("stacktrace:", exception_details["stacktrace"])

capture_exceptions.init(callback_for_capture_exceptions)

################################
# S I M P L E  E X A M P L E S #
################################

@capture_exceptions.Class
class A:
    def a(self, s=0):
        print(self, s)
    def b(self, s=1):
        print(self, s)
        raise  ZeroDivisionError('Exception message is here')

a = A()

a.a()
a.b("fdsa")   

@capture_exceptions.Function
def c(value):
    print(bad_var_name)

c("asdf")

###############
# O U T P U T #
###############

"""
<__main__.A object at 0x7f579dd9f590> 0
<__main__.A object at 0x7f579dd9f590> fdsa
hostname: FERAL
path: /home/andy/Dropbox/projects/current/roboteq
script_name: /home/andy/Dropbox/projects/current/roboteq/capture_exceptions.py
class_name: Class
method_name: b
args: ('fdsa',)
kwargs: {}
exception_type: <class 'ZeroDivisionError'>
exception_message: Exception message is here
stacktrace: ['Traceback (most recent call last):\n', '  File "/home/andy/Dropbox/projects/current/roboteq/capture_exceptions.py", line 57, in wrapper\n    return function_ref(*args, **kwargs)\n', '  File "usage_examples.py", line 28, in b\n    raise  ZeroDivisionError(\'Exception message is here\')\n', 'ZeroDivisionError: Exception message is here\n']
hostname: FERAL
path: /home/andy/Dropbox/projects/current/roboteq
script_name: /home/andy/Dropbox/projects/current/roboteq/capture_exceptions.py
class_name: 
method_name: c
args: ('asdf',)
kwargs: {}
exception_type: <class 'NameError'>
exception_message: name 'bad_var_name' is not defined
stacktrace: ['Traceback (most recent call last):\n', '  File "/home/andy/Dropbox/projects/current/roboteq/capture_exceptions.py", line 85, in __call__\n    return decorator_self.func(*args, **kwargs)\n', '  File "usage_examples.py", line 37, in c\n    print(bad_var_name)\n', "NameError: name 'bad_var_name' is not defined\n"]
"""