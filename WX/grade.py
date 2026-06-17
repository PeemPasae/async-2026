import sys
def evaluate_grade(score):
    if score >= 80:
        return 'Excellent'
    elif 50 <= score < 80:
        return 'Pass'
    elif score < 50:
        return 'Fail'
    pass

def main():
    test_score = 80
    result = evaluate_grade(test_score)
    print(f"Score: {test_score} -> Grade: {result}")

if __name__ == "__main__":
    main()
