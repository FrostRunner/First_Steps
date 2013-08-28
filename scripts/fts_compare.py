import json
import sys

_propsIndex = 0
_childrenIndex = 1
_childrenProps = 'props'

_indexIndex = 0
_ftsTypeIndex = 1
_mapiTypeIndex = 2
_tagIndex = 3
_valueIndex = 4
_propIndexName = ["Index", "Fts type", "Mapi type", "Tag", "Value"]
_guidIndex = 4
_nameIndex = 5
_namedValueIndex = 6
_namedPropIndexName = _propIndexName[:-1] + ["Guid", "Name", "Value"]
_namedPropSize = 7

_absentLeftToRight = "AbsentLeftToRight"
_absentRightToLeft = "AbsentRightToLeft"
_propsDifferences = "PropsDifferences"
_movedProps = "MovedProps"
_childrenCount = "ChildrenCount"
_children = "Children"

def FindProp(data, propTag):
  for i in data:
    if i[_tagIndex] == propTag:
      return i
  return None

def FindAbsentProps(dataSource, dataDest):
  result = []
  for i in dataSource:
    prop = FindProp(dataDest, i[_tagIndex])
    if prop is None:
      result.append(i)
  return result

def FindDifferentProps(dataLeft, dataRight):
  result = []
  for i in dataLeft:
    prop = FindProp(dataRight, i[_tagIndex])
    if not prop is None:
      if i[_indexIndex+1:] != prop[_indexIndex+1:]:
        result.append([i, prop])
  return result

def FindMovedProps(dataLeft, dataRight):
  result = []
  indexLeft = 0
  indexRight = 0
  while indexLeft < len(dataLeft) and indexRight < len(dataRight):
    foundPropLeft = FindProp(dataLeft, dataRight[indexRight][_tagIndex])
    if foundPropLeft is None:
      indexRight += 1
      continue
    foundPropRight = FindProp(dataRight, dataLeft[indexLeft][_tagIndex])
    if foundPropRight is None:
      indexLeft += 1
      continue
    if foundPropRight[_indexIndex] == dataRight[indexRight][_indexIndex]:
      indexRight += 1
      indexLeft += 1
      continue
    rightToLeftDistance = foundPropLeft[_indexIndex] - dataLeft[indexLeft][_indexIndex]
    if rightToLeftDistance < 0:
      indexRight += 1
      continue
    leftToRightDistance = foundPropRight[_indexIndex] - dataRight[indexRight][_indexIndex]
    if leftToRightDistance < 0:
      indexLeft += 1
      continue
    if rightToLeftDistance <= leftToRightDistance:
      result.append([dataLeft[indexLeft], foundPropRight])
      indexLeft += 1
    else:
      result.append([foundPropLeft, dataRight[indexLeft]])
      indexRight += 1
  return result

def IsNamedProp(prop):
  return len(prop) == _namedPropSize

def FindDifferentPropIndexes(propLeft, propRight):
  indexes = []
  if not IsNamedProp(propLeft) and not IsNamedProp(propRight):
    indexes = [_ftsTypeIndex, _mapiTypeIndex, _valueIndex]
  if IsNamedProp(propLeft) and IsNamedProp(propRight):
    indexes = [_ftsTypeIndex, _mapiTypeIndex, _guidIndex, _nameIndex, _namedValueIndex]
  result = []
  for i in indexes:
    if type(propLeft[i]) != type(propRight[i]) or propLeft[i] != propRight[i]:
      result.append(i)
  return result

def PrintUsage():
  print('Usage: fts_compare leftFile rightFile\n')

def PrintPropertyNotFound(prop, fileLeft, fileRight):
  print("Property {0} from '{1}' not found in '{2}'".format(prop, fileLeft, fileRight))

def PrintPropertiesDifference(propLeft, propRight, propIndexes, fileLeft, fileRight):
  names = []
  if not IsNamedProp(propLeft) and not IsNamedProp(propRight):
    names = _propIndexName
  if IsNamedProp(propLeft) and IsNamedProp(propRight):
    names = _namedPropIndexName
  print("Property '{0}' from '{1}' differs from property '{2} from '{3}''".format(propLeft, fileLeft, propRight, fileRight))
  if len(names) > 0:
    for i in propIndexes:
      print("{0} '{1}' differs from '{2}'".format(names[i], propLeft[i], propRight[i]))
  else:
    print("Types of properties are different")

