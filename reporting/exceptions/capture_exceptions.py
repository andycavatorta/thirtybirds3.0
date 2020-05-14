#!/usr/bin/python
# -*- coding: ascii -*-

"""
This module contains decorator classes that augment target functions and/or all methods within target classes.

It is intended to reduce the time and effort needed to gather all uncaught exceptions in a large system and/or distributed system.

Both decorators collect all relevant context information at the site of the exception.
They collect the hostname, file path, the script name, the classname, the method name, the args and kwargs,
the exception type, the exception message, and the stack trace.  

All collected exception data is passed to a callback that is external to this module.
The callback can be set for all decorators by passing a reference to the callback method to this module's init() funciton.
Note that in multithreaded environments, the callback method must be thread safe.  

Check examples.py for usage.
"""

import functools
import inspect
import os
import socket 
import sys
import time
import traceback
from types import FunctionType
from types import BuiltinFunctionType

class Class:
    """
    This class is a class decorator that collects and reports uncaught exceptions in its target class. 
    It should be applied once at the top of the class.  It will find and wrap all methods within the class

    This decorator has been tested with instance methods.
    It has not yet been tested with class methods or static methods.

    Those will be added in a future version.
    """    
    callback = lambda msg: print(msg) # default, unset state
    def __init__(decorator_self,target_class):
        decorator_self.target_class = target_class

    def __call__(decorator_self, *args, **kwargs):
        target_instance_ref = decorator_self.target_class(*args, **kwargs)
        #print(inspect.getmembers(decorator_self.target_class, predicate=inspect.isfunction))
        target_instance_dir = dir(target_instance_ref)
        for attribute in target_instance_dir:
            if isinstance(getattr(decorator_self.target_class, attribute, ""), FunctionType):
                print("--->",attribute, getattr(target_instance_ref,attribute).__str__)
                func_name = attribute
                function_ref = getattr(target_instance_ref,attribute)
                #apply_wrapper is a separate method to break the reference to wrapper() on each cycle of this loop
                wrapper = decorator_self.apply_wrapper(function_ref, target_instance_ref, args, kwargs)
                setattr(target_instance_ref, func_name, wrapper)
        return target_instance_ref
    def apply_wrapper(decorator_self, function_ref, target_instance_ref, *args, **kwargs):
        @functools.wraps(function_ref)
        def wrapper(*args, **kwargs):
            self = target_instance_ref
            try:
                return function_ref(*args, **kwargs)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception_details = {
                    "time_epoch":time.time(),
                    "time_local":time.localtime(),
                    "hostname":socket.gethostname(),
                    "path":os.getcwd(),
                    "script_name":__file__,
                    "class_name":decorator_self.__class__.__name__,
                    "method_name":function_ref.__name__,
                    "args":args,
                    "kwargs":kwargs,
                    "exception_type":exc_type,
                    "exception_message":exc_value,
                    "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
                }
                decorator_self.callback(exception_details)
        return wrapper

class Function:
    """
    This class is a function decorator that collects and reports uncaught exceptions in its target function. 
    """    
    callback = lambda msg: print(msg) # default, unset state
    def __init__(decorator_self, func):
        functools.update_wrapper(decorator_self, func)
        decorator_self.func = func
    def __call__(decorator_self, *args, **kwargs):
        try:
            return decorator_self.func(*args, **kwargs)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exception_details = {
                "time_epoch":time.time(),
                "time_local":time.localtime(),
                "hostname":socket.gethostname(),
                "path":os.getcwd(),
                "script_name":__file__,
                "class_name":"",
                "method_name":decorator_self.func.__name__,
                "args":args,
                "kwargs":kwargs,
                "exception_type":exc_type,
                "exception_message":exc_value,
                "stacktrace":traceback.format_exception(exc_type, exc_value,exc_traceback)
            }
            decorator_self.callback(exception_details)

def init(callback):
    Class.callback = callback
    Function.callback = callback
