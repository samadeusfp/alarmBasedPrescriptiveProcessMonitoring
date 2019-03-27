c_miss_weight = 5
c_action_weight = 1
c_com_weight = 2
nonmonotonic_threshold = 18
max_nonmonotonic_threshold = 12



c_miss = c_miss_weight / (c_miss_weight + c_action_weight + c_com_weight)
c_action = c_action_weight / (c_miss_weight + c_action_weight + c_com_weight)
c_com = c_com_weight / (c_miss_weight + c_action_weight + c_com_weight)

case_length = 30
prefix_nr = 14

false_positive = (c_action * (1 - min(prefix_nr, nonmonotonic_threshold) / case_length)) + (c_com * (1 - prefix_nr / case_length))
print("False positive")
print(str(false_positive))
print("First part False positive:")
first_fp = (c_action * (1 - min(prefix_nr, nonmonotonic_threshold) / case_length))
print(str(first_fp))
print("True positive")
true_positive = (c_action * (1 - min(prefix_nr, nonmonotonic_threshold) / case_length)) + (max((prefix_nr - 1) / case_length, min(max_nonmonotonic_threshold/case_length,1)) * c_miss)
print(str(true_positive))