import util_.in_out as io
from util_.util import make_dir
from collections import defaultdict

def execute(in_dir, delim, out_file, age_gender=False, counts_med=False, 
				counts_med_enrich=False, counts_consult=False, counts_referral=False, 
				counts_lab=False, tmprl=False, enriched_tmprl=False):
	'''merge the in files to produce the out file'''
	merged = defaultdict(list)
	headers = ['ID']

	if age_gender:
		headers = merge_file(in_dir+'/AG.csv', merged, headers, delim)

	if counts_med:
		headers = merge_file(in_dir+'/C_M.csv', merged, headers, delim)

	if counts_med_enrich:
		headers = merge_file(in_dir+'/C_M_enrich.csv', merged, headers, delim)

	if counts_consult:
		headers = merge_file(in_dir+'/C_C.csv', merged, headers, delim)

	if counts_referral:
		headers = merge_file(in_dir+'/C_R.csv', merged, headers, delim)
	
	if counts_lab:
		headers = merge_file(in_dir+'/C_L.csv', merged, headers, delim)

	if tmprl:
		headers = merge_file(in_dir+'/tmprl.csv', merged, headers, delim)

	if enriched_tmprl:
		headers = merge_file(in_dir+'/tmprl_enriched.csv', merged, headers, delim)

	headers = merge_file(in_dir+'/CRC.csv', merged, headers, delim)
	
	# for f in in_files:
	# 	if not 'target' in f: # we do the target at the end
	# 		headers = merge_file(f, merged, headers)

	# # now the same for the target
	# for f in in_files:
	# 	if 'target' in f:
	# 		headers = merge_file(f, merged, headers)

	# now write to new file (also check whether all results have same length)
	make_dir(out_file)
	out = io.write_csv(out_file)

	out.writerow(headers)
	skip=0
	for key in merged:
		if len(headers) != 1+len(merged[key]):
			print 'unequal to header amount ({} vs {})! watch out.'.format(len(headers),len(merged[key]))
			# skip+=1
			# continue
		out.writerow([key] + merged[key])

	print '## Done Merging ##'

def merge_file(f, merged, headers, delim):
	try:
		rows = io.read_csv(f, delim)
	except:
		print '{} does not exist, choose a different directory or exclude the specified file from merging. Skipped for now.'.format(f)
		return headers

	headers = headers + rows.next()[1:]
	for row in rows:
		ID = int(row[0])
		merged[ID] = merged[ID] + row[1:]
	return headers
