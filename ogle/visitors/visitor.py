from ogle.ast.ast_node import NodeType


# Helper functions

def _qualname(obj):
    """Get the fully-qualified name of an object (including module)."""
    return obj.__module__ + '.' + obj.__qualname__

def _declaring_class(obj):
    """Get the name of the class that declared an object."""
    name = _qualname(obj)
    return name[:name.rfind('.')]


# Stores the mapping of different visitor methods to their implementation
# Each entry has the format of:
#   (declaring_class, node_type): function
_methods = {}

# Delegate visitor implementation
def _visitor_impl(self, node, scope=None):
    """Actual visitor method implementation."""
    method = _methods[(_qualname(type(self)), node.node_type)]
    if not method:
        method = _methods[(_qualname(type(self)), NodeType.GENERAL)]
    if not scope:
        scope = self.symbol_table.global_scope
    return method(self, node, scope)

# @visitor decorator
def visitor(node_type):
    def decorator(func):
        declaring_class = _declaring_class(func)
        _methods[(declaring_class, node_type)] = func
        # Replace all decorated methods with _visitor_impl
        return _visitor_impl

    return decorator
