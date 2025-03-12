def assign_priority(count):
    
    if count >= high_threshold:
        return 'High'
    elif count >= low_threshold:
        return 'Medium'
    else:
        return 'Low'
