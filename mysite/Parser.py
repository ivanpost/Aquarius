import inspect

class Parser:

    def __init__(self):
        pass

    @staticmethod
    def setVarClass(instance, name, cl):
        try:
            exec(f'instance.{name} = {cl}()', {}, {"instance": instance, "cl": cl})
            return True
        except:
            return False

    @staticmethod
    def setVarInClass(instance, name, value, cl=None):
        if not cl == None:
            if not Parser.setVarClass(instance, name, cl):
                return False
        try:
            exec(f'instance.{name} = val', {}, {"instance": instance, "val": value})
            return True
        except:
            return False

    @staticmethod
    def parse(data, target_class, variables, separator=","):
        d = data.split(separator)




