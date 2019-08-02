import string
def toBase62(num, base=62):
	if base <= 0 or base > 62:
		return 0
	baseStr = string.digits + string.ascii_lowercase + string.ascii_uppercase
	r = num % base
	res = baseStr[r]
	q = num // base
	while q:
		r = q % base
		q = q // base
		res = baseStr[r] + res
	return res

def toBase10(num, base=62):
	baseStr = string.digits + string.ascii_lowercase + string.ascii_uppercase
	limit = len(num)
	res = 0
	for i in range(limit):
		res = base * res + baseStr.find(num[i])
	return res
