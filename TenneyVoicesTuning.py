# determine ideal guitar tuning for playing a given set of harmonics on a single fundamental 

import math

#returns a float which is the equal temperament, with the fractional part as cents and the integer part as the note 
def freqToMIDI(frequency):
	midi = frequency / 440.0
	midi = math.log(midi, 2) * 12 + 69
	
	return midi

def midiToString(midi):
	midi_rounded = int(round(midi))
	midi_cents = int(round((midi - midi_rounded) * 100))
	midi_notes = [ "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" ]

	octave = -1
	while(midi_rounded > 11):
		midi_rounded -= 12
		octave += 1
	while(midi_rounded < 0):
		midi_rounded += 12
		octave -= 1

	midi_note = midi_notes[midi_rounded % 12] + str(octave)
	if(midi_cents < 0):
		midi_note += "-" + str(abs(midi_cents))
	else:
		midi_note += "+" + str(midi_cents)

	return midi_note

def freqToMIDIString(frequency):
	midi = freqToMIDI(frequency)
	return midiToString(midi)


def midiToFreq(midi):
	midi -= 69
	midi /= 12.0
	midi = pow(2.0, midi)
	midi *= 440
	return midi

base_freq = 110.0
#print the first 24 partials
# for partial in range(1, 25):
# 	partial_freq = base_freq * partial
# 	midi_float = freqToMIDI(partial_freq)
# 	midi_str = midiToString(midi_float)

# 	print(str(partial)+" "+midi_str)

base_partials = [ 1, 3, 7, 5, 13, 9 ]
base_octaves =  [ 0, -1, -2, -1, -2, -1 ]
all_partials = []

for i in range(6):
	base_partial = base_partials[i]
	base_octave = base_octaves[i]
	base_partial_adjusted = base_partial * math.pow(2, base_octave)
	for harmonic in range(1, 13):
		harmonic_partial = base_partial_adjusted * harmonic
		if(harmonic_partial % 1.0 == 0.0):
			all_partials.append(harmonic_partial)
		#print("harmonic "+str(harmonic)+" "+str(harmonic_partial))

all_partials.sort()

#for part in all_partials:
	#print(str(part))

# todo 
# given: 
# a list of partials to be played 
# a fundamental frequency 
# a starting midi # for a string 
# a width in semitones for that string 
# 
# find: 
# the number of octave displacements of these partials that can fit in this range 

string_center_midis = [ 69-29, 69-24, 69-19, 69-14, 69-10, 69-5 ]
string_lower_midis = [ -5, -3, -3, -3, -3, -3 ]
string_upper_midis = [ 2, 2, 2, 2, 2, 1 ]
num_partials_per_string = [ 9, 9, 9, 7, 5, 4 ]

desired_partial_list = [ 8, 9, 10, 11, 12, 13, 14, 15 ]
fundamental_midi = 70-48

fundamental_freq = midiToFreq(fundamental_midi)

possible_partials = [ [], [], [], [], [], [] ]

for i in range(6):
	string_center_midi = string_center_midis[i]
	string_lower_midi = string_center_midi + string_lower_midis[i]
	string_upper_midi = string_center_midi + string_upper_midis[i]

	string_lower_freq = midiToFreq(string_lower_midi)
	string_upper_freq = midiToFreq(string_upper_midi)

	for partial in desired_partial_list:
		partial_freq = fundamental_freq * partial
		while(partial_freq < string_lower_freq):
			partial *= 2.0
			partial_freq = fundamental_freq * partial

		while(partial_freq > string_lower_freq):
			if(partial_freq < string_upper_freq):
				possible_partials[i].append(partial)
				break
			else:
				partial *= 0.5
				partial_freq = fundamental_freq * partial

	#print("STRING "+str(6-i))

	for partialo in possible_partials[i]:
		part_freq = fundamental_freq * partialo
		midi_str = midiToString(freqToMIDI(part_freq))
		#print(str(partialo) + " " + midi_str + " " + str(part_freq))

# generate a list of lists, where each list contains all partials that can be played by a given combination of strings 
# actually it should probably be some kind of tuple containing a list of the string notes, and then a list of the partials 
def generatePartialLists(string_num, possible_partials, num_partials_per_string, output_string_notes, output_partials, output_list):
	for string_note in possible_partials[string_num]:
		#make a copy of the string notes list and the output partials list 
		string_notes_cpy = list(output_string_notes)
		output_partials_cpy = list(output_partials)
		string_num_cpy = int(string_num)

		# add the current string note 
		string_notes_cpy.append(string_note)
		for scalar in range(num_partials_per_string[string_num_cpy]):
			new_partial = string_note * scalar
			if(new_partial % 1.0 == 0.0):
				output_partials_cpy.append(new_partial)
		
		# check if we should iterate down or return the lists 
		string_num_cpy += 1
		if(string_num_cpy < len(possible_partials)):
			generatePartialLists(string_num_cpy, possible_partials, num_partials_per_string, string_notes_cpy, output_partials_cpy, output_list)
		else:
			strings_partials_pair = []
			strings_partials_pair.append(string_notes_cpy)
			strings_partials_pair.append(output_partials_cpy)
			output_list.append(strings_partials_pair)

string_partials_list = []
osn = []
op = []

generatePartialLists(0, possible_partials, num_partials_per_string, osn, op, string_partials_list)

print("string partials list length "+str(len(string_partials_list)))

desired_partial_list_extended = [ 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 ]

high_score = -1
best_pairs = []

for pair in string_partials_list:
	strings = pair[0]
	partials = pair[1]
	partials.sort()

	temp_high_score = 0

	for desired_partial in desired_partial_list_extended:
		if desired_partial in partials:
			temp_high_score += 1

	if(temp_high_score == high_score):
		best_pairs.append(pair)

	if(temp_high_score > high_score):
		high_score = temp_high_score
		del best_pairs[:]
		best_pairs.append(pair)

	for string_no, string_note in enumerate(strings):
		#print("string "+str(6-string_no)+" "+str(string_note) + " " +freqToMIDIString(string_note * fundamental_freq) + " " +str(string_note * fundamental_freq))
		break

print("high score: "+str(high_score))
print("num of matching tunings: "+str(len(best_pairs)))
	
for pair in best_pairs:
	print("")
	strings = pair[0]
	for string_no, string_note in enumerate(strings):
		print("string "+str(6-string_no)+" "+str(string_note) + " " +freqToMIDIString(string_note * fundamental_freq) + " " +str(string_note * fundamental_freq))
		#break
	print("contains: ")
	for desired_partial in desired_partial_list_extended:
		if desired_partial in pair[1]:
			print(desired_partial)