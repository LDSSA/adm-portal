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

    FINAL_STATUS = [ACCEPTED, REJECTED, NOT_SELECTED]
