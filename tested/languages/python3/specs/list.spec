__add__(self, value) -> list
  Return self+value.

__contains__(self, key) -> bool
  Return key in self.

__delattr__(self, name) -> None
  Implement delattr(self, name).

__delitem__(self, key) -> None
  Delete self[key].

__dir__() -> [str]
  __dir__() -> list
  default dir() implementation

__eq__(self, value) -> bool
  Return self==value.

__format__() -> str
  default object formatter

__ge__(self, value) -> bool
  Return self>=value.

__getattribute__(self, name) -> Unknown
  Return getattr(self, name).

__getitem__() -> Unknown
  x.__getitem__(y) <==> x[y]

__gt__(self, value) -> bool
  Return self>value.

__iadd__(self, value) -> list
  Implement self+=value.

__imul__(self, value) -> list
  Implement self*=value.

__init__(self) -> None
  Initialize self.  See help(type(self)) for accurate signature.

__iter__(self) -> Unknown
  Implement iter(self).

__le__(self, value) -> bool
  Return self<=value.

__len__(self) -> int
  Return len(self).

__lt__(self, value) -> bool
  Return self<value.

__mul__(self, value) -> list
  Return self*value.n

__ne__(self, value) -> bool
  Return self!=value.

__new__(type) -> list
  Create and return a new object.  See help(type) for accurate signature.

__reduce__() -> Unknown
  helper for pickle

__reduce_ex__() -> Unknown
  helper for pickle

__repr__(self) -> str
  Return repr(self).

__reversed__() -> Unknown
  L.__reversed__() -- return a reverse iterator over the list

__rmul__(self, value) -> list
  Return self*value.

__setattr__(self, name, value) -> None
  Implement setattr(self, name, value).

__setitem__(self, key, value) -> None
  Set self[key] to value.

__sizeof__() -> int
  L.__sizeof__() -- size of L in memory, in bytes

__str__(self) -> str
  Return str(self).

__subclasshook__() -> bool
  Abstract classes can override this to customize issubclass().
  
  This is invoked early on by abc.ABCMeta.__subclasscheck__().
  It should return True, False or NotImplemented.  If it returns
  NotImplemented, the normal algorithm is used.  Otherwise, it
  overrides the normal algorithm (and the outcome is cached).

append(object) -> None -- append object to end
  L.append(object) -> None -- append object to end

clear() -> None -- remove all items from L
  L.clear() -> None -- remove all items from L

copy() -> list -- a shallow copy of L
  L.copy() -> list -- a shallow copy of L

count(value) -> integer -- return number of occurrences of value
  L.count(value) -> integer -- return number of occurrences of value

extend(iterable) -> None -- extend list by appending elements from the iterable
  L.extend(iterable) -> None -- extend list by appending elements from the iterable

index(value, start, stop) -> integer -- return first index of value.
  L.index(value, [start, [stop]]) -> integer -- return first index of value.
  Raises ValueError if the value is not present.

insert() -> Unknown
  L.insert(index, object) -- insert object before index

pop(index) -> item -- remove and return item at index (default last).
  L.pop([index]) -> item -- remove and return item at index (default last).
  Raises IndexError if list is empty or index is out of range.

remove(value) -> None -- remove first occurrence of value.
  L.remove(value) -> None -- remove first occurrence of value.
  Raises ValueError if the value is not present.

reverse() -> Unknown
  L.reverse() -- reverse *IN PLACE*

sort(key, reverse) -> None -- stable sort *IN PLACE*
  L.sort(key=None, reverse=False) -> None -- stable sort *IN PLACE*

