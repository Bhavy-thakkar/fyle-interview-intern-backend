import random
from sqlalchemy import text

from core import db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

def create_n_graded_assignments_for_teacher(number: int = 0, teacher_id: int = 1, grade_to_use=GradeEnum.A) -> int:
    """
    Creates 'n' graded assignments for a specified teacher and returns the count of assignments with grade 'A'.

    Parameters:
    - number (int): The number of assignments to be created.
    - teacher_id (int): The ID of the teacher for whom the assignments are created.
    - grade_to_use: GradeEnum, default is GradeEnum.A

    Returns:
    - int: Count of assignments with grade 'A'.
    """
    grade_a_counter = 0

    # Create 'n' graded assignments
    for _ in range(number):
        # Create a new Assignment instance
        assignment = Assignment(
            teacher_id=teacher_id,
            student_id=1,
            grade=grade_to_use,  # Use the provided grade, defaults to GradeEnum.A
            content='test content',
            state=AssignmentStateEnum.GRADED
        )

        # Add the assignment to the database session
        db.session.add(assignment)

        # Update the grade_a_counter if the grade is 'A'
        if grade_to_use == GradeEnum.A:
            grade_a_counter += 1

    # Commit changes to the database
    db.session.commit()

    # Return the count of assignments with grade 'A'
    return grade_a_counter


def test_get_assignments_in_graded_state_for_each_student():
    """Test to get graded assignments for each student"""

    # Find all the assignments for student 1 and change its state to 'GRADED'
    submitted_assignments: Assignment = Assignment.filter(Assignment.student_id == 1)

    # Iterate over each assignment and update its state
    for assignment in submitted_assignments:
        assignment.state = AssignmentStateEnum.GRADED  # Or any other desired state

    # Flush the changes to the database session
    db.session.flush()
    # Commit the changes to the database
    db.session.commit()

    # Define the expected result before any changes
    expected_result = [(1, 3)]

    # Execute the SQL query and compare the result with the expected result
    with open('tests/SQL/number_of_graded_assignments_for_each_student.sql', encoding='utf8') as fo:
        sql = fo.read()

    # Execute the SQL query compare the result with the expected result
    sql_result = db.session.execute(text(sql)).fetchall()
    for itr, result in enumerate(expected_result):
        assert result[0] == sql_result[itr][0]


def test_get_grade_A_assignments_for_teacher_with_max_grading():
    """Test to get count of grade A assignments for teacher who has graded the maximum assignments"""

    db.session.execute('DELETE FROM assignments')
    db.session.commit()

    # Read the SQL query from a file
    with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
        sql = fo.read()

    # Create and grade 5 assignments for teacher_id=1, all grade 'A'
    grade_a_count_1 = create_n_graded_assignments_for_teacher(5, 1, GradeEnum.A)

    # Check the number of assignments in the database
    assignments = db.session.execute('SELECT * FROM assignments').fetchall()

    # Execute the SQL query and check if the count matches the created assignments
    sql_result = db.session.execute(text(sql)).fetchall()
    assert grade_a_count_1 == sql_result[0][0], f"Expected {grade_a_count_1}, got {sql_result[0][0]}"
