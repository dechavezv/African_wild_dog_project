"""
Usage:
python Sliding_window_Coverage_for_HKA_test.py filtered.vcf.gz 100000 10000 chr01 10000000 11000000 > outfile.txt
"""

import sys
import pysam
import os
import gzip
import numpy
import itertools

try:
    import cPickle as pickle
except:
    import pickle
from decimal import *
getcontext().prec = 8

VCF = gzip.open(sys.argv[1], 'r')

if not os.path.exists("%s.tbi" % sys.argv[1]):
    pysam.tabix_index(sys.argv[1], preset="vcf")
parsevcf = pysam.Tabixfile(sys.argv[1])

samples=[]
for line in VCF:
    if line.startswith('##'):
        pass
    else:
	for i in line.split()[9:]: samples.append(i)
        break
nindiv=len(samples)

window_size = int(sys.argv[2])
step_size = int(sys.argv[3])
chromo = sys.argv[4]
chromo_size={'chr01':122678785,'chr02':85426708,'chr03':91889043,'chr04':88276631,'chr05':88915250,'chr06':77573801,'chr07':80974532,'chr08':74330416,'chr09':61074082,'chr10':69331447,'chr11':74389097,'chr12':72498081,'chr13':63241923,'chr14':60966679,'chr15':64190966,'chr16':59632846,'chr17':64289059,'chr18':55844845,'chr19':53741614,'chr20':58134056,'chr21':50858623,'chr22':61439934,'chr23':52294480,'chr24':47698779,'chr25':51628933,'chr26':38964690,'chr27':45876710,'chr28':41182112,'chr29':41845238,'chr30':40214260,'chr31':39895921,'chr32':38810281,'chr33':31377067,'chr34':42124431,'chr35':26524999,'chr36':30810995,'chr37':30902991,'chr38':23914537,'chrX':123869142}

# If a region is supplied, use those coordinates for start and end positions
# If no region is specified, start position is the first position in the VCF file, and end position is the length of the chromosome

if len(sys.argv)>5:
    start_pos = int(sys.argv[5])
    end_pos = int(sys.argv[6])
else:
    for line in VCF:
        if line[0] != '#':
            start_pos = int(line.strip().split()[1])
            end_pos = chromo_size[chromo]
            break

def checkmono(lst):
    return not lst or lst.count(lst[0]) == len(lst)

def fetch_and_calc(chromo,start_pos,end_pos):
        sites_present,sites_passing=0,0
	GT_All=[]
        for line in parsevcf.fetch(chromo,start_pos,end_pos):             
		line = line.split('\t')
                sites_present+=1
                if ('FAIL' in line[6]) or ('.' in line[-1]) or ('.' in line[-2]) or ('.' in line[-3]) or ('.' in line[-4]): continue
                sites_passing+=1
		line1=line[9]
		line1=line1.split(':')
		line2=line[10]
		line2=line2.split(':')
		line3=line[11]
		line3=line3.split(':')
		line4=line[12]
             	line4=line4.split(':')
		GT=((float(line1[2]) + float(line2[2]) + float(line3[2]) + float(line4[2]))/float(4))
		GT_All.append(GT)	
	value=float(numpy.sum(GT_All)/(sites_passing))
	print('%s\t%d\t%d\t%f\t%d' % (chromo,window_start,window_end,value,sites_passing))

# initialize window start and end coordinates
window_start = start_pos
window_end = start_pos+window_size-1

# calculate stats for window, change window start and end positions
while window_end <= end_pos:

    if window_end < end_pos:
        fetch_and_calc(chromo,window_start,window_end)

        window_start = window_start + step_size + window_size
        window_end = window_start + window_size - 1

    else:
	fetch_and_calc(chromo,window_start,window_end)
        break

else:
    window_end = end_pos
    fetch_and_calc(chromo,window_start,window_end)

VCF.close()
exit()
