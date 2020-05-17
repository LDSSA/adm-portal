from typing import NewType

SelectionStatusType = NewType("SelectionStatusType", str)


class SelectionStatus:
    PASSED_TEST = SelectionStatusType("Passed Test (Awaiting)")
    DRAWN = SelectionStatusType("Drawn")
    INTERVIEW = SelectionStatusType("Awaiting Interview")
    SELECTED = SelectionStatusType("Selected (Must Update Payment Proof)")
    TO_BE_ACCEPTED = SelectionStatusType("Awaiting for Payment Proof Review")
    ACCEPTED = SelectionStatusType("Accepted")
    REJECTED = SelectionStatusType("Rejected")
    NOT_SELECTED = SelectionStatusType("Not Selected")

    SELECTION_AWAITING_STATUS = [PASSED_TEST, DRAWN]
    SELECTION_POSITIVE_STATUS = [SELECTED, TO_BE_ACCEPTED, ACCEPTED, REJECTED]
    SELECTION_NEGATIVE_STATUS = [NOT_SELECTED]

    FINAL_STATUS = [ACCEPTED, REJECTED, NOT_SELECTED]
