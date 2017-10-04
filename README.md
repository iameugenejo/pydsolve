pydsolve
========

Generic Dependency Resolver

### Install
``` bash
pip install dsolve
```

### Usage
#### Package Management
``` python
    from collections import OrderedDict
    
    class Package(object):
        def __init__(self, name, dependencies=None):
            self.name = name
            self.dependencies = dependencies
    
    
    class PackageResolver(object):
        def __init__(self, packages):
            self.execution_order = OrderedDict()
            self.resolver = dsolve.resolver()
            for package in packages:
                self.resolver.register(package.name, package, package.dependencies)
    
        def __resolve(self, resolving, dependent):
            order = self.execution_order.get(resolving.name)
            if not order:
                order = self.execution_order[resolving.name] = []
    
            order.append(dependent.name)
    
        def resolve(self):
            # register 3rd party packages
            for key in self.resolver.unregistered_nodes:
                self.resolver.register(key, Package(key))
    
            self.resolver.resolve(self.__resolve)
    
            return [(key, tuple(values)) for key, values in self.execution_order.items()]

    main_project = Package('main', dependencies=['whatever-project', 'awesome-project', 'that-project', 'great-project']) 
    packages = [
        main_project,
        Package('whatever-project', dependencies=['great-project', 'that-project']),
        Package('awesome-project', dependencies=['dsolve']),
        Package('that-project', dependencies=['great-project', 'flask']),
        Package('great-project', dependencies=['dsolve', 'flask']),
    ]
    
    resolved = PackageResolver(packages).resolve()
    
    print('# required for {}'.format(main_project.name))
    
    for name, resolved_for in resolved:
        print('pip install {}'.format(name))

```

##### OUTPUT

``` bash
# required for main

pip install dsolve
pip install flask
pip install awesome-project
pip install great-project
pip install that-project
pip install whatever-project
```
