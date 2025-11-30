import functools
'''
This is just a basic decorator that logs when a function starts and when it ends
'''

# def logger(func):
#     @functools.wraps(func)
#     def wrapper_logger(*args, **kwargs):
#         print(f'Starting "{func.__name__}" function')
#         func(*args, **kwargs)
#         print(f'Finished "{func.__name__}" Finished')
#     return wrapper_logger


'''
I want to write a decorator that can take optional arguments
'''
# This decorator requires parameter to work correctly. Can i make the parameters optional?
def logger(_func=None, *, show_print=False):
    def decorator_logger(func):
        @functools.wraps(func)
        def wrapper_logger(*args, **kwargs):
            if show_print:
                print(f'Starting "{func.__name__}" function')
                func(*args, **kwargs)
                print(f'Finished "{func.__name__}" Finished')
            else:
                return func(*args, **kwargs)
        return wrapper_logger
    if _func is None: #called with parameters
        return decorator_logger
    return decorator_logger(_func) #logger called without parameters



@logger(show_print=True)
def call_name(name):
    print(f'Hello {name}')

call_name('kolade')