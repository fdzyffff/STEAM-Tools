class my_class1():
    a = 0
    def seta(self,a_in):
        self.a = a_in
    def my_add(self,b):
        return b+1
    def printa(self):
        for i in range(10):
            self.a=self.my_add(self.a)
            print self.a


c1 = my_class1()
print c1.a
c1.seta(10)
print c1.a
c1.printa()
