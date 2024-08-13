from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt

def combine_series(c1, c2):
    return c1*c2/(c1+c2)

def combine_parallel(c1, c2):
    return c1 + c2

capacitors = [.1, .1, .33, .33, 1, 1, 2.2, 2.2, 4.7, 4.7] #old 0603 capacitors
capacitors = [.047,.047,.047,.047,.047,
              .082,.082,.082,.082,.082,
              .1,.1,.1,.1,.1,
              .22,.22,.22,.22,
              .33,.33,.33,.33,.33,
              1,1,1,1,1,
              1.8,1.8,1.8,1.8,1.8,
              3.3,3.3,3.3,3.3,3.3,
              4.7,4.7,4.7,4.7,4.7] #new 0805 caps
depth = 4 

def parallel_series_perms(total_length,current_length = 0, data = []):
    if total_length == current_length:
        return data
    else:
        return parallel_series_perms(total_length,current_length+1,data+[0]) + parallel_series_perms(total_length,current_length+1,data+[1])
def extract_numbers(input_string):
    # Characters that can be part of numbers
    number_chars = set('0123456789.')

    numbers = []
    current_number = ''

    for char in input_string:
        if char in number_chars:
            current_number += char
        else:
            if current_number:
                # Check if current_number is valid and add to numbers list
                if current_number.count('.') <= 1 and current_number.count('-') <= 1 and (current_number[1:].find('-') == -1):
                    try:
                        numbers.append(float(current_number))
                    except ValueError:
                        pass
                current_number = ''

    # Check the last number in the string
    if current_number:
        if current_number.count('.') <= 1 and current_number.count('-') <= 1 and (current_number[1:].find('-') == -1):
            try:
                numbers.append(float(current_number))
            except ValueError:
                pass
    return numbers

def only_series(st):
    for s in st:
        if s == '|':
            return False
    return True

caps = {}
for c in capacitors:
    caps[c] = str(c)
for i in range(2, min(depth,len(capacitors))+1):
    
    p_s_perms = parallel_series_perms(i-1)#this pretty much works, but i needed to reformat the output
    perms = []#perms is the desired output in the correct format
    for j in range(len(p_s_perms)//(i-1)):#this iterates through the total number of lists that will be in the output
        perms.append([])
        for k in range(i-1):# this adds each entry to the sub list inside of perms
            perms[j].append(p_s_perms[(i-1)*j+k])

    for j in combinations(capacitors,i):#through all the combos
        for k in range(len(perms)):#all the different permutations of parallel ans series
            for l in range(len(perms[k])):
                if l == 0:
                    if perms[k][l]:
                        c_new = combine_series(j[l],j[l+1])
                    else:
                        c_new = combine_parallel(j[l],j[l+1])
                else:
                    if perms[k][l]:
                        c_new = combine_series(c_new,j[l+1])
                    else:
                        c_new = combine_parallel(c_new,j[l+1])
            # print(j,perms[k],c_new)
            # input()
            if c_new in caps:
                caps[c_new] += ',\t'+'('*(len(j)-1)+str(j[0])
            else:
                caps[c_new] = '('*(len(j)-1)+str(j[0])
            for l in range(len(perms[k])):
                if perms[k][l]:
                    caps[c_new] += '--' + str(j[l+1]) + ')'
                else:
                    caps[c_new] += '||' + str(j[l+1]) + ')'
for c in caps:
    combos = caps[c].split(',\t')
    combos = set(combos)
    s = ''
    for combo in combos:
        if s == '':
            s = combo
        else:
            s += ',\n' + combo
    caps[c] = s

#sort caps
sorted_keys = sorted(caps.keys())
caps = {key: caps[key] for key in sorted_keys}
nums  = {}
for c in caps:
    
    
    
    entries = caps[c].split(',\n')
    # print(entries)
    ent_nums = []
    for entry in entries:
        ent_nums.append(len(extract_numbers(entry)))
    nums[c] = min(ent_nums)


    #display cap reciepes here
    if c>=0.04 and c<=0.05 and nums[c]==4:
        if only_series(caps[c]):
            print(c, caps[c])



#Visualize how well distributed the capacitance values are

# cap_values = np.array(list(caps.keys()))
# # cap_values = cap_values[0]
# # print(cap_values)
# cap_spacing = (cap_values[1:]-cap_values[:-1])/(cap_values[1:]+cap_values[:-1])*2
# print(np.average(cap_spacing))
# fig4 = plt.figure(constrained_layout = True)
# ax1 = fig4.add_subplot(1, 1, 1)
# ax1.scatter(cap_values[:-1],cap_spacing,s=2)
# ax1.set_yscale('log')
# ax1.set_xscale('log')


fig1 = plt.figure(constrained_layout = True)
ax = fig1.add_subplot(1, 1, 1)
ax.scatter(nums.values(),caps.keys())
ax.set_xlabel('Required Capacitors')
ax.set_ylabel('Capacitance Value (nF)')
ax.set_ylim(min(caps.keys()),.1)
# ax.set_ylim(0.07,.08)
ax.set_yscale('log')

plt.show()