def PrintPropertyMoved(propLeft, propRight, fileLeft, fileRight):
  print("Property '{0}' from file '{1}' and property '{2}' from file '{3}' are in different places".format(propLeft, fileLeft, propRight, fileRight))

def PrintChildrenCountAreDifferent(lenLeft, lenRight):
  print("Children counts are different ({0} and {1})".format(lenLeft, lenRight))

def PrintSuccess():
  print("Success")

class UsageException(Exception):
  pass

class PropsComparer:
  def __init__(self, fileLeft, fileRight):
    self._FileLeft = fileLeft
    self._FileRight = fileRight
    (self._DataLeft, self._DataRight) = self._ReadData()

  def _ReadData(self):
    dataLeft = json.load(open(self._FileLeft))
    dataRight = json.load(open(self._FileRight))
    return (dataLeft, dataRight)

  def CompareProps(self):
    self._Result = self._CompareProps(self._DataLeft, self._DataRight)

  def GetResult(self):
    return self._Result

  def _CompareProps(self, dataLeft, dataRight):
    root = {}
    root[_absentLeftToRight] = FindAbsentProps(dataLeft[_propsIndex], dataRight[_propsIndex])
    root[_absentRightToLeft] = FindAbsentProps(dataRight[_propsIndex], dataLeft[_propsIndex])
    differences = []
    for i in FindDifferentProps(dataLeft[_propsIndex], dataRight[_propsIndex]):
      differences.append([i[0], i[1], FindDifferentPropIndexes(i[0], i[1])])
    root[_propsDifferences] = differences
    root[_movedProps] = FindMovedProps(dataLeft[_propsIndex], dataRight[_propsIndex])
    childrenCount = []
    if (len(dataLeft[_childrenIndex:]) != len(dataRight[_childrenIndex:])):
      childrenCount = [len(dataLeft[_childrenIndex:]), len(dataRight[_childrenIndex:])]
    root[_childrenCount] = childrenCount
    children = []
    root[_children] = []
    if len(dataLeft[_childrenIndex:]) > 0 or len(dataRight[_childrenIndex:]) > 0:
      if (len(dataLeft[_childrenIndex:]) == len(dataRight[_childrenIndex:])):
        for i in range(1, 1 + len(dataLeft[_childrenIndex:])):
          root[_children].append(self._CompareProps(dataLeft[i][_childrenProps], dataRight[i][_childrenProps]))
    return root, self._FileLeft, self._FileRight

  def PrintDifferences(self):
    self._PrintDifferences(self._Result)

  def _PrintDifferences(self, root):
    self._PrintCurrentLevel(root[_absentLeftToRight], root[_absentRightToLeft], root[_propsDifferences], root[_movedProps])
    if len(root[_childrenCount]) > 0:
      PrintChildrenCountAreDifferent(root[_childrenCount][0], root[_childrenCount][1])
    else:
      if len(root[_children]) > 0:
        self._PrintDifferences(root[_children])

  def _PrintCurrentLevel(self, resultLeftToRight, resultRightToLeft, resultDifferentPropIndexes, resultMovedProps):
    if not resultLeftToRight is None:
      for i in resultLeftToRight:
        PrintPropertyNotFound(i, self._FileLeft, self._FileRight)
    if not resultRightToLeft is None:
      for i in resultRightToLeft:
        PrintPropertyNotFound(i, self._FileRight, self._FileLeft)
    for i in resultDifferentPropIndexes:
      PrintPropertiesDifference(i[0], i[1], i[2], self._FileLeft, self._FileRight)
    for i in resultMovedProps:
      PrintPropertyMoved(i[0], i[1], self._FileLeft, self._FileRight)

def compare(left, right):
  comparer = PropsComparer(left, right)
  comparer.CompareProps()
  # result = comparer.GetResult()
  # import pdb; pdb.set_trace()
  return comparer.GetResult()
    
# def main(args):
    # compare(args[1], args[2])   
    
# if __name__ == "__main__":
    # main(sys.argv)
 

  
