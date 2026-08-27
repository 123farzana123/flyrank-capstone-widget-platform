from ..repositories.submission_repository import SubmissionRepository
from ..models.submission import Submission, SubmissionCreate


class SubmissionService:

    def __init__(self, repository: SubmissionRepository):
        self.repository = repository

    def create_submission(self, widget_id: str, data: dict, ip_address: str = None,
                        country: str = None, city: str = None) -> Submission:
        #  call repository, wrap result in Submission(**...)
        result = self.repository.create_submission(widget_id, data, ip_address, country, city)
        return Submission(**result)

    def list_submissions(self, widget_id: str, owner_id: str) -> list[Submission]:
        # call repository, wrap each dict in a list comprehension 
        return [Submission(**sub) for sub in self.repository.list_submissions(widget_id, owner_id)]
        