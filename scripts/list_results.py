import os
print('CWD:', os.getcwd())
p='results'
if os.path.isdir(p):
    for f in os.listdir(p):
        print(f)
else:
    print('results directory not found')
