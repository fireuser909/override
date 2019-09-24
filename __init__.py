from types import FunctionType as function, MethodType as method

###---core---###
class override(object):
    """Use this decorator to assert this callable, classmethod, staticmethod,
    or property overrides an attribute of the same type as the decorated attrbute 
    of its first superclass that has it. 
    
    This decorator must be used inside a class which its metaclass is OverridesMeta
    or a subclass of it for the decorated attribute to be checked.
    
    Upon success, the class that this decorater was calledinside will set the
    decorated attribute's name to the  decorated attribute. If the assertion
    failed, the class will raise a subclass of OverrideError.
    
    Note: classmethods are treated like methods, staticmethods like functions
    
    For example usage, see testing at the end of this decorator's module.
    """
    __slots__ = "__func__", 
    
    def __new__(cls, func):
        self = object.__new__(cls)
        if not callable(func) and not isinstance(func, (classmethod, staticmethod, property)):
            raise ValueError("value of func parameter must be callable")
        self.__func__ = func
        return self
    
    def __eq__(self, other):
        return NotImplemented if not isinstance(other, override) else self.__func__ is other.__func__
    
    def __hash__(self):
        return hash((self.__func__,))
    
class OverrideError(AssertionError):
    "Callable, classmethod, staticmethod or property does not override"
    __slots__ = ()
    

class OverridesMeta(type):
    "Metaclass to support usage of the override decorator"
    def __new__(mcls, name, bases, classdict):
        cls = type.__new__(mcls, name, bases, classdict)
        for key, value in cls.__dict__.items():
            if isinstance(value, override):
                setattr(cls, key, value)
        return cls
                
    def __setattr__(cls, name, value):
        if isinstance(value, override):
            for b in cls.__bases__:
                if hasattr(b, name):
                    overriden = getattr(b, name)
                    break
            else:
                raise OverrideError("no base of %s has attr %s" % (cls.__name__, repr(name)))
            
            kind = function if isinstance(value.__func__, staticmethod) else (
                   method if isinstance(value.__func__, classmethod) else type(value.__func__)
                   )
            
            if type(overriden) is not kind:
                raise OverrideError("attempt to override a %s object with a %s object" % (
                    type(overriden).__name__, type(value.__func__).__name__
                ))
            value = value.__func__
        return super().__setattr__(name, value)
    
class OverridesBase(metaclass=OverridesMeta):
    "Mixin to allow usage of the override decorator"
    __slots__ = ()
    
###---support for custom metaclasses---###
def create_custom_overrides_meta(mcls, *, name=None, doc=None):
    metaclass = mcls
    
    class Meta(metaclass):
        def __new__(mcls, name, bases, classdict):
            cls = metaclass.__new__(mcls, name, bases, classdict)
            for key, value in cls.__dict__.items():
                if isinstance(value, override):
                    setattr(cls, key, value)
            return cls
        
        def __setattr__(cls, name, value):
            if isinstance(value, override):
                for b in cls.__bases__:
                    if hasattr(b, name):
                        overriden = getattr(b, name)
                        break
                else:
                    raise OverrideError("no base of %s has attr %s" % (cls.__name__, repr(name)))
                
                kind = function if isinstance(value.__func__, staticmethod) else (
                       method if isinstance(value.__func__, classmethod) else type(value.__func__)
                       )
                
                if type(overriden) is not kind:
                    raise OverrideError("attempt to override a %s object with a %s object" % (
                        type(overriden).__name__, type(value.__func__).__name__
                    ))
                value = value.__func__
            return metaclass.__setattr__(name, value)
        
    Meta.__name__ = name if name != None else "Overrides" + metaclass.__name__
    Meta.__doc__ = doc
    return Meta
        
    
__all__ = ['create_custom_overrides_meta', 'override', 'OverridesMeta', 'OverridesBase', 'OverrideError']
__author__ = "Michael Roberts: chermon3@gmail.com"
__credits__ = "Python 3.7 library
__date__ = "September 24 2019"
__doc__ = "Module to emulate Java's Override annotation in Python 3.7"
__version__ = 1.0

def main():
    class A(OverridesBase):
        def __init__(self, **kwds):
            "You're average constructor"
            self.__dict__.update(kwds)
            
        def b(mcls, self):
            "You're average method"
            pass
        
        def c(self):
            "You're average function"
            pass
        
        @classmethod
        def d(self):
            "You're average classmethod"
            pass
        
        @property
        def e(self):
            "You're average property"
            return None
             
    A.b = method(A.b, type)
    
    try:   
        class B(A):
            @override
            def b(self):
                print("b")
    except Exception as e:
        print(type(e).__name__, "raised while overriding method 'b' via class B:", e)
    
    try:       
        class C(A):
            @override
            def __init__(self, h=None, **kwds):
                super().__init__(**{'h':a, **kwds})
            @override
            def c(self):
                print("c")
    except Exception as e:
        print(type(e).__name__, "raised while overriding function 'c':", e)
        
    try:       
        class D(A):
            @override
            @classmethod
            def d(self):
                print("d")
    except Exception as e:
        print(type(e).__name__, "raised while overriding classmethod 'd':", e)
        
    try:       
        class E(A):
            @override
            @property
            def e(self):
                return "e"
    except Exception as e:
        print(type(e).__name__, "raised while overriding property 'e':", e)
        
    try:       
        class F(A):
            @override
            @classmethod
            def b(mcls, self):
                return "f"
    except Exception as e:
        print(type(e).__name__, "raised while overriding method 'b' via class F:", e)

if __name__ == "__main__":
    main()
