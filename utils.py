def divideBy(x):
    def numerator(y):
        return int(y / x)
    return numerator

def getPercent(y): 
  return divideBy(1000000000000000000)(y)

def multiplyBy(x):
  def input(y):
    return int(x + y)
  return input


def handleFloat(x):
  return multiplyBy(1e-18)(x)

def roundFloat(x):
  return round(float(handleFloat(x)), 2)


def rebase(prebase,digits):
    return prebase * (digits)



def writeFn(string): 
    return st.write(string)
def captionFn(string):
    return st.caption(string)
    
    
    
    
compose(writeFn('wrie stomething'), captionFn('somethim'),calcuationFn)

const calculateSomeValue = compose(writeFn('wrie stomething'), captionFn('somethim'),calcuationFn)

calculateSomeValue(2.7)